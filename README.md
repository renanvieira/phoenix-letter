# Phoenix Letter [![pypi](https://img.shields.io/pypi/v/phoenix_letter.svg)](https://pypi.org/project/phoenix-letter/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![](https://img.shields.io/pypi/pyversions/phoenix_letter.svg) [![Build Status](https://travis-ci.com/renanvieira/phoenix-letter.svg?branch=master)](https://travis-ci.com/renanvieira/phoenix-letter) ![](coverage.svg) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 
 
Bring your messages back from [Dead Letter Queue](https://en.wikipedia.org/wiki/Dead_letter_queue) with this command line script that helps you moving messages from DLQ back to the main queue for reprocessing [SQS](https://aws.amazon.com/sqs/?nc1=h_ls) queues. It also can be used to move messages between queues in SQS.

## Install
### Manually
- Mac/Linux: ```python3 setup.py install```
- Windows: ```py setup.py install```
### PyPi  
- `pip install phoenix_letter`

## Usage

After installation you will have a command with the following params:
```bash
$   phoenix_letter --help
usage: phoenix_letter [-h] --src SOURCE_QUEUE --dst DESTINATION_QUEUE [--aws-keys] --region REGION [--empty-receive EMPTY_RECEIVE] [--max N] [--max-per-request N]

optional arguments:
  -h, --help            show this help message and exit
  --src SOURCE_QUEUE    Source SQS Queue Name
  --dst DESTINATION_QUEUE
                        Destination SQS Queue Name
  --aws-keys            Flag that indicates you want to enter custom AWS keys.
  --region REGION       AWS Region
  --empty-receive EMPTY_RECEIVE
                        Max number of empty receives before giving up
  --max N               Max number of messages to process from the source queue.
  --max-per-request N   Max number of messages to received from the source queue per request (this will be pass in the MaxNumberOfMessages param). Default: 10 (AWS API max limit)
```

* `--src`: Source Queue Name
* `--dst`: Destination Queue Name
* `--aws-keys`: _[OPTIONAL]_ The CLI will prompt you to enter the AWS keys securely. Default: Fallback to Boto, more information [here](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#configuring-credentials).
* `--region`: AWS Region.
* `--empty-receive`: _[OPTIONAL]_[**default value=10**] Number of empty receives before the script gives up trying to get message from queue.*
* `--empty-receive`: _[OPTIONAL]_[**default value=10**] Number of empty receives before the script gives up trying to get message from queue.*
* `--max`: _[OPTIONAL]_[**default value=0**] Number of messages to process from the source queue. _`0` means everything_*
* `--max-per-request`: _[OPTIONAL]_[**default value=10**] Max number of messages to received from the source queue per request (this will be pass in the [MaxNumberOfMessages param](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_ReceiveMessage.html#API_ReceiveMessage_RequestParameters)). Default: 10 (AWS API max limit)


\* Sometimes the SQS returns false empty receives, where there is messages on queue but for some reason AWS decided not 
return anything on that requests. To understand more [here a link from AWS docs](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-long-polling.html).
