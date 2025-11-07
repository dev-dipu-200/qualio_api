# handlers/processing_worker.py
import json
import boto3
import logging
import requests
from datetime import datetime
from services.acl_adapter import QualiaToInternalAdapter
from services.dynamodb_service import put_metadata
from config.settings import settings

logger = logging.getLogger(__name__)
s3 = boto3.client('s3', region_name=settings.AWS_REGION)

def handle_processing_event(event):
    """Lambda handler for processing downloaded orders and sending to internal API."""
    logger.info(f"Processing {len(event.get('Records', []))} processing records")

    for record in event.get("Records", []):
        body = json.loads(record["body"])
        order_id = body["order_id"]
        s3_key = body["s3_key"]
        checksum = body.get("checksum")

        logger.info(f"Starting processing for order {order_id}", extra={
            "order_id": order_id,
            "s3_key": s3_key
        })

        try:
            # 1. Retrieve raw payload from S3
            response = s3.get_object(Bucket=settings.S3_BUCKET, Key=s3_key)
            raw_payload = json.loads(response['Body'].read().decode('utf-8'))

            logger.info(f"Retrieved order {order_id} from S3", extra={
                "order_id": order_id,
                "s3_key": s3_key,
                "payload_size": len(json.dumps(raw_payload))
            })

            # 2. Transform using ACL adapter
            adapter = QualiaToInternalAdapter()
            transformed_data = adapter.transform(raw_payload)

            logger.info(f"Transformed order {order_id} data", extra={
                "order_id": order_id,
                "transformed_fields": list(transformed_data.keys())
            })

            # 3. Send to internal API
            headers = {
                "Authorization": f"Bearer {settings.INTERNAL_API_TOKEN}",
                "Content-Type": "application/json"
            }

            api_response = requests.post(
                settings.INTERNAL_API_URL,
                json=transformed_data,
                headers=headers,
                timeout=30
            )

            if api_response.status_code in (200, 201):
                logger.info(f"Successfully sent order {order_id} to internal API", extra={
                    "order_id": order_id,
                    "status_code": api_response.status_code,
                    "response": api_response.text
                })

                # 4. Update DB with PROCESSED status
                put_metadata(order_id, "PROCESSED", {
                    "processed_at": datetime.utcnow().isoformat() + "Z",
                    "api_status_code": api_response.status_code,
                    "checksum": checksum
                })

                logger.info(f"Successfully completed processing for order {order_id}", extra={
                    "order_id": order_id
                })

            else:
                logger.error(f"Internal API rejected order {order_id}", extra={
                    "order_id": order_id,
                    "status_code": api_response.status_code,
                    "response": api_response.text
                })
                raise RuntimeError(f"Internal API error: {api_response.status_code} - {api_response.text}")

        except Exception as e:
            logger.error(f"Processing failed for order {order_id}: {str(e)}", extra={
                "order_id": order_id,
                "s3_key": s3_key,
                "error": str(e)
            }, exc_info=True)

            # Update DB with FAILED status
            try:
                put_metadata(order_id, "FAILED", {
                    "failed_at": datetime.utcnow().isoformat() + "Z",
                    "error": str(e)
                })
            except Exception as db_error:
                logger.error(f"Failed to update failure status for order {order_id}: {str(db_error)}")

            # Let SQS retry
            raise
