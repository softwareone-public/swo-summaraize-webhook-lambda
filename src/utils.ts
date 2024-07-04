import { Octokit } from '@octokit/rest';
import { createAppAuth } from '@octokit/auth-app';
import {
  BatchGetSecretValueCommand,
  SecretsManagerClient,
  SecretValueEntry,
} from '@aws-sdk/client-secrets-manager';

const secretsManagerClient = new SecretsManagerClient({
  region: process.env.REGION,
} as any);

const convertSecretValuesResponseToJSON = (
  secretValues: SecretValueEntry[],
) => {
  return secretValues.reduce(
    (secretInfo: {}, currentValue: SecretValueEntry) => {
      try {
        const secretObj = JSON.parse(currentValue.SecretString!);
        Object.assign(secretInfo, secretObj);
      } catch (error) {
        console.error(
          `Error parsing SecretString for entry with ARN: ${currentValue.ARN}`,
        );
      }

      return secretInfo;
    },
    {},
  );
};

export const getApiKey = async () => {
  const secretsResponse = (await secretsManagerClient.send(
    new BatchGetSecretValueCommand({
      SecretIdList: [process.env.API_KEY!],
    }) as any,
  )) as any;

  const formattedSecretResponse = convertSecretValuesResponseToJSON(
    secretsResponse.SecretValues!,
  ) as { API_KEY: string };

  return formattedSecretResponse.API_KEY;
};

export const createOctoClient = async () => {
  const secretsResponse = (await secretsManagerClient.send(
    new BatchGetSecretValueCommand({
      SecretIdList: [
        process.env.GITHUB_PK!,
        process.env.GITHUB_APP_ID!,
        process.env.GITHUB_CLIENT_ID!,
        process.env.GITHUB_CLIENT_SECRET!,
        process.env.GITHUB_INSTALLATION_ID!,
      ],
    }) as any,
  )) as any;

  const formattedSecretsResponse = convertSecretValuesResponseToJSON(
    secretsResponse.SecretValues!,
  ) as {
    GITHUB_APP_ID: string;
    GITHUB_PK: string;
    GITHUB_CLIENT_ID: string;
    GITHUB_CLIENT_SECRET: string;
    GITHUB_INSTALLATION_ID: string;
  };

  return new Octokit({
    authStrategy: createAppAuth,
    auth: {
      appId: formattedSecretsResponse.GITHUB_APP_ID,
      privateKey: formattedSecretsResponse.GITHUB_PK.replaceAll('\\n', '\n'),
      clientId: formattedSecretsResponse.GITHUB_CLIENT_ID,
      clientSecret: formattedSecretsResponse.GITHUB_CLIENT_SECRET,
      installationId: formattedSecretsResponse.GITHUB_INSTALLATION_ID,
    },
  });
};

export const sanitizeGitDiff = (diffContent: string): string => {
  const lines = diffContent.split('\n');
  const sanitizedLines = lines.reduce(
    (acc: string[], line: string, index: number, arr: string[]) => {
      if (isEndOfFileNewLineRemoved(line, index, arr)) {
        return acc;
      }
      if (
        line.startsWith('@@') ||
        line.startsWith('+') ||
        line.startsWith('-')
      ) {
        return acc.concat(line);
      }

      return acc;
    },
    [],
  );

  return sanitizedLines.join('\n');
};

const isEndOfFileNewLineRemoved = (
  line: string,
  index: number,
  arr: string[],
) => {
  return (
    line.includes('\\ No newline at end of file') ||
    (index > 0 && arr[index - 1].includes('\\ No newline at end of file')) ||
    (index < arr.length - 1 &&
      arr[index + 1].includes('\\ No newline at end of file'))
  );
};
