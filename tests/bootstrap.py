import json
import logging
import sys

import boto3
import six
from moto import mock_sqs

from phoenix_letter.main import main

if six.PY2:
    from unittest2 import TestCase
else:
    from unittest import TestCase

logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('nose').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout)

logger = logging.getLogger(__name__)


@mock_sqs
class BaseTestCase(TestCase):

    def setUp(self):
        self.region = "us-east-1"

        self.access_key = "AWS_ACCESS_MOCKED_KEY"
        self.secret_key = "AWS_SECRET_MOCKED_KEY"

        self.args = list()

        self.args.append("--src")
        self.args.append("queue_a")

        self.args.append("--dst")
        self.args.append("queue_b")

        self.args.append("--region")
        self.args.append(self.region)

        self.args.append("--empty-receive")
        self.args.append("2")

        self.sqs = boto3.client("sqs", region_name=self.region,
                                aws_access_key_id=self.access_key,
                                aws_secret_access_key=self.secret_key)

        self.sqs.create_queue(QueueName="queue_a")
        self.queue_a_url = self.sqs.get_queue_url(QueueName="queue_a")['QueueUrl']

        self.sqs.create_queue(QueueName="queue_b")
        self.queue_b_url = self.sqs.get_queue_url(QueueName="queue_b")['QueueUrl']

    def tearDown(self):
        self._clean_queues([self.queue_a_url, self.queue_b_url])
    
    def _create_message(self):
        message = dict()
        message["Body"] = json.dumps(dict(test="This is a test"))

        message_attr = {
            'Attribute1': {
                'StringValue': 'Attribute Value',
                'DataType': 'String'
            },
            'Attribute2': {
                'StringValue': 'Attribute 2 Value',
                'DataType': 'String'
            },
        }

        message["MessageAttributes"] = message_attr

        return message

    def add_message(self, queue_url):
        message = self._create_message()
        self.sqs.send_message(QueueUrl=queue_url,
                              MessageBody=message['Body'],
                              MessageAttributes=message['MessageAttributes'])

    def get_number_of_message(self, queue_url):
        attributes = self.sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['ApproximateNumberOfMessages'])

        return int(attributes['Attributes'].get("ApproximateNumberOfMessages"))

    def _clean_queues(self, queues):
        for q in queues:
            self.sqs.purge_queue(QueueUrl=q)
