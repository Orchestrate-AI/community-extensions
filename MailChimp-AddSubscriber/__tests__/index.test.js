const axios = require('axios');
const redis = require('redis');

jest.mock('axios');
jest.mock('redis');

const mockPublish = jest.fn();
const mockSubscribe = jest.fn();
const mockUnsubscribe = jest.fn();
const mockQuit = jest.fn();

redis.createClient.mockReturnValue({
  connect: jest.fn(),
  publish: mockPublish,
  subscribe: mockSubscribe,
  unsubscribe: mockUnsubscribe,
  quit: mockQuit
});

process.env.WORKFLOW_INSTANCE_ID = 'test-instance';
process.env.WORKFLOW_EXTENSION_ID = 'test-extension';
process.env.MAILCHIMP_API_KEY = 'test-api-key';
process.env.MAILCHIMP_LIST_ID = 'test-list-id';
process.env.MAILCHIMP_SERVER_PREFIX = 'us1';

const { processMessage } = require('../index');

describe('MailChimp AddSubscriber Extension', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should add a subscriber successfully', async () => {
    const mockResponse = {
      data: { id: 'test-subscriber-id' }
    };
    axios.put.mockResolvedValue(mockResponse);

    const message = JSON.stringify({
      inputs: {
        email: 'test@example.com',
        firstName: 'John',
        lastName: 'Doe'
      }
    });

    const result = await processMessage(message);

    expect(result).toEqual({
      status: 'success',
      message: 'Subscriber added successfully',
      subscriberId: 'test-subscriber-id'
    });

    expect(axios.put).toHaveBeenCalledWith(
      expect.stringContaining('https://us1.api.mailchimp.com'),
      expect.objectContaining({
        email_address: 'test@example.com',
        status: 'subscribed',
        merge_fields: {
          firstName: 'John',
          lastName: 'Doe'
        }
      }),
      expect.any(Object)
    );
  });

  it('should throw an error if email is missing', async () => {
    const message = JSON.stringify({
      inputs: {
        firstName: 'John',
        lastName: 'Doe'
      }
    });

    await expect(processMessage(message)).rejects.toThrow('Email is required');
  });

  it('should throw an error if email is invalid', async () => {
    const message = JSON.stringify({
      inputs: {
        email: 'invalid-email',
        firstName: 'John',
        lastName: 'Doe'
      }
    });

    await expect(processMessage(message)).rejects.toThrow('Invalid email format');
  });

  it('should handle MailChimp API errors', async () => {
    axios.put.mockRejectedValue(new Error('MailChimp API error'));

    const message = JSON.stringify({
      inputs: {
        email: 'test@example.com',
        firstName: 'John',
        lastName: 'Doe'
      }
    });

    await expect(processMessage(message)).rejects.toThrow('Failed to add subscriber: MailChimp API error');
  });
});