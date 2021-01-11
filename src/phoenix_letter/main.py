import random
import sys
from time import sleep

import boto3

from phoenix_letter.common.arguments import parse_arguments
from phoenix_letter.common.credentials import get_credentials
from phoenix_letter.common.enums import ReasonStopEnum


def main(args=None):
    args = parse_arguments(args)

    if args.input_keys:
        aws_access_key, aws_secret_key = get_credentials()
    else:
        aws_access_key, aws_secret_key = (None, None)

    sqs_client = boto3.client(
        "sqs",
        region_name=args.region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
    )

    print("Getting Queue URLs")

    source_queue = sqs_client.get_queue_url(QueueName=args.source)
    source_queue_url = source_queue["QueueUrl"]

    destination_queue = sqs_client.get_queue_url(QueueName=args.destination)
    destination_queue_url = destination_queue["QueueUrl"]

    number_of_empty_receives = 0
    total_messages_received = 0

    reason = None

    while True:
        if number_of_empty_receives == int(args.max_empty_receives_count):
            reason = ReasonStopEnum.EMPTY_RECEIVED
            break
        elif 0 < args.max_messages <= total_messages_received:
            reason = ReasonStopEnum.MAX_MESSAGES_RECEIVED
            break

        print("Receiving message...")
        received_response = sqs_client.receive_message(
            QueueUrl=source_queue_url,
            MessageAttributeNames=["All"],
            AttributeNames=["All"],
            MaxNumberOfMessages=args.max_receive_messages,
        )

        if ("Messages" not in received_response) or (
            len(received_response["Messages"]) == 0
        ):
            print("Queue did not returned messages")

            number_of_empty_receives += 1
            sleep_time = random.randint(500, 2000) / 1000

            print("Sleeping for {} seconds".format(sleep_time))
            sleep(sleep_time)

            continue

        messages_received = len(received_response["Messages"])

        total_messages_received += messages_received

        print("Received {} messages".format(messages_received))

        for message in received_response["Messages"]:
            print("Sending message to '{}'".format(args.destination))

            if "MessageAttributes" in message:
                sqs_client.send_message(
                    QueueUrl=destination_queue_url,
                    MessageBody=message["Body"],
                    MessageAttributes=message["MessageAttributes"],
                )
            else:
                sqs_client.send_message(
                    QueueUrl=destination_queue_url, MessageBody=message["Body"]
                )

            print("Deleting message from '{}'".format(args.source))
            sqs_client.delete_message(
                QueueUrl=source_queue_url, ReceiptHandle=message["ReceiptHandle"]
            )

    if reason == ReasonStopEnum.MAX_MESSAGES_RECEIVED:
        print("Stopping after processing {} messages.".format(total_messages_received))
    else:
        print(
            "Giving up after {} empty receives from the source queue.".format(
                number_of_empty_receives
            )
        )

    return reason


if __name__ == "__main__":  # pragma: no cover
    response = main(sys.argv[1:])
    print("Stop Reason: {}".format(response.name))
    sys.exit(0)
