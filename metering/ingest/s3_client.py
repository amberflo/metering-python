import json
import logging
from uuid import uuid4
from datetime import datetime

try:
    import boto3
except ImportError:
    boto3 = None


class IngestS3Client:
    """
    Alternative client for meter ingestion which sends them to an AWS S3
    bucket.
    """

    def __init__(self, bucket_name, access_key=None, secret_key=None):
        self.bucket_name = bucket_name
        self.logger = logging.getLogger(__name__)

        if not boto3:
            raise ImportError("boto3 is required to use the IngestS3Client")

        self.s3 = boto3.resource(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    def send(self, payload):
        """
        Uploads the payload to S3.

        The payload should be a list of meter records.

        Create meter records with `metering.ingest.create_ingest_payload`.
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
