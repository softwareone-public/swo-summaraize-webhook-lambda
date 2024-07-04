import { createOctoClient, getApiKey, sanitizeGitDiff } from './utils';
import { verifySignature } from './authorize';
import {
  BedrockRuntimeClient,
  InvokeModelCommand,
} from '@aws-sdk/client-bedrock-runtime';

const prompt = `${process.env.PROMPT}`.replaceAll('\\n', '\n');

const bedrockClient = new BedrockRuntimeClient({
  region: process.env.REGION,
} as any);

let octokitClient;
let apiKey;

export const handler = async (event: any) => {
  if (!apiKey) {
    apiKey = await getApiKey();
  }

  const authorized = verifySignature(event, apiKey);

  if (!authorized) {
    return {
      statusCode: 403,
    };
  }

  const body = JSON.parse(event.body);

  if (body.action !== 'opened') {
    return {
      statusCode: 200,
    };
  }

  if (!octokitClient) {
    octokitClient = await createOctoClient();
  }

  const resp = await octokitClient.rest.pulls.get({
    owner: process.env.ORG_NAME!,
    repo: body.repository.name,
    pull_number: body.pull_request.number,
    mediaType: {
      format: 'diff',
    },
  });

  const diff = sanitizeGitDiff(resp.data);

  const command = new InvokeModelCommand({
    body: JSON.stringify({
      prompt: prompt.replace('{diff}', diff),
      max_tokens_to_sample: +process.env.MAX_TOKENS_TO_SAMPLE,
      temperature: +process.env.TEMPERATURE,
      top_k: +process.env.TOP_K,
      top_p: +process.env.TOP_P,
    }),
    contentType: 'application/json',
    accept: '*/*',
    modelId: 'anthropic.claude-v2',
  });

  //@ts-ignore
  const bedrockResp = (await bedrockClient.send(command)) as { body: string };

  const parsedResponse = JSON.parse(
    Buffer.from(bedrockResp.body).toString('utf8'),
  ) as { completion: string };

  let updatedBody = body.pull_request.body || '';
  if (updatedBody) {
    updatedBody = updatedBody + '\n\n';
  }
  updatedBody += `**[SummarAIzation]:** ${parsedResponse.completion}`;

  await octokitClient.rest.pulls.update({
    owner: process.env.ORG_NAME!,
    repo: body.repository.name,
    pull_number: body.pull_request.number,
    body: updatedBody,
  });

  return {
    statusCode: 200,
  };
};
