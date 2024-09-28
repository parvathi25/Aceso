import streamlit as st
import random
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the Google Places API key from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set page config
st.set_page_config(page_title="Aceso AI Symptom Checker", page_icon="🏥", layout="centered")

# Define symptoms and diagnoses
symptoms = ['Fever', 'Cough', 'Headache', 'Fatigue', 'Nausea', 'Other']
diagnoses = ['Common Cold', 'Flu', 'Pneumonia', 'Allergies', 'Migraine']

# Function to get nearby doctors using Google Places API
def get_nearby_doctors(location):
    if not GOOGLE_API_KEY:
        raise ValueError("Google API Key not found. Please check your .env file.")
    
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    query = f"doctors OR hospitals near {location}"
    params = {
        "query": query,
        "key": GOOGLE_API_KEY,
        "type": "doctor|hospital"
    }
    response = requests.get(base_url, params=params)
    results = response.json().get("results", [])
    
    doctors = []
    for result in results[:3]:  # Limit to top 3 results
        name = result.get("name", "Unknown")
        address = result.get("formatted_address", "Address not available")
        doctors.append(f"{name} - {address}")
    
    return doctors

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'selected_symptoms' not in st.session_state:
    st.session_state.selected_symptoms = []

# Aceso AI avatar
st.image("https://via.placeholder.com/100x100.png?text=Aceso+AI", width=100)

# Title
st.title("Aceso AI Symptom Checker")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat steps
if st.session_state.step == 0:
    st.session_state.messages.append({"role": "assistant", "content": "Hello, I am Aceso, an AI-powered symptom checker chatbot. I can help find possible diagnoses for your symptoms and suggest nearby doctors. Please note that I am not a replacement for professional medical advice, and you should always consult a doctor for accurate diagnosis and treatment."})
    st.session_state.step = 1
    st.experimental_rerun()

elif st.session_state.step == 1:
    if "symptom_question_asked" not in st.session_state:
        st.session_state.messages.append({"role": "assistant", "content": "Great! What are your symptoms today? You can select multiple options."})
        st.session_state.symptom_question_asked = True
    
    selected_symptoms = st.multiselect("Select your symptoms:", symptoms, key="symptom_selector")
    
    if st.button("Submit Symptoms"):
        if selected_symptoms:
            st.session_state.selected_symptoms = selected_symptoms
            st.session_state.messages.append({"role": "user", "content": f"My symptoms: {', '.join(selected_symptoms)}"})
            st.session_state.step = 2
        else:
            st.warning("Please select at least one symptom.")
        st.experimental_rerun()

elif st.session_state.step == 2:
    random_diagnoses = random.sample(diagnoses, 3)
    diagnosis_message = "Based on your symptoms, here are some possible diagnoses: " + ", ".join(random_diagnoses)
    st.session_state.messages.append({"role": "assistant", "content": diagnosis_message})
    st.session_state.diagnosis = random_diagnoses[0]
    st.session_state.step = 3
    st.experimental_rerun()

elif st.session_state.step == 3:
    if "doctor_question_asked" not in st.session_state:
        st.session_state.messages.append({"role": "assistant", "content": "Would you like me to search for doctors or hospitals in your area?"})
        st.session_state.doctor_question_asked = True
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes"):
            st.session_state.step = 4
            st.experimental_rerun()
    with col2:
        if st.button("No"):
            st.session_state.messages.append({"role": "assistant", "content": "Thank you for using Aceso. Remember to consult with a healthcare professional for accurate diagnosis and treatment."})
            st.session_state.step = -1
            st.experimental_rerun()

elif st.session_state.step == 4:
    location = st.text_input("Please enter your location (city, state, or full address):")
    if st.button("Search"):
        if location:
            try:
                doctors = get_nearby_doctors(location)
                if doctors:
                    doctor_message = f"Here are some healthcare providers near {location}:\n\n" + "\n".join(doctors)
                else:
                    doctor_message = f"I couldn't find any healthcare providers near {location}. Please try a different location or broaden your search area."
                st.session_state.messages.append({"role": "assistant", "content": doctor_message})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"I'm sorry, there was an error searching for healthcare providers: {str(e)}"})
            finally:
                st.session_state.messages.append({"role": "assistant", "content": "Thank you for using Aceso. Remember to consult with a healthcare professional for accurate diagnosis and treatment."})
                st.session_state.step = -1
        else:
            st.warning("Please enter a location.")
        st.experimental_rerun()

# Add a reset button
if st.button("Start Over"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()