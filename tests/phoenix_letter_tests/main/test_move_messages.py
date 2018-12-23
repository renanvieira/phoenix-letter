import json

import boto3
from moto import mock_sqs

from phoenix_letter.main import main
from phoenix_letter_tests.bootstrap import BaseTestCase


class MoveMessagesTestCase(BaseTestCase):

    def setUp(self):

        self.region = "us-east-1"
        self.access_key = "asdjaoisdj"
        self.secret_key = "ajshiuahfiauhduiahsd"

        self.args = list()

        self.args.append("--src")
        self.args.append("queue_a")

        self.args.append("--dst")
        self.args.append("queue_b")

        self.args.append("--access-key")
        self.args.append("access_key")

        self.args.append("--secret-key")
        self.args.append(self.secret_key)

        self.args.append("--region")
        self.args.append(self.region)

        self.args.append("--empty-receive")
        self.args.append("2")

    @mock_sqs
    def test_move_message_without_args(self):
        with self.assertRaises(SystemExit) as cm:
            main([])

        self.assertEqual(cm.exception.code, 2)

    @mock_sqs
    def test_move_message_empty(self):
        sqs = boto3.client("sqs", region_name=self.region,
                           aws_access_key_id=self.access_key,
                           aws_secret_access_key=self.secret_key)

        sqs.create_queue(QueueName="queue_a")
        sqs.create_queue(QueueName="queue_b")

        main(self.args)

    def create_message(self):
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

    @mock_sqs
    def test_move_message(self):
        sqs = boto3.client("sqs", region_name=self.region,
                           aws_access_key_id=self.access_key,
                           aws_secret_access_key=self.secret_key)

        sqs.create_queue(QueueName="queue_a")

        message = self.create_message()

        sqs.send_message(QueueUrl=sqs.get_queue_url(QueueName="queue_a")['QueueUrl'],
                         MessageBody=message['Body'],
                         MessageAttributes=message['MessageAttributes'])

        sqs.create_queue(QueueName="queue_b")

        main(self.args)

        dst_message = sqs.receive_message(QueueUrl=sqs.get_queue_url(QueueName="queue_b")['QueueUrl'],
                                          MessageAttributeNames=["All"],
                                          AttributeNames=['All'],
                                          MaxNumberOfMessages=10)

        self.assertIsNotNone(dst_message)
        self.assertIn("Messages", dst_message)
        self.assertTrue(len(dst_message["Messages"]) == 1)

        first_message = dst_message["Messages"][0]
        self.assertEqual(first_message["Body"], json.dumps(dict(test="This is a test")))

        msg_attributes = first_message["MessageAttributes"]
        self.assertIn("Attribute1", msg_attributes)
        self.assertIn("Attribute2", msg_attributes)

        self.assertEqual(msg_attributes["Attribute1"]["StringValue"], "Attribute Value")
        self.assertEqual(msg_attributes["Attribute1"]["DataType"], "String")

        self.assertEqual(msg_attributes["Attribute2"]["StringValue"], "Attribute 2 Value")
        self.assertEqual(msg_attributes["Attribute2"]["DataType"], "String")
