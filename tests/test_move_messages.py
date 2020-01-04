import json
from unittest.mock import patch, MagicMock

import boto3
from moto import mock_sqs

from phoenix_letter.main import main
from tests.bootstrap import BaseTestCase


@mock_sqs
class MoveMessagesTestCase(BaseTestCase):

    def setUp(self):
        self.region = "us-east-1"

        self.access_key = "AWS_ACCESS_MOCKED_KEY"
        self.secret_key = "AWS_SECRET_MOCKED_KEY"

        self.args = list()

        self.args.append("--src")
        self.args.append("queue_a")

        self.args.append("--dst")
        self.args.append("queue_b")

        self.args.append("--aws-keys")

        self.args.append("--region")
        self.args.append(self.region)

        self.args.append("--empty-receive")
        self.args.append("2")

        self.sqs = boto3.client("sqs", region_name=self.region,
                                aws_access_key_id=self.access_key,
                                aws_secret_access_key=self.secret_key)

        self.sqs.create_queue(QueueName="queue_a")
        self.queue_a_url = self.sqs.get_queue_url(QueueName="queue_a")['QueueUrl']

        message = self.__create_message()

        self.sqs.send_message(QueueUrl=self.queue_a_url,
                              MessageBody=message['Body'],
                              MessageAttributes=message['MessageAttributes'])

        self.sqs.create_queue(QueueName="queue_b")
        self.queue_b_url = self.sqs.get_queue_url(QueueName="queue_b")['QueueUrl']

    def tearDown(self):
        self.sqs.purge_queue(QueueUrl=self.queue_a_url)
        self.sqs.purge_queue(QueueUrl=self.queue_b_url)

    @patch("phoenix_letter.main.getpass")
    def test_move_message_with_aws_key(self, mock_get_pass):
        mock_get_pass.side_effect = [self.access_key, self.secret_key] * 2

        with self.subTest("move_message_without_args"):
            with self.assertRaises(SystemExit) as cm:
                main([])

            self.assertEqual(cm.exception.code, 2)
        with self.subTest("move_message_empty"):
            main(self.args)

            self.assertEqual(mock_get_pass.call_count, 2)
            mock_get_pass.reset_mock()
        with self.subTest("move_message"):
            main(self.args)

            self.assertEquals(mock_get_pass.call_count, 2)

            dst_message = self.sqs.receive_message(QueueUrl=self.queue_b_url,
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
            mock_get_pass.reset_mock()

    @patch("phoenix_letter.main.getpass")
    def test_move_message_without_aws_key(self, mock_get_pass):
        self.args.remove("--aws-keys")

        with self.subTest("move_message_without_args"):
            with self.assertRaises(SystemExit) as cm:
                main([])

            self.assertEqual(cm.exception.code, 2)
        with self.subTest("move_message_empty"):
            main(self.args)

            mock_get_pass.assert_not_called()
            mock_get_pass.reset_mock()
        with self.subTest("move_message"):
            main(self.args)

            mock_get_pass.assert_not_called()

            dst_message = self.sqs.receive_message(QueueUrl=self.queue_b_url,
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
            mock_get_pass.reset_mock()

    def __create_message(self):
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
