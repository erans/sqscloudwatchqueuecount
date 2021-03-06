sqs_cloud_watch_queue_count.py updates an AWS CloudWatch custom metric with an SQS queue length.

This allows you to create custom alerts based on the queue's length such as adding more workers to handle the queues if the queue's size doesn't drop below a threashold for a certain period of time.
I'm using it in production via a cron job that runs every 1 minute.

REQUIREMENTS:
=============
* boto 2.0rc1 and above


NOTES:
======
- AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY can also be read from the envrionment by variables with the same name
- if -l (--log) is not set logging will not be printed 


Usage:
======
Usage: sqs_cloudwatch_queue_count.py [options]

AWS SQS queue status check command line tool

Options:
  -h, --help            show this help message and exit
  -k AWS_ACCESS_KEY_ID, --aws_access_key_id=AWS_ACCESS_KEY_ID
                        AWS Access Key ID
  -s AWS_SECRET_ACCESS_KEY, --aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                        AWS Secret Access Key
  -q QUEUE_NAME, --queue_name=QUEUE_NAME
                        Name of queue to check count
  -n NAMESPACE, --namespace=NAMESPACE
                        The metric namespace
  -m METRIC_NAME, --metric_name=METRIC_NAME
                        The metric name
  -l LOG, --log=LOG     Location of the log file



