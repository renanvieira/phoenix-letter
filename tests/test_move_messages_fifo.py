import json
from unittest.mock import patch

from moto import mock_sqs

from phoenix_letter.common.enums import ReasonStopEnum
from phoenix_letter.main import main
from tests.bootstrap import BaseTestCase


@mock_sqs
class MoveMessagesFIFOTestCase(BaseTestCase):
    def setUp(self):
        super(MoveMessagesFIFOTestCase, self).setUp()

        self.args_fifo.append("--aws-keys")

    def tearDown(self):
        super(MoveMessagesFIFOTestCase, self).tearDown()

    def test_move_message_without_args(self):
        with self.assertRaises(SystemExit) as cm:
            main([])

        self.assertEqual(cm.exception.code, 2)

    def test_move_message_without_group_id(self):
        with self.assertRaises(SystemExit) as cm:
            main(self.args_fifo)

        self.assertEqual(cm.exception.code, 2)

    @patch("phoenix_letter.common.credentials.getpass")
    def test_move_message_with_empty_queue(self, mock_get_pass):
        mock_get_pass.side_effect = [self.access_key, self.secret_key] * 2
        message_group_id = "test_move_message_with_aws_key"

        self.args_fifo.append(f"--group-id={message_group_id}")

        self._clean_queues([self.queue_a_fifo_url, self.queue_b_fifo_url])
        result = main(self.args_fifo)

        self.assertEqual(result, ReasonStopEnum.EMPTY_RECEIVED)

        self.assertEqual(mock_get_pass.call_count, 2)
        mock_get_pass.reset_mock()

    @patch("phoenix_letter.common.credentials.getpass")
    def test_move_message_with_aws_key(self, mock_get_pass):
        message_group_id = "test_move_message_with_aws_key"

        self.args_fifo.append(f"--group-id={message_group_id}")
        mock_get_pass.side_effect = [self.access_key, self.secret_key] * 2

        self.add_message(self.queue_a_fifo_url, message_group_id=message_group_id)

        result = main(self.args_fifo)

        self.assertEqual(result, ReasonStopEnum.EMPTY_RECEIVED)

        self.assertEqual(mock_get_pass.call_count, 2)

        dst_message = self.sqs.receive_message(
            QueueUrl=self.queue_b_fifo_url,
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

    @patch("phoenix_letter.common.credentials.getpass")
    def test_move_message_fifo_without_message_attributes(self, mock_get_pass):
        message_group_id = "test_move_message_fifo_without_message_attributes"

        self.args_fifo.append(f"--group-id={message_group_id}")
        mock_get_pass.side_effect = [self.access_key, self.secret_key] * 2

        self.add_message(
            self.queue_a_fifo_url,
            with_message_attributes=False,
            message_group_id=message_group_id,
        )

        result = main(self.args_fifo)

        self.assertEqual(result, ReasonStopEnum.EMPTY_RECEIVED)

        self.assertEqual(mock_get_pass.call_count, 2)

        dst_message = self.sqs.receive_message(
            QueueUrl=self.queue_b_fifo_url,
            MessageAttributeNames=["All"],
            AttributeNames=["All"],
            MaxNumberOfMessages=10,
        )

        self.assertIsNotNone(dst_message)
        self.assertIn("Messages", dst_message)
        self.assertTrue(len(dst_message["Messages"]) == 1)

        first_message = dst_message["Messages"][0]
        self.assertEqual(first_message["Body"], json.dumps(dict(test="This is a test")))
        self.assertNotIn("MessagAttributes", dst_message)

        mock_get_pass.reset_mock()
