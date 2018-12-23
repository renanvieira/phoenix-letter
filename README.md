# Phoenix Letter [![Build Status](https://travis-ci.com/renanvieira/phoenix-letter.svg?branch=master)](https://travis-ci.com/renanvieira/phoenix-letter) ![](coverage.svg) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
 
Command line script to help moving messages from DLQ back to the main queue for reprocessing in AWS SQS. Can be used to move messages to any other queue.

## Usage

After installation you will have a command with the following params:
```bash
usage: phoenix_letter [-h] --src SOURCE_QUEUE --dst DESTINATION_QUEUE
                      --access-key AWS_USER_ACCESS_KEY --secret-key
                      AWS_USER_SECRET_KEY --region REGION
                      [--empty-receive EMPTY_RECEIVE]
phoenix_letter: error: the following arguments are required: --src, --dst, --access-key, --secret-key, --region
```

* `--src`: Source Queue Name
* `--dst`: Destination Queue Name
* `--access-key`: AWS Access Key, make sure that the account used here has access to both queues.
* `--secret-key`: AWS Secret Key, make sure that the account used here has access to both queues.
* `--region`: AWS Region.
* `--empty-receive`: _[OPTIONAL]_[**default value=10**] Number of empty receives before the script gives up trying to get message from queue.*

\* Sometimes the SQS returns false empty receives, where there is messages on queue but for some reason AWS decided not 
return anything on that requests. To understand more [here a lnk from AWS docs](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-long-polling.html).
