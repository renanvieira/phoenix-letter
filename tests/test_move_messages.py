import json

import six

from phoenix_letter.common.enums import ReasonStopEnum

if six.PY2:
    from mock import patch
else:
    from unittest.mock import patch

import boto3
from moto import mock_sqs

from phoenix_letter.main import main
from tests.bootstrap import BaseTestCase


@mock_sqs
@patch("phoenix_letter.common.credentials.getpass")
class MoveMessagesTestCase(BaseTestCase):
    def setUp(self):
        super(MoveMessagesTestCase, self).setUp()

        self.args.append("--aws-keys")

    def tearDown(self):
        super(MoveMessagesTestCase, self).tearDown()

    def test_move_message_without_args(self, mock_get_pass):
        with self.assertRaises(SystemExit) as cm:
            main([])

        self.assertEqual(cm.exception.code, 2)

    def test_move_message_with_empty_queue(self, mock_get_pass):
        mock_get_pass.side_effect = [self.access_key, self.secret_key] * 2

        self._clean_queues([self.queue_a_url, self.queue_b_url])
        result = main(self.args)

        self.assertEquals(result, ReasonStopEnum.EMPTY_RECEIVED)

        self.assertEqual(mock_get_pass.call_count, 2)
        mock_get_pass.reset_mock()

    def test_move_message_with_aws_key(self, mock_get_pass):
        mock_get_pass.side_effect = [self.access_key, self.secret_key] * 2

        self.add_message(self.queue_a_url)

        result = main(self.args)

        self.assertEquals(result, ReasonStopEnum.EMPTY_RECEIVED)

        self.assertEquals(mock_get_pass.call_count, 2)

        dst_message = self.sqs.receive_message(
            QueueUrl=self.queue_b_url, MessageAttributeNames=["All"], AttributeNames=["All"], MaxNumberOfMessages=10,
        )

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
