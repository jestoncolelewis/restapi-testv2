const url = "https://ptwo5hksng.execute-api.us-east-1.amazonaws.com/stage/";

function get() {
    fetch(
        `${url}`,
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