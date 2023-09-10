import json

def handler(event, context):
    # transactionID = event["queryStringParameters"]["transactionId"]
    # transactionType = event["queryStringParameters"]["type"]
    # transactionAmount = event["queryStringParameters"]["amount"]

    # print("transactionID=" + transactionID)
    # print("transactionType=" + transactionType)
    # print("transactionAmount=" + transactionAmount)

    transactionResponse = {}
    # transactionResponse["transactionID"] = transactionID
    # transactionResponse["type"] = transactionType
    # transactionResponse["amount"] = transactionAmount
    transactionResponse["message"] = "Hello from Lambdaland"

    responseObject = {}
    responseObject["statusCode"] = 200
    responseObject["headers"] = {}
    responseObject["headers"]["ContentType"] = "applications/json"
    responseObject["body"] = json.dumps(transactionResponse)

    return responseObject
