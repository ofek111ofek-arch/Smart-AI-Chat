import requests
headers = {"Authorization": "Bearer sk-std-nWigFa_S1pBK9M149B4JMTlgSLP8v3IAnt_ARJQWFU"}
payload = {
    "reasoning": {"effort": "low"},
    "instructions": "Give a short answer up to 50 words only. Talk like a pirate.",
    "input": "Are semicolons optional in JavaScript?"
}
r = requests.post("https://server.iac.ac.il/api/v1/studentapi/responses",
                  json=payload, headers=headers)
print(r.json())