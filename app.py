import streamlit as st
import base64
from pdf_processor import extract_text_from_pdf
from question_generator import generate_from_text, generate_from_topic
from evaluator import evaluate_answer
from answer_classifier import generate_ideal_answer

# Function to encode image to base64
def get_base64_of_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Load background image
bg_image_base64 = get_base64_of_image("assets/background.jpg")

# Custom CSS with background image
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_image_base64}");
        background-size: cover;
        background-position: center;
    }}
    .main-title {{
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        color: #4dabf7;
        padding: 10px;
        border-bottom: 2px solid #4dabf7;
    }}
    .sub-title {{
        font-size: 22px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #4dabf7;
    }}
    .stButton>button {{
        background-color: #4dabf7;
        color: #ffffff;
        font-size: 16px;
        font-weight: bold;
        border-radius: 10px;
        padding: 8px 16px;
    }}
    .stButton>button:hover {{
        background-color: #1b4965;
    }}
    .question-box {{
        background-color: rgba(44, 44, 44, 0.7); 
        padding: 10px;
        border-radius: 10px;
        border-left: 5px solid #4dabf7;
        margin-bottom: 10px;
        color: #ffffff;
        font-weight: bold;
    }}
    .answer-box {{
        background-color: #333333;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #555555;
    }}
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state["page"] = "home"
if "questions" not in st.session_state:
    st.session_state["questions"] = []
if "user_answers" not in st.session_state:
    st.session_state["user_answers"] = {}

# Page Navigation
if st.session_state["page"] == "home":
    st.markdown("<h1 class='main-title'>AI-Based Assessment System 📄🤖</h1>", unsafe_allow_html=True)

    num_questions = st.slider("Select number of questions:", min_value=1, max_value=20, value=5)
    st.session_state["num_questions"] = num_questions

    st.markdown("<h2 class='sub-title'>Enter a Topic for Question Generation</h2>", unsafe_allow_html=True)
    topic = st.text_input("Enter a topic:")

    if st.button("Generate Questions from Topic"):
        if topic:
            st.session_state["questions"] = generate_from_topic(topic, num_questions)
            st.session_state["page"] = "assessment"
            st.rerun()
        else:
            st.warning("Please enter a topic.")

    st.markdown("<h2 class='sub-title'>Generate Questions by Uploading a PDF</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file:
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())

        extracted_text = extract_text_from_pdf("temp.pdf")

        st.subheader("Extracted Text Preview:")
        st.text_area("Text from PDF", extracted_text[:2000], height=250)

        if st.button("Generate Questions from PDF"):
            st.session_state["questions"] = generate_from_text(extracted_text, num_questions)
            st.session_state["page"] = "assessment"
            st.rerun()

elif st.session_state["page"] == "assessment":
    st.markdown("<h1 class='main-title'>Answer the Questions Below</h1>", unsafe_allow_html=True)

    user_answers = {}
    
    if st.session_state["questions"]:
        for idx, question in enumerate(st.session_state["questions"]):
            st.markdown(f"<div class='question-box'><b>Question {idx+1}:</b> {question}</div>", unsafe_allow_html=True)
            user_answer = st.text_area(f"Enter your answer for Question {idx+1}:", key=f"answer_{idx}")
            user_answers[question] = user_answer
    else:
        st.warning("No questions generated. Please go back and try again.")

    if st.button("Submit Answers"):
        st.session_state["user_answers"] = user_answers
        st.session_state["page"] = "results"
        st.rerun()

elif st.session_state["page"] == "results":
    st.markdown("<h1 class='main-title'>Results & Feedback</h1>", unsafe_allow_html=True)

    if st.session_state["user_answers"]:
        for idx, (question, user_answer) in enumerate(st.session_state["user_answers"].items()):
            ideal_answer = generate_ideal_answer(question)
            score, feedback = evaluate_answer(user_answer, ideal_answer)

            st.markdown(f"<div class='question-box'><b>Question {idx+1}:</b> {question}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='answer-box'><b>Your Answer:</b> {user_answer}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='answer-box'><b>AI-Generated Ideal Answer:</b> {ideal_answer}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='answer-box'><b>Your Score:</b> {score}%</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='answer-box'><b>Feedback:</b> {feedback}</div>", unsafe_allow_html=True)
            st.write("---")
    else:
        st.warning("No answers submitted. Please try again.")

    if st.button("Start New Assessment"):
        st.session_state["page"] = "home"
        st.rerun()