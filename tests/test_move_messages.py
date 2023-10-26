import json
from unittest.mock import patch

from moto import mock_sqs

from phoenix_letter.common.enums import ReasonStopEnum
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

        self.assertEqual(result, ReasonStopEnum.EMPTY_RECEIVED)

        self.assertEqual(mock_get_pass.call_count, 2)
        mock_get_pass.reset_mock()

    def test_move_message_with_aws_key(self, mock_get_pass):
        mock_get_pass.side_effect = [self.access_key, self.secret_key] * 2

        self.add_message(self.queue_a_url)

        result = main(self.args)

        self.assertEqual(result, ReasonStopEnum.EMPTY_RECEIVED)

        self.assertEqual(mock_get_pass.call_count, 2)

        dst_message = self.sqs.receive_message(
            QueueUrl=self.queue_b_url,
            MessageAttributeNames=["All"],
            AttributeNames=["All"],
            MaxNumberOfMessages=10,
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

        self.assertEqual(
            msg_attributes["Attribute2"]["StringValue"], "Attribute 2 Value"
        )
        self.assertEqual(msg_attributes["Attribute2"]["DataType"], "String")
        mock_get_pass.reset_mock()

    def test_move_message_without_message_attributes(self, mock_get_pass):
        mock_get_pass.side_effect = [self.access_key, self.secret_key] * 2

        self.add_message(self.queue_a_url, with_message_attributes=False)

        result = main(self.args)

        self.assertEqual(result, ReasonStopEnum.EMPTY_RECEIVED)

        self.assertEqual(mock_get_pass.call_count, 2)

        dst_message = self.sqs.receive_message(
            QueueUrl=self.queue_b_url,
            MessageAttributeNames=["All"],
            AttributeNames=["All"],
            MaxNumberOfMessages=10,
        )

        self.assertIsNotNone(dst_message)
        self.assertIn("Messages", dst_message)
        self.assertTrue(len(dst_message["Messages"]) == 1)

        first_message = dst_message["Messages"][0]
        self.assertEqual(first_message["Body"], json.dumps(dict(test="This is a test")))
        self.assertNotIn("MessageAttributes", dst_message)

        mock_get_pass.reset_mock()

    def test_move_message_with_custom_message_attributes(self, mock_get_pass):
        self.args.append("--message-attributes-values")
        self.args.append("Attribute1=Value%String")
        self.args.append("Attribute2=2%Number")

        mock_get_pass.side_effect = [self.access_key, self.secret_key] * 2

        self.add_message(self.queue_a_url, with_message_attributes=False)

        result = main(self.args)

        self.assertEqual(result, ReasonStopEnum.EMPTY_RECEIVED)

        self.assertEqual(mock_get_pass.call_count, 2)

        dst_message = self.sqs.receive_message(
            QueueUrl=self.queue_b_url,
            MessageAttributeNames=["All"],
            AttributeNames=["All"],
            MaxNumberOfMessages=10,
        )

        self.assertIsNotNone(dst_message)
        self.assertIn("Messages", dst_message)
        self.assertTrue(len(dst_message["Messages"]) == 1)

        first_message = dst_message["Messages"][0]
        self.assertEqual(first_message["Body"], json.dumps(dict(test="This is a test")))
        self.assertDictEqual(
            first_message["MessageAttributes"],
            { "Attribute1": { "DataType": "String", "StringValue": "Value" }, "Attribute2": { "DataType": "Number", "StringValue": "2" } }
        )

        mock_get_pass.reset_mock()
