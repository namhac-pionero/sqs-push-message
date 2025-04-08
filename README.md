# SQS Message Sender

This Python script provides functionality to send messages to an Amazon SQS (Simple Queue Service) queue.

## Prerequisites

1. AWS account with appropriate credentials
2. Python 3.6 or higher
3. Required Python packages (install using requirements.txt)

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Configure AWS credentials using one of these methods:

   - AWS CLI: `aws configure`
   - Environment variables:
     ```bash
     export AWS_ACCESS_KEY_ID='your_access_key'
     export AWS_SECRET_ACCESS_KEY='your_secret_key'
     export AWS_DEFAULT_REGION='your_region'
     ```
   - AWS credentials file (`~/.aws/credentials`)

3. Update the `queue_url` in `sqs_sender.py` with your SQS queue URL

## Usage

The script provides a `SQSMessageSender` class that can be used to send messages to an SQS queue.

### Basic usage:

```python
from sqs_sender import SQSMessageSender

# Initialize the sender
sender = SQSMessageSender("YOUR_QUEUE_URL")

# Send a simple message
message = {"key": "value"}
response = sender.send_message(message)
```

### Running the example:

```bash
python sqs_sender.py
```

## Features

- Send JSON messages to SQS queue
- Support for message attributes
- Error handling and logging
- Configurable AWS region

## Error Handling

The script includes comprehensive error handling and logging. All operations are logged using Python's built-in logging module.
