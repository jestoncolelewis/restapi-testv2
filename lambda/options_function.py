import json

def handler(event, context):
    body = {}
    body["requestTime"] = event["requestContext"]["requestTimeEpoch"]
    body["agent"] = event["requestContext"]["identity"]["userAgent"]
    body["message"] = "All good on the backend"

    responseObject = {}
    responseObject["statusCode"] = 204
    responseObject["headers"] = {}
    responseObject["headers"]["Content-Type"] = "applications/json"
    responseObject["headers"]["Access-Control-Allow-Headers"] = "Content-Type"
    responseObject["headers"]["Access-Control-Allow-Origin"] = "*"
    responseObject["headers"]["Access-Control-Allow-Methods"] = "OPTIONS,POST,GET"
    responseObject["body"] = json.dumps(body)

    return responseObject