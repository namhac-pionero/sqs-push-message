import boto3
import json
from botocore.exceptions import ClientError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQSMessageSender:
    def __init__(self, queue_url, region_name='us-east-1'):
        """
        Initialize the SQS sender with queue URL and region
        
        Args:
            queue_url (str): The URL of the SQS queue
            region_name (str): AWS region name (default: us-east-1)
        """
        self.queue_url = queue_url
        self.sqs = boto3.client('sqs', region_name=region_name)
    
    def send_message(self, message_body, message_attributes=None):
        """
        Send a message to the SQS queue
        
        Args:
            message_body (dict/str): The message to send
            message_attributes (dict): Optional message attributes
            
        Returns:
            dict: Response from SQS if successful, None if failed
        """
        try:
            # Convert dict to JSON string if message_body is a dictionary
            if isinstance(message_body, dict):
                message_body = json.dumps(message_body)
            
            # Prepare the send message parameters
            params = {
                'QueueUrl': self.queue_url,
                'MessageBody': message_body
            }
            
            # Add message attributes if provided
            if message_attributes:
                params['MessageAttributes'] = message_attributes
            
            # Send the message
            response = self.sqs.send_message(**params)
            
            logger.info(f"Message sent. MessageId: {response['MessageId']}")
            return response
            
        except ClientError as e:
            logger.error(f"Failed to send message: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None

