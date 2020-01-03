# Phoenix Letter ![](https://img.shields.io/pypi/pyversions/phoenix_letter.svg) [![Build Status](https://travis-ci.com/renanvieira/phoenix-letter.svg?branch=master)](https://travis-ci.com/renanvieira/phoenix-letter) ![](coverage.svg) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
 
Bring your messages back from [Dead Letter Queue](https://en.wikipedia.org/wiki/Dead_letter_queue) with this command line script that helps you moving messages from DLQ back to the main queue for reprocessing [SQS](https://aws.amazon.com/sqs/?nc1=h_ls) queues. It also can be used to move messages between queues in SQS.

## Usage

After installation you will have a command with the following params:
```bash
$  phoenix_letter --help
usage: main.py [-h] --src SOURCE_QUEUE --dst DESTINATION_QUEUE [--aws-keys]
               --region REGION [--empty-receive EMPTY_RECEIVE]

optional arguments:
  -h, --help               show this help message and exit
  --src SOURCE_QUEUE       Source SQS Queue Name
  --dst DESTINATION_QUEUE  Destination SQS Queue Name
  --aws-keys               Flag that indicates you want to enter custom AWS keys.
  --region REGION          AWS Region
```

* `--src`: Source Queue Name
* `--dst`: Destination Queue Name
* `--aws-keys`: _[OPTIONAL]_ The CLI will prompt you to enter the AWS keys securely. Default: Fallback to Boto, more information [here](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#configuring-credentials).
* `--region`: AWS Region.
* `--empty-receive`: _[OPTIONAL]_[**default value=10**] Number of empty receives before the script gives up trying to get message from queue.*

\* Sometimes the SQS returns false empty receives, where there is messages on queue but for some reason AWS decided not 
return anything on that requests. To understand more [here a link from AWS docs](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-long-polling.html).
