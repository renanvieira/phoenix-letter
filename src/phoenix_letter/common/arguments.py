from argparse import ArgumentParser


def parse_arguments(args):
    parser = ArgumentParser()
    parser.add_argument(
        "--src",
        dest="source",
        required=True,
        help="Source SQS Queue Name",
        metavar="SOURCE_QUEUE",
    )

    parser.add_argument(
        "--dst",
        dest="destination",
        required=True,
        help="Destination SQS Queue Name",
        metavar="DESTINATION_QUEUE",
    )

    parser.add_argument(
        "--aws-keys",
        dest="input_keys",
        help="Flag that indicates you want to enter custom AWS keys.",
        action="store_true",
    )

    parser.add_argument(
        "--region",
        dest="region",
        default="us-east-1",
        required=True,
        help="AWS Region",
        metavar="REGION",
    )

    parser.add_argument(
        "--empty-receive",
        dest="max_empty_receives_count",
        default=10,
        help="Max number of empty receives before giving up",
        metavar="EMPTY_RECEIVE",
    )

    parser.add_argument(
        "--max",
        dest="max_messages",
        default=0,
        type=int,
        help="Max number of messages to process from the source queue.",
        metavar="N",
    )

    parser.add_argument(
        "--max-per-request",
        dest="max_receive_messages",
        default=10,
        type=int,
        choices=range(1, 11),
        help="Max number of messages to received from the source queue per request (this will be pass "
        "in the MaxNumberOfMessages param). Default: 10 (AWS API max limit)",
        metavar="N",
    )

    return parser.parse_args(args)
