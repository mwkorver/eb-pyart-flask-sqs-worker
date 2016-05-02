# eb-pyart-flask-sqs-worker
This Python sample application illustrates how to use AWS Elastic Beanstalk in Worker mode to process NEXRAD as function of SNS notifications. It is designed to process SQS messages generated from a subscription to SNS topic that announce new data arriving in the 2 S3 buckets that contain the [NEXRAD Public Data Sets on AWS](http://aws.amazon.com/noaa-big-data/nexrad/). SQS Messages contain information about new NEXRAD data landing in the noaa-nexrad-level2 S3 bucket for archive data and unidata-nexrad-level2-chunks for, real-time chunk data.

The real-time (chunks) data is in the “unidata-nexrad-level2-chunks” Amazon S3 bucket.
The archive (volume scan) data is in the “noaa-nexrad-level2” Amazon S3 bucket.
Both of buckets are located in the us-east-1 Region
The respective Amazon Resource Names (ARN) of the SNS notification topics are
arn:aws:sns:us-east-1:684042711724:NewNEXRADLevel2Object.
and
arn:aws:sns:us-east-1:811054952067:NewNEXRADLevel2Archive

To subscribe your own SQS queue to NEXRAD notifications so that you can use this project, please look at [this page] (http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqssubscribe.html).

## Sample Message Format (Archive data)
To test the Amazon Beanstalk Worker app you can manually enqueue messages of the following json format:

{
  "Type" : "Notification",
  "MessageId" : "4881eba1-f3f9-5336-bbd6-a55a561cc9ea",
  "TopicArn" : "arn:aws:sns:us-east-1:811054952067:NewNEXRADLevel2Archive",
  "Subject" : "Amazon S3 Notification",
  "Message" : "{\"Records\":[{\"eventVersion\":\"2.0\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"us-east-1\",\"eventTime\":\"2015-12-28T21:03:33.544Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AROAINJPLIR64FRUFDYZO:i-2eeaae91\"},\"requestParameters\":{\"sourceIPAddress\":\"52.23.53.231\"},\"responseElements\":{\"x-amz-request-id\":\"E24FE71DCB4EF35F\",\"x-amz-id-2\":\"Me5I5Olb7wOdLuo5r6fHu8TqpQeg+0n8Kp5XdDyvZbBSenzHxBe3vZz7LGjvyfjT\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"NewNEXRADLevel2Object\",\"bucket\":{\"name\":\"noaa-nexrad-level2\",\"ownerIdentity\":{\"principalId\":\"A174AJZU80HRKD\"},\"arn\":\"arn:aws:s3:::noaa-nexrad-level2\"},\"object\":{\"key\":\"2015/12/28/KCLE/KCLE20151228_205754_V06.gz\",\"size\":20750089,\"eTag\":\"29590f045e0e599956cfe9a595945fe8\",\"sequencer\":\"005681A3A47FB77917\"}}}]}",
  "Timestamp" : "2015-12-28T21:03:33.603Z",
  "SignatureVersion" : "1",
  "Signature" : "Fn4ZeGAyHbGt+YAm9R8pxOey/QflelYzRSiziNdx/RuK8KSWVtYKHnE3imBBHtpqAj0Pxmy5BiS8inYGON7EHZgiibFAK7fZwPWak3A7QSmQ8D5fbTvmP4xxtdXs6w/Vxt/Z5RejY1LbJ0ZiLlQkfXwSZRbYCE91mASDTh0iuVv2y7zQrzA+WAqI+eVxH799UJQR+hfav2KxHPOKPd9GCtduXOgpa/xzOZHRpbNwESiBXxl03UWBwIpwy7qChKGkSTdIAJgNRBVFAzEBowNnZRhc2TOml1lLIgpq44ONc9g9B5FKfNegZ4rGp5mYwtDQL6qIem6cIg1RLtHtjp/xhg==",
  "SigningCertURL" : "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-bb750dd426d95ee9390147a5624348ee.pem",
  "UnsubscribeURL" : "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:811054952067:NewNEXRADLevel2Archive:2a3b3eef-bf2e-4d58-96a6-56d812097026"
}


## IAM Role Permissions
The worker role must run in an IAM role with permissions to SQS and S3. An example policy is included in [iam_policy.json](iam_policy.json).
