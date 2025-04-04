import streamlit as st
from sentence_transformers import SentenceTransformer, util
import torch

# Load similarity model
similarity_model = SentenceTransformer("all-MiniLM-L6-v2")

def evaluate_answer(user_answer, ideal_answer):
    """Compare user answer with AI-generated ideal answer and return a percentage score and feedback."""
    if not user_answer or not user_answer.strip():  
        return 0.0, "No answer provided. Please enter a response."

    user_embedding = similarity_model.encode(user_answer, convert_to_tensor=True)
    ideal_embedding = similarity_model.encode(ideal_answer, convert_to_tensor=True)

    # Compute cosine similarity (0 = no match, 1 = perfect match)
    similarity_score = util.pytorch_cos_sim(user_embedding, ideal_embedding).item()

    # Convert to percentage (0-100%)
    percentage_score = round(similarity_score * 100, 2)

    # Generate feedback based on score
    if percentage_score > 85:
        feedback = "Excellent! Your answer is very accurate."
    elif percentage_score > 70:
        feedback = "Good job! Your answer is mostly correct, but could use more details."
    elif percentage_score > 50:
        feedback = "Fair attempt. Your answer is somewhat correct but lacks key points."
    else:
        feedback = "Needs improvement. Your answer is not well-aligned with the ideal answer."

    return percentage_score, feedback

# Streamlit UI
st.title("AI-Based Answer Evaluation System")

# Input fields
user_answer = st.text_area("Your Answer", "")
ideal_answer = st.text_area("Ideal Answer", "")

# Evaluate button
if st.button("Evaluate Answer"):
    score, feedback = evaluate_answer(user_answer, ideal_answer)
    st.write(f"### Score: {score}%")
    st.write(f"### Feedback: {feedback}")

# Check CUDA availability
if st.checkbox("Show CUDA Info"):
    st.write("CUDA Available:", torch.cuda.is_available())
    st.write("Device:", torch.device("cuda" if torch.cuda.is_available() else "cpu"))
