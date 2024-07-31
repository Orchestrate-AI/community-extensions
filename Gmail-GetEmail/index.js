const { google } = require('googleapis');
const redis = require('redis');
const dotenv = require('dotenv');
const cheerio = require('cheerio');

dotenv.config();

const {
  WORKFLOW_INSTANCE_ID,
  WORKFLOW_EXTENSION_ID,
  REDIS_HOST_URL,
  REDIS_USERNAME,
  REDIS_PASSWORD,
  REDIS_CHANNEL_IN,
  REDIS_CHANNEL_OUT,
  REDIS_CHANNEL_READY
} = process.env;

const publisher = redis.createClient({
  url: REDIS_HOST_URL,
  username: REDIS_USERNAME,
  password: REDIS_PASSWORD,
});

const subscriber = redis.createClient({
  url: REDIS_HOST_URL,
  username: REDIS_USERNAME,
  password: REDIS_PASSWORD,
});

async function main() {
  await publisher.connect();
  await subscriber.connect();

  await publisher.publish(REDIS_CHANNEL_READY, '');

  await subscriber.subscribe(REDIS_CHANNEL_IN, async (message) => {
    try {
      const result = await processMessage(message);

      const output = {
        type: 'completed',
        workflowInstanceId: WORKFLOW_INSTANCE_ID,
        workflowExtensionId: WORKFLOW_EXTENSION_ID,
        output: result
      };
      await publisher.publish(REDIS_CHANNEL_OUT, JSON.stringify(output));
    } catch (error) {
      console.error('Error in processMessage:', error);
      const errorOutput = {
        type: 'failed',
        workflowInstanceId: WORKFLOW_INSTANCE_ID,
        workflowExtensionId: WORKFLOW_EXTENSION_ID,
        error: {
          message: error.message,
          stack: error.stack
        }
      };
      await publisher.publish(REDIS_CHANNEL_OUT, JSON.stringify(errorOutput));
    } finally {
      await subscriber.unsubscribe(REDIS_CHANNEL_IN);
      await subscriber.quit();
      await publisher.quit();
    }
  });
}

function stripHtmlAndStyles(html) {
  const $ = cheerio.load(html);

  // Remove all style attributes
  $('*').removeAttr('style');

  // Remove all <style> tags
  $('style').remove();

  // Get the body content
  const bodyContent = $('body').html();

  // If there's no body tag, just return the whole content
  return bodyContent || $.html();
}

async function processMessage(message) {
  const { inputs } = JSON.parse(message);
  
  const { messageId, emailAddress, accessToken } = inputs;

  if (!messageId || !emailAddress || !accessToken) {
    throw new Error('Missing required input: messageId, emailAddress, or accessToken');
  }

  // Create an OAuth2 client
  const oauth2Client = new google.auth.OAuth2();
  oauth2Client.setCredentials({ access_token: accessToken });

  // Create Gmail client
  const gmail = google.gmail({ version: 'v1', auth: oauth2Client });

  // Fetch the email content
  const response = await gmail.users.messages.get({
    userId: emailAddress,
    id: messageId,
    format: 'full'
  });

  const email = response.data;

  // Extract email content (plain text and HTML)
  const parts = email.payload.parts || [email.payload];
  let content = '';

  // First, try to find HTML content
  for (const part of parts) {
    if (part.mimeType === 'text/html' && part.body.data) {
      const htmlBody = Buffer.from(part.body.data, 'base64').toString('utf-8');
      content = stripHtmlAndStyles(htmlBody);
      break;
    }
  }

  // If no HTML content found, look for plain text
  if (!content) {
    for (const part of parts) {
      if (part.mimeType === 'text/plain' && part.body.data) {
        content = Buffer.from(part.body.data, 'base64').toString('utf-8');
        break;
      }
    }
  }

  // If still no content, check the body of the payload itself
  if (!content) {
    if (email.payload.mimeType === 'text/html' && email.payload.body.data) {
      const htmlBody = Buffer.from(email.payload.body.data, 'base64').toString('utf-8');
      content = stripHtmlAndStyles(htmlBody);
    } else if (email.payload.mimeType === 'text/plain' && email.payload.body.data) {
      content = Buffer.from(email.payload.body.data, 'base64').toString('utf-8');
    }
  }

  // Extract subject
  const subject = email.payload.headers.find(header => header.name.toLowerCase() === 'subject')?.value || 'No subject';

  // Extract sender
  const from = email.payload.headers.find(header => header.name.toLowerCase() === 'from')?.value || 'Unknown sender';

  return {
    messageId: email.id,
    threadId: email.threadId,
    subject,
    from,
    content,
    timestamp: new Date(parseInt(email.internalDate)).toISOString(),
  };
}

main().catch(console.error);