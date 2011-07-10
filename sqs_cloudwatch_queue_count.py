#!/usr/bin/python
#
# Copyright 2009 Eran Sandler (eran@sandler.co.il)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import sys
import logging
import logging.handlers
from optparse import OptionParser

from boto.ec2.cloudwatch import CloudWatchConnection
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
from boto.sns import SNSConnection

class SQSCloudWatchQueueCount(object):
	_sqs_connection = None
	_cloud_watch_connection = None
	
	def __init__(self, aws_access_key, aws_secret_access_key, queue_name, namespace, metric_name):
		if aws_access_key is None or aws_access_key == "":
			raise Exception("aws_access_key cannot be null")
			
		if aws_secret_access_key is None or aws_secret_access_key == "":
			raise Exception("aws_secret_access_key cannot be null")
			
		if queue_name is None or queue_name == "":
			raise Exception("queue_name cannot be null")
		
		if namespace is None or namespace == "":
			raise Exception("namespace cannot be null")
		
		if metric_name is None or metric_name == "":
			raise Exception("metric_name cannot be null")
		
		self.aws_access_key = aws_access_key
		self.aws_secret_access_key = aws_secret_access_key
		
		self.queue_name = queue_name
		self.namespace = namespace
		self.metric_name = metric_name
		
	@property
	def sqs_connection(self):
		if self._sqs_connection is None:
			self._sqs_connection = SQSConnection(self.aws_access_key, self.aws_secret_access_key)
		
		return self._sqs_connection
	
	@property
	def cloud_watch_connection(self):
		if self._cloud_watch_connection is None:
			self._cloud_watch_connection = CloudWatchConnection(self.aws_access_key, self.aws_secret_access_key)
		
		return self._cloud_watch_connection
	
	def _get_queue_by_name(self, queue_name):
		rs = self.sqs_connection.get_all_queues()

		for q in rs:
			if q.name == queue_name:
				return q
				
		return None
		
	def check(self):
		logging.info("Check Started")
		queue = self._get_queue_by_name(self.queue_name)
		if not queue:
			raise Exception("Unknown queue '%s'" % self.queue_name)
		
		logging.info("Got Queue=%s" % self.queue_name)
			
		count = queue.count()
		logging.info("Queue Count: %d" % count)
		result = self.cloud_watch_connection.put_metric_data(self.namespace, self.metric_name, count, unit="Count")
		logging.info("Call Result: %s" % str(result))
		logging.info("Check Ended")

def main():	
	parser = OptionParser(description='AWS SQS queue status check command line tool')
	parser.add_option('-k', '--aws_access_key_id', help='AWS Access Key ID')
	parser.add_option('-s', '--aws_secret_access_key', help='AWS Secret Access Key')
	parser.add_option('-q', '--queue_name', help='Name of queue to check count')
	parser.add_option('-n', '--namespace', help='The metric namespace')
	parser.add_option('-m', '--metric_name', help='The metric name')
	parser.add_option('-l', '--log', help="Location of the log file")

	(options, args) = parser.parse_args()
	
	if options.aws_access_key_id is None and options.aws_secret_access_key is None:
		env_AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
		env_AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
		if not (env_AWS_ACCESS_KEY_ID and env_AWS_SECRET_ACCESS_KEY):
			print "ERROR: Missing AWS_ACCESS_KEY_ID parameter. Set it via command line or via the AWS_ACCESS_KEY_ID envrionment variable."
			print "ERROR: Missing AWS_SECRET_ACCESS_KEY parameter. Set it via command line or via the AWS_SECRET_ACCESS_KEY envrionment variable."
			sys.exit(2)
		else:
			options.aws_access_key_id = env_AWS_ACCESS_KEY_ID
			options.aws_secret_access_key = env_AWS_SECRET_ACCESS_KEY
	
	if options.log:
		logger = logging.getLogger()
		handler = logging.handlers.TimedRotatingFileHandler(options.log, "midnight", backupCount=3, utc=True)
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		logger.setLevel(logging.INFO)
		
	watch_queue_count = SQSCloudWatchQueueCount(options.aws_access_key_id, options.aws_secret_access_key, options.queue_name, options.namespace, options.metric_name)
	watch_queue_count.check()

if __name__ == "__main__":
	main()