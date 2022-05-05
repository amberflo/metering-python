from metering.ingest.api_client import IngestApiClient, create_ingest_payload  # noqa
from metering.ingest.s3_client import IngestS3Client
from metering.ingest.producer import ThreadedProducer


def create_ingest_client(
    api_key=None, bucket_name=None, access_key=None, secret_key=None, **kwargs
):
    """
    Convenience method to instantiate a threaded ingest client.

    Provide either:
    - `api_key` to use the Amberflor API, or
    - `bucket_name`, `access_key` and `secret_key` to use the AWS S3 bucket.

    This will return a new instance of `metering.ingest.ThreadedProducer` with
    either `IngestApiClient` or `IngestS3Client` as backend.

    Additional keyword arguments will be passed to the ThreadedProducer
    constructor.
    """
    if api_key:
        return ThreadedProducer({"api_key": api_key}, IngestApiClient, **kwargs)

    params = {
        "bucket_name": bucket_name,
        "access_key": access_key,
        "secret_key": secret_key,
    }
    return ThreadedProducer(params, IngestS3Client, **kwargs)
