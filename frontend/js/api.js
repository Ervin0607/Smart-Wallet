const API_BASE = "http://127.0.0.1:5000";

async function apiRequest(endpoint, method="GET", body=null){

    const options = {
        method: method,
        headers:{
            "Content-Type":"application/json"
        }
    };

    if(body){
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE}${endpoint}`, options);

    return await response.json();
}