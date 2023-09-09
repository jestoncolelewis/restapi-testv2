const url = "https://86900w8so3.execute-api.us-west-2.amazonaws.com/prod/functions";

function get() {
    fetch(
        `${url}?transactionId=10&type=SELL&amount=600`,
        {
            method: "GET",
            headers: {
                "Content-Type": "applications/json"
            }
        }
    )
    .then((response) => response.json());
}

function post() {
    let data = {};
    data["bodyId"] = 5;
    data["type"] = "BUY";
    data["amount"] = 600;

    fetch(
        url,
        {
            method: "POST",
            headers: {
                "Content-Type": "applications/json"
            },
        body: JSON.stringify(data)
        }
    )
    .then((response) => response.json())
}

function options() {
    fetch(
        url,
        {
            method: "OPTIONS",
            headers: {
                "Content-Type": "applications/json"
            }
        }
    )
    .then((response) => response.json())
}