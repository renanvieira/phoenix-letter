import json
import logging
import sys
import six
from moto import mock_sqs

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
        self.sqs = None

    def tearDown(self):
        pass

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
