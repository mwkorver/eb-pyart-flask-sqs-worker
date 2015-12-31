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
# just test line here xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

import logging
import os
import json
import flask
from flask import request, Response
import boto
import urllib.request	

local_Dir = '/tmp/'
url_S3_Prefix = 'http://s3.amazonaws.com/'
log_bucket = 'usgs-naip'                      

# Create and configure the Flask app
application = flask.Flask(__name__)
application.config.from_object('default_config')
application.debug = application.config['FLASK_DEBUG'] in ['true', 'True']

@application.route('/nexrad', methods=['POST'])
def customer_registered():
    """Send an e-mail using SES"""
    response = None
    if request.json is None:
        # Expect application/json request
        response = Response("no json in body", status=415)
    else:
        message = dict()
        try:
            # If the message has an SNS envelope, extract the inner message
            if 'TopicArn' in request.json and 'Message' in request.json:
            	#if 'TopicArn' in request.json:
                logging.exception('in the test loop tttttttttttttttttttttttttttttttttttttttttttttttt')
                message = json.loads(request.json['Message'])                
                bucketName = message['Records'][0]['s3']['bucket']['name']
                objectKey = message['Records'][0]['s3']['object']['key']
                value = bucketName + '/' + objectKey
                #response = Response(value, status=200)
            else:
                response = Response("in else part", status=200)    
                # message = request.json

            url = url_S3_Prefix + bucketName + "/" + objectKey
            file_name = local_Dir + objectKey
            if not os.path.exists(os.path.dirname(file_name)):
                os.makedirs(os.path.dirname(file_name))		

            open(file_name, 'a+')
            # this writes to local
            urllib.request.urlretrieve(url, file_name)

            s3_conn = boto.connect_s3()
            srcBucket = s3_conn.get_bucket(bucketName, validate=False)
            from boto.s3.key import Key
            srcKey = Key(srcBucket)
            srcKey.key = objectKey
            srcKey.get_contents_to_filename('/tmp/test.test')

            # Do something to the data here.

            # Boto 2.x
            s3_conn = boto.connect_s3()
            logBucket = s3_conn.get_bucket(log_bucket, validate=False)
            from boto.s3.key import Key
            logKey = Key(logBucket)
            logKey.key = objectKey
            logKey.set_contents_from_filename(file_name)

            # Boto 3
            # s3 = boto3.resource('s3')
            # s3.Object(log_bucket, objectKey).put(Body=open(file_name, 'rb'))            

            response = Response(value, status=200)

        except Exception as ex:
            logging.exception('Error processing SQS message: %s' % request.json)
            # response = Response(ex.message, status=500))
            response = Response("exception part -eeeeeeeeeeeeeeeee", status=500)
            raise
            # response = Response(flask.jsonify(request.json), status=500)

    return response

# https://codeseekah.com/2012/10/28/dubugging-flask-applications-under-uwsgi/
if ( application.debug ):
    from werkzeug.debug import DebuggedApplication
    application.wsgi_app = DebuggedApplication( application.wsgi_app, True )

if __name__ == '__main__':
    application.run(host='0.0.0.0')

