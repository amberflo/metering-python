"""
This sample shows a lambda function that gets records from CloudWatch and send
them to Amberflo.
"""

import base64
import gzip
import io
import json
import os
import time

from metering.ingest import create_ingest_client


def lambda_handler(records, context):  # noqa: C901
    client = create_ingest_client(api_key=os.environ["API_KEY"])

    # print(records)
    num_records = len(records["Records"])
    print("INFO: NumRecords is {}".format(num_records))

    for record in records["Records"]:
        datablob = record["kinesis"]["data"]
        try:
            entry = decode(datablob)
        except Exception:
            print("ERROR decode Record: {}".format(str(record)))
            continue

        print(entry)
        logevents = entry["logEvents"]

        for log_event in logevents:
            if "amberflo_meter" not in log_event["message"]:
                continue

            if "amberflo_meter:" in log_event["message"]:
                record = json.loads(log_event["message"].split("amberflo_meter:")[1])
            if '"amberflo_meter":' in log_event["message"]:
                record = json.loads(log_event["message"])["amberflo_meter"]
            if "tenant" in record:
                record["customerId"] = record["tenant"]
            if "tenant_id" in record:
                record["customerId"] = record["tenant_id"]
            if "customerId" in record:
                record["customer"] = record["customerId"]
            if "time" not in record:
                record["time"] = int(round(time.time() * 1000))
            if "dimensions" in record and record["dimensions"] is None:
                del record["dimensions"]

            client.send(record)

    client.shutdown()

    return ""


def decode(datablob):
    try:
        data = base64.b64decode(datablob)
        striodata = io.BytesIO(data)
        with gzip.GzipFile(fileobj=striodata, mode="r") as f:
            entry = json.loads(f.read())
        return entry
    except Exception as e:
        print("ERROR: Unable to decode kinesis datablob")
        print("ERROR: {}".format(e))
        raise e
