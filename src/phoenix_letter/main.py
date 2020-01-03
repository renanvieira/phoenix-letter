import random
import sys
from argparse import ArgumentParser
from time import sleep
from getpass import getpass

import boto3


def parse_arguments(args):
    parser = ArgumentParser()
    parser.add_argument("--src", dest="source",
                        required=True,
                        help="Source SQS Queue Name",
                        metavar="SOURCE_QUEUE")

    parser.add_argument("--dst", dest="destination",
                        required=True,
                        help="Destination SQS Queue Name",
                        metavar="DESTINATION_QUEUE")

    parser.add_argument("--aws-keys", dest="input_keys",
                        help="Flag that indicates you want to enter custom AWS keys.", action='store_true')

    parser.add_argument("--region", dest="region", default="us-east-1",
                        required=True,
                        help="AWS Region",
                        metavar="REGION")

    parser.add_argument("--empty-receive", dest="max_empty_receives_count", default=10,
                        help="Max number of empty receives before giving up",
                        metavar="EMPTY_RECEIVE")

    return parser.parse_args(args)


def get_credentials():
    access_key = getpass("AWS Access Key:")
    secret_key = getpass("AWS Secret Key:")

    return access_key, secret_key


def main(args=None):
    args = parse_arguments(args)

    if args.input_keys:
        aws_access_key, aws_secret_key = get_credentials()
    else:
        aws_access_key, aws_secret_key = (None, None)

    sqs_client = boto3.client("sqs", region_name=args.region,
                              aws_access_key_id=aws_access_key,
                              aws_secret_access_key=aws_secret_key)

    print("Getting Queue URLs")

    source_queue = sqs_client.get_queue_url(QueueName=args.source)
    source_queue_url = source_queue['QueueUrl']

    destination_queue = sqs_client.get_queue_url(QueueName=args.destination)
    destination_queue_url = destination_queue['QueueUrl']

    number_of_empty_receives = 0

    while number_of_empty_receives <= int(args.max_empty_receives_count):
        print("Receiving message...")
        received_response = sqs_client.receive_message(QueueUrl=source_queue_url, MessageAttributeNames=["All"],
                                                       AttributeNames=['All'],
                                                       MaxNumberOfMessages=10)

        if ("Messages" not in received_response) or (len(received_response['Messages']) == 0):
            print("Queue did not returned messages")

            number_of_empty_receives += 1
            sleep_time = random.randint(500, 2000) / 1000

            print("Sleeping for {} seconds".format(sleep_time))
            sleep(sleep_time)

            continue

        print("Received {} messages".format(len(received_response['Messages'])))

        for message in received_response['Messages']:
            print("Sending message to '{}'".format(args.destination))

            send_response = sqs_client.send_message(QueueUrl=destination_queue_url,
                                                    MessageBody=message['Body'],
                                                    MessageAttributes=message['MessageAttributes'])

            print("Deleting message from '{}'".format(args.source))
            sqs_client.delete_message(QueueUrl=source_queue_url,
                                      ReceiptHandle=message['ReceiptHandle'])

    print("Giving up after {} empty receives from the source queue.".format(number_of_empty_receives))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
