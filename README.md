# eb-py-flask-sqs-worker
This Python sample application illustrates the worker role functionality of AWS Elastic Beanstalk. It is designed to process SQS messages generated from a subscription to the [NEXRAD Public Data Set on AWS](http://aws.amazon.com/noaa-big-data/nexrad/). SQS Messages contain information about new NEXRAD data landing in the noaa-nexrad-level2 S3 bucket for archive data and unidata-nexrad-level2-chunks for, real-time chunk data.


## Message Format
To test the worker app without the frontend, you can manually enqueue messages of the following json format and send to the worker app using an HTTP POST request:

{
  "Type" : "Notification",
  "MessageId" : "74412159-e129-5807-b697-6fa2761c8a0a",
  "TopicArn" : "arn:aws:sns:us-east-1:684042711724:NewNEXRADLevel2Object",
  "Subject" : "Amazon S3 Notification",
  "Message" : "{\"Records\":[{\"eventVersion\":\"2.0\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"us-east-1\",\"eventTime\":\"2015-12-28T20:00:53.031Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AROAINJPLIR64FRUFDYZO:i-2eeaae91\"},\"requestParameters\":{\"sourceIPAddress\":\"52.23.53.231\"},\"responseElements\":{\"x-amz-request-id\":\"AA0225D63D9F838D\",\"x-amz-id-2\":\"oL8eV6o9WAV52ScQAhbXDr42B9riZyMCZwS1NhDoTEKhetA8RmyrqB5pEyx+DAyh8vk3pVJbab0=\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"NewNEXRADLevel2Object\",\"bucket\":{\"name\":\"unidata-nexrad-level2-chunks\",\"ownerIdentity\":{\"principalId\":\"AMNSLGO92Q3HN\"},\"arn\":\"arn:aws:s3:::unidata-nexrad-level2-chunks\"},\"object\":{\"key\":\"KDAX/734/20151228-200051-001-S\",\"size\":11714,\"eTag\":\"e3d721125d839db8337f32636c33d2b9\",\"sequencer\":\"00568194F4F94A44B5\"}}}]}",
  "Timestamp" : "2015-12-28T20:00:53.075Z",
  "SignatureVersion" : "1",
  "Signature" : "bKuLvkPvTXYPGYDM3r4v8AcQPaC/MsZ0ETdJ52awMCcLc13LObGFo2cPFLPAVw0foNrRTtQ13JOJGIHRlcj5O84pFPYGAmtc2lVpWGX3r/FOGNRnMDkykUEpUNJqpYKhv1lRKJuhope0QqgD2PiLaAbBdQSHUZDhgGAruPrc0FuCVIbq1R2sSgUfqjUEm77QEfdwlf7IMxN2yPJ9k0AyC3rbGEXZv4ek+tKCnRUvKiFg3cAp/yZWuaA0BpiBDrVRu7zag3rdPxTpfaEy8DapU2RwNORu3CL2QR7007Syl6mtZEzprep9ZyE6sSxuRPEx1pKzs1wlVmArT4g3KR4JwA==",
  "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-bb750dd426d95ee9390147a5624348ee.pem",
  "UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:684042711724:NewNEXRADLevel2Object:b97bbc7a-657c-434a-a4ee-a142ae34e8cf"
}

## IAM Role Permissions
The worker role must run in an IAM role with permissions to SQS and S3. An example policy is included in [iam_policy.json](iam_policy.json).
