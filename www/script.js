const url = "https://7ici6znw71.execute-api.us-east-1.amazonaws.com/prod/get_func-4709940";

function get() {
    fetch(
        `${url}?transactionId=1234?type=BUY?amount=250`,
        {
            method: "GET",
            headers: {
                "Content-Type": "text/plain; charset=utf-8"
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
                "Content-Type": "text/plain; charset=utf-8"
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
                "Content-Type": "text/plain; charset=utf-8"
            }
        }
    )
    .then((response) => response.json())
}