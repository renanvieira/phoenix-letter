import json
from unittest.mock import patch

from moto import mock_sqs

from phoenix_letter.common.enums import ReasonStopEnum
from phoenix_letter.main import main
from tests.bootstrap import BaseTestCase


@mock_sqs
class MoveMessagesWithoutAWSKeysTestCase(BaseTestCase):
    def setUp(self):
        super(MoveMessagesWithoutAWSKeysTestCase, self).setUp()

    def tearDown(self):
        super(MoveMessagesWithoutAWSKeysTestCase, self).tearDown()

    def test_move_message_without_args(self):
        with self.assertRaises(SystemExit) as cm:
            main([])

        self.assertEqual(cm.exception.code, 2)

    @patch("phoenix_letter.common.credentials.getpass")
    def test_move_message(self, mock_get_pass):
        self.add_message(self.queue_a_url)

        result = main(self.args)

        self.assertEqual(result, ReasonStopEnum.EMPTY_RECEIVED)
        mock_get_pass.assert_not_called()

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

    @patch("phoenix_letter.common.credentials.getpass")
    def test_move_message_empty(self, mock_get_pass):
        result = main(self.args)

        self.assertEqual(result, ReasonStopEnum.EMPTY_RECEIVED)

        mock_get_pass.assert_not_called()
        mock_get_pass.reset_mock()
