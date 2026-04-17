import requests

BASE_URL = "https://server.iac.ac.il/api/v1/studentapi"

# ----------------------------
# קבלת API KEY דינמית
# ----------------------------
def generate_api_key():
    student_id = input("Enter your student ID: ").strip()
    password = input("Enter your portal password: ").strip()

    r = requests.post(
        f"{BASE_URL}/generate_key",
        json={"id": student_id, "password": password},
        timeout=15
    )

    data = r.json()

    if "api_key" in data:
        return data["api_key"]
    elif "token" in data:
        return data["token"]
    else:
        print("Error generating API key:", data)
        return None


# ----------------------------
# CHAT MODE
# ----------------------------
def call_chat(headers, messages):
    payload = {
        "messages": messages,
        "max_completion_tokens": 3000
    }

    r = requests.post(
        f"{BASE_URL}/chat/completions",
        json=payload,
        headers=headers,
        timeout=60
    )

    data = r.json()

    quota = data.get("iac_quota_status")

    if "choices" not in data or not data["choices"]:
        return None, quota, data

    reply = data["choices"][0]["message"].get("content", "")

    if not reply:
        return None, quota, data

    return reply, quota, data


# ----------------------------
# AGENT MODE
# ----------------------------
def call_agent(headers, prompt, previous_response_id):
    payload = {
        "reasoning": {"effort": "low"},
        "instructions": "Answer clearly and briefly. Maximum 80 words.",
        "input": prompt,
        "tools": [{"type": "web_search"}],
        "max_output_tokens": 1000
    }

    if previous_response_id is not None:
        payload["previous_response_id"] = previous_response_id

    r = requests.post(
        f"{BASE_URL}/responses",
        json=payload,
        headers=headers,
        timeout=60
    )

    data = r.json()

    quota = data.get("iac_quota_status")

    reply = None
    for item in data.get("output", []):
        if item.get("type") == "message":
            for content_item in item.get("content", []):
                if content_item.get("type") == "output_text":
                    reply = content_item.get("text")
                    break
        if reply:
            break

    new_response_id = data.get("id")
    return reply, quota, new_response_id


# ----------------------------
# הרצה ישירה מהטרמינל
# ----------------------------
if __name__ == "__main__":
    print("=== Welcome to Smart Chat ===\n")
    API_KEY = generate_api_key()

    if not API_KEY:
        print("Could not obtain API key. Exiting.")
        exit()

    print(f"\nAPI Key obtained successfully!")
    headers = {"Authorization": f"Bearer {API_KEY}"}

    print("\nType 'exit' to quit, 'chat' to switch to chat mode, 'agent' to switch to agent mode.\n")

    while True:
        choice = input("Please select mode - 0 for simple chat or 1 for agent: ").strip()
        if choice == "0":
            state = "chat"
            break
        elif choice == "1":
            state = "agent"
            break
        else:
            print("Invalid choice. Please enter 0 or 1.")

    print(f"Started in {'Chat' if state == 'chat' else 'Agent'} mode. Type 'chat' or 'agent' to switch.\n")

    messages = [
        {
            "role": "system",
            "content": "Answer briefly and clearly."
        }
    ]
    previous_response_id = None

    while True:
        prompt = input("You: ").strip()

        if not prompt:
            continue

        if prompt.lower() == "exit":
            print("End of chat.")
            break

        if prompt.lower() == "chat":
            state = "chat"
            print("Switched to Chat mode.\n")
            continue

        if prompt.lower() == "agent":
            state = "agent"
            previous_response_id = None
            print("Switched to Agent mode.\n")
            continue

        if state == "chat":
            messages.append({"role": "user", "content": prompt})
            reply, quota, raw = call_chat(headers, messages)

            if quota:
                print(f"[Tokens: hour {quota['tokens_used_hourly']}/{quota['limit_hourly']} | day {quota['tokens_used_daily']}/{quota['limit_daily']}]")

            if not reply:
                print("Error: Empty reply from chat API.")
                print(raw)
                messages.pop()
                continue

            print("Assistant:", reply, "\n")
            messages.append({"role": "assistant", "content": reply})

        elif state == "agent":
            reply, quota, new_id = call_agent(headers, prompt, previous_response_id)

            if quota:
                print(f"[Tokens: hour {quota['tokens_used_hourly']}/{quota['limit_hourly']} | day {quota['tokens_used_daily']}/{quota['limit_daily']}]")

            if not reply:
                print("Error: Empty reply from agent API.")
                continue

            print("Assistant:", reply, "\n")
            previous_response_id = new_id
