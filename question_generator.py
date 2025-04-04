from transformers import T5ForConditionalGeneration, T5Tokenizer

# Load the model and tokenizer
MODEL_NAME = "google/flan-t5-large"
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME, legacy=False)
model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

def generate_questions(prompt, num_questions=5):
    """Generate unique, high-quality, and challenging questions based on the prompt."""
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    outputs = model.generate(
        input_ids,
        max_length=150,  # Allow longer, more detailed questions
        num_return_sequences=num_questions * 2,  # Generate extra for better filtering
        do_sample=True,
        temperature=0.9,  # Increase creativity
        top_p=0.85
    )
    questions = [tokenizer.decode(output, skip_special_tokens=True).strip() for output in outputs]

    # Filter and refine questions
    filtered_questions = list(set(filter(lambda q: len(q) > 20 and "?" in q, questions)))  # Ensure complexity
    unique_questions = list(set(filtered_questions))[:num_questions]  # Remove duplicates

    if not unique_questions:
        return ["No meaningful questions generated. Try refining your prompt."]
    
    return unique_questions

def generate_from_topic(topic, num_questions=5):
    """Generate **advanced** questions from a given topic."""
    prompt = (
        f"Generate {num_questions} highly technical, open-ended questions about '{topic}'. "
        "Ensure questions require deep understanding, problem-solving, and critical thinking. "
        "Focus on practical applications, theories, and algorithmic concepts. "
        "Avoid simple definitions and multiple-choice formats."
    )
    return generate_questions(prompt, num_questions)

def generate_from_text(text, num_questions=5):
    """Generate **difficult and thought-provoking** questions from provided text."""
    truncated_text = text[:1500]  # Extend context for better question depth
    prompt = (
        f"From the following content, generate {num_questions} expert-level questions:\n"
        f"{truncated_text}\n\n"
        "Ensure the questions test deep analytical skills and problem-solving ability. "
        "They should be application-driven and challenge the user's understanding."
    )
    return generate_questions(prompt, num_questions)

if __name__ == "__main__":
    try:
        choice = input("Enter '1' for topic-based or '2' for text-based questions: ")
        num_qs = int(input("Enter the number of questions: "))

        if choice == "1":
            topic = input("Enter the topic: ")
            questions = generate_from_topic(topic, num_qs)
        elif choice == "2":
            text = input("Enter text content: ")
            questions = generate_from_text(text, num_qs)
        else:
            raise ValueError("Invalid choice.")

        print("\nGenerated Questions:")
        for idx, question in enumerate(questions, 1):
            print(f"{idx}. {question}")

    except ValueError:
        print("Please enter a valid number.")
