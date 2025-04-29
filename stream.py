import streamlit as st
import google.generativeai as genai

# 🔐 Configure Gemini
genai.configure(api_key="AIzaSyB3hYZ-n6HEIqgwlAtnKRhSnlr2aVTUQ8E")
model = genai.GenerativeModel("gemini-1.5-flash")

# 🧠 Toggle: Reasoning mode
use_reasoning = st.sidebar.toggle("Show Reasoning (Developer Mode)", value=False)

# 📄 Dynamic system prompt
if use_reasoning:
    system_prompt = """
You are a classical homeopathic doctor.
Your task is to identify the correct remedy based on patient symptoms.
You must reason step by step before asking each follow-up question.

Your response format should be:
🧠 Reasoning: <why you are asking this>
❓ Question: <the next question to ask>

Only ask one question at a time.
When you have enough information to suggest a remedy, reply:
✅ Thank you. I have enough details to suggest a remedy.
"""
else:
    system_prompt = """
You are a classical homeopathic doctor.
Ask only one specific, relevant question at a time to gather information from the patient.
Once you have enough details, respond with:
✅ Thank you. I have enough details to suggest a remedy.
"""

# 🔁 Chat with Gemini
def chatwithgemini(prompt):
    response = model.generate_content(prompt)
    return response.text.strip()

# 🧠 Initialize session state
if "conversation" not in st.session_state:
    st.session_state.conversation = [f"System: {system_prompt.strip()}"]
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
if "patient_data" not in st.session_state:
    st.session_state.patient_data = {}
if "done" not in st.session_state:
    st.session_state.done = False

# 🏥 UI
st.title("💊 Homeopathic Doctor Chatbot")
st.markdown("Describe your symptoms and I'll ask relevant follow-up questions like a real homeopath.")

user_input = st.chat_input("Your response...")

# 🔁 Handle input
if user_input and not st.session_state.done:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.conversation.append(f"Patient: {user_input}")

    # Extract last question
    if st.session_state.chat_log:
        last_reply = st.session_state.chat_log[-1]
        if "❓ Question:" in last_reply:
            question = last_reply.split("❓ Question:")[-1].strip()
        else:
            question = last_reply
        st.session_state.patient_data[question] = user_input
    else:
        st.session_state.patient_data["initial_complaint"] = user_input

    # Call Gemini
    prompt = "\n".join(st.session_state.conversation) + "\nDoctor:"
    doctor_reply = chatwithgemini(prompt)
    st.session_state.chat_log.append(doctor_reply)
    st.session_state.conversation.append(f"Doctor: {doctor_reply}")

    with st.chat_message("assistant"):
        st.markdown(doctor_reply)

    # Check for end
    if "✅" in doctor_reply:
        st.session_state.done = True
        st.success("Done collecting symptoms. Click below to view data or suggest remedy.")

# ✅ Suggest remedy or show data
if st.session_state.done:
    st.subheader("📋 Collected Patient Data")
    for k, v in st.session_state.patient_data.items():
        st.markdown(f"**{k.strip()}**: {v.strip()}")

    if st.button("💡 Suggest Homeopathic Remedy"):
        with st.spinner("Thinking..."):
            summary_prompt = (
                "You are a homeopathic doctor. Based on the following symptoms, suggest the most appropriate remedy "
                "and explain your reasoning clearly:\n\n"
            )
            for k, v in st.session_state.patient_data.items():
                summary_prompt += f"- {k.strip()}: {v.strip()}\n"
            summary_prompt += "\nYour response:"
            suggestion = chatwithgemini(summary_prompt)
        st.subheader("🧾 Suggested Remedy")
        st.write(suggestion)
