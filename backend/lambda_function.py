"""
Serverless Student Feedback Portal - Lambda handler
Runtime: Python 3.12
Handles:  POST /feedback  -> validate, store in DynamoDB, notify via SNS
          GET  /feedback  -> return latest feedback entries
"""
import json
import os
import time
import uuid
from decimal import Decimal

import boto3

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")
table = dynamodb.Table(os.environ["TABLE_NAME"])
TOPIC_ARN = os.environ.get("TOPIC_ARN", "")

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
}


class DecimalEncoder(json.JSONEncoder):
    """DynamoDB returns numbers as Decimal; convert them for JSON."""
    def default(self, o):
        if isinstance(o, Decimal):
            return int(o) if o % 1 == 0 else float(o)
        return super().default(o)


def respond(status, body):
    return {"statusCode": status, "headers": HEADERS,
            "body": json.dumps(body, cls=DecimalEncoder)}


def validate(data):
    """Return an error message, or None if the data is valid."""
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    message = str(data.get("message", "")).strip()
    try:
        rating = int(data.get("rating", 0))
    except (TypeError, ValueError):
        return "Rating must be a number between 1 and 5."
    if not name or len(name) > 80:
        return "Name is required (max 80 characters)."
    if "@" not in email or len(email) > 120:
        return "A valid email is required."
    if not message or len(message) > 1000:
        return "Message is required (max 1000 characters)."
    if rating < 1 or rating > 5:
        return "Rating must be between 1 and 5."
    return None


def create_feedback(event):
    try:
        data = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return respond(400, {"error": "Request body must be valid JSON."})

    error = validate(data)
    if error:
        return respond(400, {"error": error})

    item = {
        "feedbackId": str(uuid.uuid4()),
        "name": data["name"].strip(),
        "email": data["email"].strip(),
        "message": data["message"].strip(),
        "rating": int(data["rating"]),
        "createdAt": int(time.time()),
        "pk": "FEEDBACK",
    }
    table.put_item(Item=item)

    if TOPIC_ARN:
        try:
            sns.publish(
                TopicArn=TOPIC_ARN,
                Subject="New feedback received",
                Message=f"{item['name']} ({item['rating']}/5): {item['message']}",
            )
        except Exception as exc:  # a failed email must not fail the request
            print(f"SNS publish failed: {exc}")

    return respond(201, {"message": "Thank you! Feedback saved.",
                         "feedbackId": item["feedbackId"]})


def list_feedback():
    result = table.query(
        IndexName="byCreatedAt",
        KeyConditionExpression=boto3.dynamodb.conditions.Key("pk").eq("FEEDBACK"),
        ScanIndexForward=False,   # newest first
        Limit=20,
    )
    items = [{"name": i["name"], "rating": i["rating"],
              "message": i["message"], "createdAt": i["createdAt"]}
             for i in result.get("Items", [])]
    return respond(200, {"items": items})


def lambda_handler(event, context):
    method = event.get("httpMethod") or \
        event.get("requestContext", {}).get("http", {}).get("method", "")
    print(f"Request: {method}")
    try:
        if method == "OPTIONS":
            return respond(200, {})
        if method == "POST":
            return create_feedback(event)
        if method == "GET":
            return list_feedback()
        return respond(405, {"error": "Method not allowed."})
    except Exception as exc:
        print(f"Unhandled error: {exc}")
        return respond(500, {"error": "Internal server error."})
