import os
import boto3
import logging


class S3Storage():

    session = boto3.Session(aws_access_key_id=os.getenv('AWS_SERVER_PUBLIC_KEY'),
                            aws_secret_access_key=os.getenv('AWS_SERVER_SECRET_KEY'))

    s3 = session.resource('s3')
    bucket_name = os.getenv('S3_BUCKET_NAME')

    def __init__(self):
        # Initialize the Variables
        self.logger = logging.getLogger(__name__)

    def __create_bucket(self):
        return self.s3.create_bucket(
            ACL='private',
            Bucket=self.bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': os.getenv('S3_LOCATION')
            },
        )

    def save(self, file_path):
        self.logger.info(f'Saving the file {file_path}')
        data = open(file_path, 'rb')
        key = os.path.basename(file_path)
        self.s3.Bucket(self.bucket_name).put_object(Key=key, Body=data)

    def delete(self, file_path):
        self.logger.info(f'Saving the file {file_path}')
        key = os.path.basename(file_path)
        self.s3.Bucket(self.bucket_name).delete_key(Key=key)
