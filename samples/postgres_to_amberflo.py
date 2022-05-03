#!/usr/bin/env python3

"""
This sample shows an example of meter record ingestion, using a PostgreSQL
instance as record source.

Ingestion is done in batches on a background thread for high-throughput.

See https://docs.amberflo.io/reference/post_ingest
"""

import os
from datetime import timezone

import psycopg2
from psycopg2.extras import RealDictCursor

from metering.ingest import get_ingest_client, create_ingest_payload


def get_conn():
    return psycopg2.connect(
        host="database-1.myhost.us-west-2.rds.amazonaws.com",
        database="staging",
        user="pg_user",
        password="pg_password",
        port="5432",
    )


def main():
    # 1. initialize the threaded ingestion client
    client = get_ingest_client(api_key=os.environ["API_KEY"])

    # 2. get events from postgres
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT
            id,
            service_id,
            duration_in_seconds,
            completed_at,
            host_name
        FROM
            events
        WHERE
            completed_at >= (NOW() - INTERVAL '12 hours')
    """
    )
    records = cur.fetchall()

    # 3. ingest the events
    for record in records:
        completed_at = record["completed_at"].replace(tzinfo=timezone.utc)

        event = create_ingest_payload(
            meter_api_name="backup_processing_time",
            meter_value=1,
            meter_time_in_millis=int(round(completed_at.timestamp() * 1000)),
            customer_id=record["service_id"],
            unique_id=record["id"],
            dimensions={
                "host_name": record["host_name"],
            },
        )
        client.send(event)

    # 4. close postgres connection
    cur.close()
    conn.close()

    # 5. ensure all events are sent and safely stop the background threads
    client.shutdown()


if __name__ == "__main__":
    main()
