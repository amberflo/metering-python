import json
import boto3
import logging
from uuid import uuid4
from datetime import datetime


class IngestS3Client:
    """
    Alternative client for meter ingestion which sends them to an AWS S3
    bucket.
    """

    def __init__(self, bucket_name, access_key=None, secret_key=None):
        self.bucket_name = bucket_name
        self.logger = logging.getLogger(__name__)

        self.s3 = boto3.resource(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def send(self, payload):
        """
        Uploads the payload to S3.
        """

        data = json.dumps(payload)

        file_name = "{}-{}.json".format(
            uuid4(), datetime.now().strftime(r"%d-%b-%Y-%H-%M-%S-%f")
        )

        response = self.s3.Object(self.bucket_name, file_name).put(Body=data)

        status_code = response["ResponseMetadata"]["HTTPStatusCode"]
        if status_code != 200:
            self.logger.warning("Failed to upload to S3: %s", response)
            # FIXME: maybe throw to trigger a retry?

        return response