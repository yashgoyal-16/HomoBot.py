import streamlit as st
import google.generativeai as genai

# 🔐 Configure Gemini
genai.configure(api_key="AIzaSyB3hYZ-n6HEIqgwlAtnKRhSnlr2aVTUQ8E")
model = genai.GenerativeModel("gemini-1.5-flash")

# 📄 System prompt with reasoning option
show_reasoning = st.sidebar.checkbox("Show Reasoning", value=True)

if show_reasoning:
    system_prompt = """
You are a classical homeopathic doctor. Your task is to ask the patient only important, relevant questions one at a time.
You should:
- Ask clear, natural questions, with a friendly tone
- **Explain** the reasoning behind each question
- Focus on gathering the most important details first
- Avoid asking unnecessary questions
- When you feel you have enough details, say: "I have enough information to suggest a remedy."
"""
else:
    system_prompt = """
You are a classical homeopathic doctor. Ask only the **important, relevant questions** to gather symptoms.
Once you have enough details, simply say: "I have enough information to suggest a remedy."
"""

# 🔁 Chat with Gemini function
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
st.markdown("Describe your symptoms in your own words, and I'll ask a few questions like a real doctor.")

user_input = st.chat_input("Your response...")

# 🔁 Handle user input
if user_input and not st.session_state.done:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.conversation.append(f"Patient: {user_input}")

    # Extract previous question for storing response
    if st.session_state.chat_log:
        last_reply = st.session_state.chat_log[-1]
        question = last_reply.strip()
        st.session_state.patient_data[question] = user_input
    else:
        st.session_state.patient_data["Initial complaint"] = user_input

    # Call Gemini for the next question based on conversation context
    prompt = "\n".join(st.session_state.conversation) + "\nDoctor:"
    doctor_reply = chatwithgemini(prompt)
    st.session_state.chat_log.append(doctor_reply)
    st.session_state.conversation.append(f"Doctor: {doctor_reply}")

    with st.chat_message("assistant"):
        st.markdown(doctor_reply)

    # If enough data has been collected, set done to True
    if "I have enough information" in doctor_reply:
        st.session_state.done = True
        st.success("Done collecting symptoms. Click below to view data or suggest a remedy.")

# ✅ Show collected data and suggest remedy
if st.session_state.done:
    st.subheader("📋 Collected Patient Data")
    for k, v in st.session_state.patient_data.items():
        st.markdown(f"**{k.strip()}**: {v.strip()}")

    if st.button("💡 Suggest Homeopathic Remedy"):
        with st.spinner("Thinking..."):
            summary_prompt = (
                "You are a homeopathic doctor. Based on the following symptoms, suggest the most appropriate remedy "
                "and explain your reasoning in a clear and simple way:\n\n"
            )
            for k, v in st.session_state.patient_data.items():
                summary_prompt += f"- {k.strip()}: {v.strip()}\n"
            suggestion = chatwithgemini(summary_prompt)

        st.subheader("🧾 Suggested Remedy")
        st.write(suggestion)

