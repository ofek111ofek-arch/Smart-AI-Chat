import requests
headers = {"Authorization": "Bearer sk-std-AUSZLgAoxGXfopNAozhBaFo84WPH7UWg7wcO7yyQ_t0"}
payload = {
    "reasoning": {"effort": "low"},
    "instructions": "Give a short answer up to 50 words only. Talk like a pirate.",
    "input": "Are semicolons optional in JavaScript?"
}
r = requests.post("https://server.iac.ac.il/api/v1/studentapi/responses",
                  json=payload, headers=headers)
print(r.json())