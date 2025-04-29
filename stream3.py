import streamlit as st
import google.generativeai as genai

# 🔐 Configure Gemini API Key
genai.configure(api_key="AIzaSyB3hYZ-n6HEIqgwlAtnKRhSnlr2aVTUQ8E")
model = genai.GenerativeModel("gemini-1.5-flash")

# 📄 System Prompt with Reasoning Option
show_reasoning = st.sidebar.checkbox("Show Reasoning", value=True)

# Reasoning logic in the system prompt
if show_reasoning:
    system_prompt = """
You are a homeopathic doctor. Ask the patient relevant, focused questions in a simple, friendly, and easy-to-understand tone. 
If necessary, explain why you are asking each question, but only when it's important. 
Gather just enough information to suggest the right remedy. Avoid unnecessary questions.
Once you have enough details, say: "I have enough information to suggest a remedy."
"""
else:
    system_prompt = """
You are a homeopathic doctor. Ask the patient relevant, focused questions in a simple, friendly tone. 
Keep the questions easy to understand. Once you feel you have enough information, say: "I have enough information to suggest a remedy."
"""

# Function to interact with Gemini API
def chatwithgemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize session state if it does not exist
if "conversation" not in st.session_state:
    st.session_state.conversation = [f"System: {system_prompt.strip()}"]
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
if "patient_data" not in st.session_state:
    st.session_state.patient_data = {}
if "done" not in st.session_state:
    st.session_state.done = False

# 🏥 Streamlit Interface
st.title("💊 Homeopathic Doctor Chatbot")
st.markdown("Please briefly describe your symptoms. I'll ask a few important questions to understand your case better.")

# Text Input for user symptoms
user_input = st.chat_input("Your response...")

# Handle user input and get the next question from the chatbot
if user_input and not st.session_state.done:
    with st.chat_message("user"):
        st.write(user_input)
    
    st.session_state.conversation.append(f"Patient: {user_input}")

    # Save the user's response to the session state
    if st.session_state.chat_log:
        last_reply = st.session_state.chat_log[-1]
        question = last_reply.strip()
        st.session_state.patient_data[question] = user_input
    else:
        st.session_state.patient_data["Initial complaint"] = user_input

    # Form the prompt for the bot to generate the next response
    prompt = "\n".join(st.session_state.conversation) + "\nDoctor:"
    doctor_reply = chatwithgemini(prompt)

    # Store the bot's response and show it
    st.session_state.chat_log.append(doctor_reply)
    st.session_state.conversation.append(f"Doctor: {doctor_reply}")
    
    with st.chat_message("assistant"):
        st.markdown(doctor_reply)

    # Check if the bot has gathered enough information
    if "I have enough information" in doctor_reply:
        st.session_state.done = True
        st.success("Done collecting symptoms. Click below to view the summary or suggest a remedy.")

# Show the collected patient data and allow for remedy suggestion
if st.session_state.done:
    st.subheader("📋 Collected Patient Data")
    for k, v in st.session_state.patient_data.items():
        st.markdown(f"**{k.strip()}**: {v.strip()}")

    # Button to suggest a remedy
    if st.button("💡 Suggest Homeopathic Remedy"):
        with st.spinner("Thinking..."):
            summary_prompt = (
                "You are a homeopathic doctor. Based on the following symptoms, suggest the most appropriate remedy "
                "and explain your reasoning clearly and simply:\n\n"
            )
            for k, v in st.session_state.patient_data.items():
                summary_prompt += f"- {k.strip()}: {v.strip()}\n"
            suggestion = chatwithgemini(summary_prompt)

        st.subheader("🧾 Suggested Remedy")
        st.write(suggestion)
