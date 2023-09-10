import json

def handler(event, context):
    body = json.loads(event["body"])
    bodyID = body["bodyId"]
    bodyType = body["type"]
    bodyAmount = body["amount"]

    print("bodyID=" + bodyID)
    print("bodyType=" + bodyType)
    print("bodyAmount=" + bodyAmount)

    bodyResponse = {}
    bodyResponse["bodyID"] = bodyID
    bodyResponse["type"] = bodyType
    bodyResponse["amount"] = bodyAmount
    bodyResponse["message"] = "Hello from Lambdaland"

    responseObject = {}
    responseObject["statusCode"] = 200
    responseObject["headers"] = {}
    responseObject["headers"]["ContentType"] = "applications/json"
    responseObject["body"] = json.dumps(bodyResponse)

    return responseObject
