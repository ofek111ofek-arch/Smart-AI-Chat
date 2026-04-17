import requests

headers = {"Authorization": "Bearer sk-std-nWigFa_S1pBK9M149B4JMTlgSLP8v3IAnt_ARJQWFU"}
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