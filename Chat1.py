import requests

headers = {"Authorization": "Bearer sk-std-AUSZLgAoxGXfopNAozhBaFo84WPH7UWg7wcO7yyQ_t0"}
payload = {
    "messages": [
        {
            "role": "user",
            "content": "what is better a cat or a dog? give a short, up to 50 words answer."
        }
    ],
    "max_completion_tokens": 500
}

r = requests.post("https://server.iac.ac.il/api/v1/studentapi/chat/completions",
                  json=payload, headers=headers)
print(r.json())