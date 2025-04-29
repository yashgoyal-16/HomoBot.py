import google.generativeai as genai

# 🔐 Configure Gemini
genai.configure(api_key="AIzaSyB3hYZ-n6HEIqgwlAtnKRhSnlr2aVTUQ8E")
model = genai.GenerativeModel("gemini-1.5-flash")

# 🔁 Toggle: True = with reasoning | False = clean user mode
use_reasoning = True

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
Never ask unnecessary or vague questions.
Once you have enough details, respond with:
✅ Thank you. I have enough details to suggest a remedy.
"""

# 🧠 Chat function
def chatwithgemini(prompt):
    response = model.generate_content(prompt)
    return response.text.strip()

# 🏥 Main bot function
def run_homeopathic_bot():
    conversation_history = []
    patient_data = {}

    print("👩‍⚕️ Homeopathic Doctor: Hello! Please describe your problem in your own words.")
    user_input = input("🧑 Patient: ")

    # Initial prompt setup
    conversation_history.append(f"System: {system_prompt.strip()}")
    conversation_history.append(f"Patient: {user_input}")
    patient_data["initial_complaint"] = user_input

    while True:
        # Combine history for prompt
        prompt = "\n".join(conversation_history) + "\nDoctor:"
        doctor_reply = chatwithgemini(prompt)
        print("\n👩‍⚕️ Doctor:", doctor_reply)

        if "✅" in doctor_reply:
            break

        user_input = input("\n🧑 Patient: ")
        conversation_history.append(f"Doctor: {doctor_reply}")
        conversation_history.append(f"Patient: {user_input}")

        # Store question/answer in structured data
        last_question = doctor_reply.split("❓ Question:")[-1].strip() if "❓ Question:" in doctor_reply else doctor_reply
        patient_data[last_question] = user_input

    print("\n📋 Final Extracted Patient Data:")
    for k, v in patient_data.items():
        print(f"- {k.strip()}: {v.strip()}")

    return patient_data


# 🚀 Run the bot
if __name__ == "__main__":
    run_homeopathic_bot()
