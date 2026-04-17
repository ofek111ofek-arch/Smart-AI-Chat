import streamlit as st
import requests
from chat_loop import call_chat, call_agent

BASE_URL = "https://server.iac.ac.il/api/v1/studentapi"

# ----------------------------
# Page configuration
# ----------------------------
st.set_page_config(
    page_title="Smart AI Chat",
    page_icon="💬",
    layout="centered"
)

st.title("💬 Smart AI Chat")
st.caption("Streamlit frontend for Chat Completions and Agentic Responses")

# ----------------------------
# Helper functions
# ----------------------------
def generate_api_key_ui(student_id: str, password: str):
    response = requests.post(
        f"{BASE_URL}/generate_key",
        json={"id": student_id, "password": password},
        timeout=15
    )
    data = response.json()
    if "api_key" in data:
        return data["api_key"], data
    if "token" in data:
        return data["token"], data
    return None, data


def get_headers():
    return {"Authorization": f"Bearer {st.session_state.api_key}"}


def reset_chat_state(mode_name: str):
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": f"{mode_name} mode is ready. Start chatting."
        }
    ]
    st.session_state.chat_history_for_api = [
        {
            "role": "system",
            "content": "Answer briefly and clearly."
        }
    ]
    st.session_state.previous_response_id = None
    st.session_state.quota_status = None


# ----------------------------
# Session state initialization
# ----------------------------
if "api_key" not in st.session_state:
    st.session_state.api_key = None

if "mode" not in st.session_state:
    st.session_state.mode = "Chat"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! Please log in and start chatting."
        }
    ]

if "chat_history_for_api" not in st.session_state:
    st.session_state.chat_history_for_api = [
        {
            "role": "system",
            "content": "Answer briefly and clearly."
        }
    ]

if "previous_response_id" not in st.session_state:
    st.session_state.previous_response_id = None

if "quota_status" not in st.session_state:
    st.session_state.quota_status = None

# ----------------------------
# Login section
# ----------------------------
if st.session_state.api_key is None:
    st.subheader("🔐 Login")

    student_id = st.text_input("Student ID")
    password = st.text_input("Portal Password", type="password")

    if st.button("Generate API Key"):
        if not student_id or not password:
            st.error("Please enter both Student ID and Password.")
        else:
            api_key, raw_data = generate_api_key_ui(student_id, password)

            if api_key:
                st.session_state.api_key = api_key
                reset_chat_state(st.session_state.mode)
                st.success("API Key generated successfully!")
                st.rerun()
            else:
                st.error(f"Failed to generate API key: {raw_data}")

    st.stop()

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    st.header("Settings")

    selected_mode = st.radio(
        "Choose mode",
        ["Chat", "Agent"],
        index=0 if st.session_state.mode == "Chat" else 1
    )

    max_tokens = st.slider("Max tokens", 100, 10000, 3000, 100)

    if selected_mode != st.session_state.mode:
        st.session_state.mode = selected_mode
        reset_chat_state(selected_mode)
        st.rerun()

    if st.button("Clear chat"):
        reset_chat_state(st.session_state.mode)
        st.rerun()

    if st.button("Log out"):
        st.session_state.api_key = None
        reset_chat_state("Chat")
        st.session_state.mode = "Chat"
        st.rerun()

    st.markdown("---")
    st.write(f"**Current mode:** {st.session_state.mode}")

    if st.session_state.quota_status:
        quota = st.session_state.quota_status
        st.write("**Quota status**")
        st.write(f"Hour: {quota.get('tokens_used_hourly', 'N/A')} / {quota.get('limit_hourly', 'N/A')}")
        st.write(f"Day: {quota.get('tokens_used_daily', 'N/A')} / {quota.get('limit_daily', 'N/A')}")
        st.write(f"Month: {quota.get('tokens_used_monthly', 'N/A')} / {quota.get('limit_monthly', 'N/A')}")

# ----------------------------
# Display chat history
# ----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ----------------------------
# Chat input
# ----------------------------
user_prompt = st.chat_input("Type your message...")

if user_prompt:
    if user_prompt.lower() == "exit":
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "Chat ended. You can continue typing or clear the chat."
            }
        )
        st.rerun()

    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_placeholder.markdown("Thinking...")

        try:
            if st.session_state.mode == "Chat":
                st.session_state.chat_history_for_api.append(
                    {"role": "user", "content": user_prompt}
                )

                reply, quota, raw = call_chat(
                    get_headers(),
                    st.session_state.chat_history_for_api
                )

                if reply:
                    st.session_state.chat_history_for_api.append(
                        {"role": "assistant", "content": reply}
                    )
                else:
                    st.session_state.chat_history_for_api.pop()
                    raise ValueError(f"Empty reply from chat API: {raw}")

            else:
                with st.spinner("🤖 Thinking..."):
                    reply, quota, new_id = call_agent(
                        get_headers(),
                        user_prompt,
                        st.session_state.previous_response_id
                    )

                if reply:
                    st.session_state.previous_response_id = new_id
                else:
                    raise ValueError("Empty reply from agent API.")

            if quota:
                st.session_state.quota_status = quota

            assistant_reply = reply
            response_placeholder.markdown(assistant_reply)

        except Exception as e:
            assistant_reply = f"Error: {str(e)}"
            response_placeholder.error(assistant_reply)

    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
