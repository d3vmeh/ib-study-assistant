import json
from dataclasses import dataclass
from typing import Dict, Optional
import os

@dataclass
class Question:
    id: str
    subject: str
    topic: str
    question_text: str
    answer: str 
    markscheme: str
    question_type: str = "frq"
    options: Optional[Dict[str, str]] = None
    image_path: Optional[str] = None
    difficulty: Optional[int] = None
    marks: Optional[int] = None
    chat_history: str = ""

    def __post_init__(self):
        # Automatically set image path if an image exists for this question
        if not self.image_path:
            potential_image = f"{self.id}.jpg"
            if os.path.exists(os.path.join('static', 'question_images', potential_image)):
                self.image_path = potential_image

    def is_multiple_choice(self):
        return self.question_type == "mcq"

    def add_to_chat_history(self, role: str, message: str):
        """Add a message to the chat history"""
        self.chat_history += f"{role}: {message}\n"

    def clear_chat_history(self):
        """Clear the chat history"""
        self.chat_history = ""

    def check_answer(self, student_answer):
        """Check if the student's answer is correct"""
        if self.is_multiple_choice():
            return student_answer.upper() == self.answer.upper(), None
        else:
            # For free response questions, we'll use the LLM to evaluate
            from querying import evaluate_answer
            return evaluate_answer(self.question_text, self.answer, self.markscheme, student_answer)


class QuestionBank:
    def __init__(self):
        self.questions = []
        self.data_files = {
            "Physics": "questions/physics_questions.json",
            "Mathematics": "questions/math_questions.json",
            "Design Technology": "questions/design_tech_questions.json"
        }
        self.load_questions()

    def validate_question(self, question_data):
        """Validate that the question has required fields and valid subject/topic"""
        required_fields = ['id', 'subject', 'topic', 'question_text', 'answer', 'markscheme']
        
        # Check required fields
        if not all(field in question_data for field in required_fields):
            print(f"Missing required fields in question {question_data.get('id', 'unknown')}")
            return False
        
        # Check subject and topic validity
        subject = question_data.get('subject')
        topic = question_data.get('topic')
        
        if subject not in self.data_files:
            print(f"Invalid subject '{subject}' in question {question_data.get('id')}")
            return False
        
        return True

    def load_questions(self):
        total_loaded = 0
        for subject, file_path in self.data_files.items():
            try:
                with open(file_path, 'r') as f:
                    try:
                        questions_data = json.load(f)
                        subject_count = 0
                        for q in questions_data:
                            if self.validate_question(q):
                                question = Question(**q)
                                self.questions.append(question)
                                subject_count += 1
                        print(f"Loaded {subject_count} questions for {subject}")
                        total_loaded += subject_count
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON from {file_path}")
            except FileNotFoundError:
                print(f"Could not find file: {file_path}")
        print(f"Total questions loaded: {total_loaded}")
