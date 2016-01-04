# Copyright 2015. Amazon Web Services, Inc. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import flask
import boto
import logging
import os
import json
from flask import request, Response

local_Dir = '/tmp/'
log_bucket = 'eb-py-flask-sqs-worker-log'
radarSite = 'KCLEx'                      

# Create and configure the Flask app
application = flask.Flask(__name__)
application.config.from_object('default_config')
application.debug = application.config['FLASK_DEBUG'] in ['true', 'True']

@application.route('/nexrad', methods=['POST'])
def customer_registered():
    """Process NEXRAD data using by parsing SQS message"""
    response = None
    if request.json is None:
        # Expect application/json request
        response = Response("no json in body", status=415)
    else:
        message = dict()
        try:
            # If the message has an SNS envelope, extract the inner message
            if 'TopicArn' in request.json and 'Message' in request.json:
                message = json.loads(request.json['Message'])                
            else:
                message = json.loads(request.json)

            bucketName = message['Records'][0]['s3']['bucket']['name']
            objectKey = message['Records'][0]['s3']['object']['key']
            #value = bucketName + '/' + objectKey

            # Filter for a particular station
            if radarSite in objectKey:

                file_name = local_Dir + objectKey
                if not os.path.exists(os.path.dirname(file_name)):
                    os.makedirs(os.path.dirname(file_name))		

                s3_conn = boto.connect_s3()
                srcBucket = s3_conn.get_bucket(bucketName, validate=False)
                from boto.s3.key import Key
                srcKey = Key(srcBucket)
                srcKey.key = objectKey
                srcKey.get_contents_to_filename(file_name)

                # Do something to the data here.

                # Writes result to own S3 bucket using Boto 2.x
                s3_conn = boto.connect_s3()
                logBucket = s3_conn.get_bucket(log_bucket, validate=False)
                from boto.s3.key import Key
                logKey = Key(logBucket)
                logKey.key = objectKey
                logKey.set_contents_from_filename(file_name)

                response = Response("processed NEXRAD data:  " + objectKey, status=200)

            else:
                response = Response("This data does not satisfy filter:  " + objectKey, status=200)

        except Exception as ex:
            logging.exception('Error processing SQS message: %s' % request.json)
            response = Response("exception", status=500)
            raise

    return response

# from https://codeseekah.com/2012/10/28/dubugging-flask-applications-under-uwsgi/
if ( application.debug ):
    from werkzeug.debug import DebuggedApplication
    application.wsgi_app = DebuggedApplication( application.wsgi_app, True )

if __name__ == '__main__':
    application.run(host='0.0.0.0')

