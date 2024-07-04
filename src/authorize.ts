import * as crypto from 'crypto';

export const verifySignature = (req: any, apiKey: string): boolean => {
  const signature = crypto
    .createHmac('sha256', apiKey)
    .update(req.body)
    .digest('hex');

  const trusted = Buffer.from(`sha256=${signature}`, 'ascii');
  const untrusted = Buffer.from(req.headers['X-Hub-Signature-256'], 'ascii');

  return crypto.timingSafeEqual(trusted, untrusted);
};
