import os
import boto3
import logging


class S3Storage():

    s3 = boto3.resource('s3')
    bucket_name = 'swx.tiger.uploads.test'

    def __init__(self):
        # Initialize the Variables
        self.logger = logging.getLogger(__name__)

    def __create_bucket(self):
        return self.s3.create_bucket(
            ACL='private',
            Bucket=self.bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': 'us-west-2'
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
