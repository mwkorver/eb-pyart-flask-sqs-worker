# Copyright 2015. Amazon Web Services, Inc. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
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

import numpy as np
import matplotlib.pyplot as plt
import pyart
import tempfile
import time

local_Dir = '/tmp/'
log_bucket = 'eb-pyart-flask-sqs-worker-output'
filterCondition = '*'                      

# Create and configure the Flask app
application = flask.Flask(__name__)
application.config.from_object('default_config')
application.debug = application.config['FLASK_DEBUG'] in ['true', 'True']


@application.route('/heartbeat', methods=['GET'])
def heartbeat():
    """Process NEXRAD data by parsing SQS message"""
    response = Response("running", status=200)
    return response

@application.route('/nexrad', methods=['POST'])
def customer_registered():
    """Process NEXRAD data by parsing SQS message"""
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

            # Filter for a particular station
            if (filterCondition in objectKey) or (filterCondition == '*'):

                file_name = local_Dir + objectKey
                if not os.path.exists(os.path.dirname(file_name)):
                    os.makedirs(os.path.dirname(file_name))   

                s3_conn = boto.connect_s3()
                srcBucket = s3_conn.get_bucket(bucketName, validate=False)
                from boto.s3.key import Key
                srcKey = Key(srcBucket)
                srcKey.key = objectKey            

                # Do something to the data here.

                # Download to a local file, and read it
                # localfile = tempfile.NamedTemporaryFile()
                localfile = tempfile.NamedTemporaryFile(delete=True)
                print('starting to get object from S3')
                srcKey.get_contents_to_filename(localfile.name)
                print('done getting object from S3')

                radar = pyart.io.read_nexrad_archive(localfile.name)
                localfile.close()  # deletes the temp file

                print('Doing Grid')
                start = time.time()
                lon0 = radar.longitude['data'][0]
                lat0 = radar.latitude['data'][0]
                radar_list = [radar]
                grid = pyart.map.grid_from_radars(radar_list, grid_shape=(20, 201, 201), grid_limits=((1000, 20000), (-200000, 200000), (-200000, 200000)), grid_origin = (lat0, lon0), fields=['reflectivity'],gridding_algo='map_gates_to_grid',grid_origin_alt=0.0)
                print('Grid Done')
                end = time.time()
                print(end - start)

                print('Starting to write geotif')
                pyart.io.write_grid_geotiff(grid, 'test_warp', 'reflectivity', rgb=True, warp=True, vmin=0, vmax=75,cmap='pyart_LangRainbow12', sld=False)
                print('Done writing geotif')


                # Writes result to own S3 bucket using Boto 2.x
                s3_conn = boto.connect_s3()
                logBucket = s3_conn.get_bucket(log_bucket, validate=False)
                from boto.s3.key import Key
                logKey = Key(logBucket)
                destKey = objectKey.split('.')[0]
                logKey.key = destKey.split('/')[3] + '.tif'
                print('Starting to write file: ' + logKey.key + ' to S3')
                logKey.set_contents_from_filename('test_warp.tif')
                print('Finished writing to S3')

                response = Response("processed NEXRAD data:  " + objectKey, status=200)

            else:
                response = Response("This data does not satisfy filter condition [ " + filterCondition + " ]", status=200)

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


          


















          
