# handlers/download_worker.py
import json
import logging
from datetime import datetime
from services.qualia_client import QualiaClient
from services.s3_service import upload_raw_payload
from services.dynamodb_service import put_metadata
from services.sqs_service import send_to_processing_queue

logger = logging.getLogger(__name__)

def handle_download_event(event):
    """Lambda handler for downloading orders from Qualia API."""
    logger.info(f"Processing {len(event.get('Records', []))} download records")

    for record in event.get("Records", []):
        body = json.loads(record["body"])
        order_id = body["order_id"]

        logger.info(f"Starting download for order {order_id}", extra={
            "order_id": order_id
        })

        try:
            # 1. Download from Qualia API
            client = QualiaClient()
            payload = client.download_order(order_id)

            # 2. Store to S3
            s3_key, checksum = upload_raw_payload(order_id, payload)

            # 3. Update DB with DOWNLOADED status
            put_metadata(order_id, "DOWNLOADED", {
                "s3_key": s3_key,
                "checksum": checksum,
                "downloaded_at": datetime.utcnow().isoformat() + "Z"
            })

            # 4. Queue for processing stage
            send_to_processing_queue(order_id, s3_key, checksum)

            logger.info(f"Successfully completed download for order {order_id}", extra={
                "order_id": order_id,
                "s3_key": s3_key
            })

        except Exception as e:
            logger.error(f"Download failed for order {order_id}: {str(e)}", extra={
                "order_id": order_id,
                "error": str(e)
            }, exc_info=True)
            # Let SQS retry
            raise