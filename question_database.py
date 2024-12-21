from dataclasses import dataclass
from typing import Optional, List, Dict, Union
import json
import os
from PIL import Image
from enum import Enum
from querying import grade_frq_response

@dataclass
class Question:
    id: str
    subject: str
    topic: str
    question_text: str
    answer: str 
    markscheme: str
    question_type: str = "frq"
    options: Optional[Dict[str, str]] = None  #for MCQs: {"A": "option text", "B": "option text", ...}
    image_path: Optional[str] = None
    difficulty: Optional[int] = None
    marks: Optional[int] = None
    chat_history: str = ""

    def add_to_chat_history(self, role: str, message: str):
        """Add a message to the chat history"""
        self.chat_history += f"{role}: {message}\n"

    def clear_chat_history(self):
        """Clear the chat history"""
        self.chat_history = ""
        
    def is_multiple_choice(self) -> bool:
        return self.question_type == "mcq"
    
    def get_options(self) -> Optional[Dict[str, str]]:
        if self.is_multiple_choice():
            return self.options
        return None
    
    #Checking if the answer entered/selected is correct
    def check_answer(self, student_answer: str) -> tuple[bool, Optional[str]]:
        """Returns a tuple of (is_correct: bool, explanation: Optional[str])"""
        if self.is_multiple_choice():
            is_correct = student_answer.upper() == self.answer.upper()
            return is_correct, None #no explanation needed for MCQs
        else:
            #FRQs -- get explanation from LLM
            context = f"""
                question: {self.question_text}
                markscheme: {self.markscheme}
                """
            explanation = grade_frq_response(context, student_answer)
            print(f"Explanation: {explanation}")
            return None, explanation

    def add_to_chat_history(self, role: str, message: str):
        """Add a message to the chat history"""
        self.chat_history += f"{role}: {message}\n"

    def clear_chat_history(self):
        """Clear the chat history"""
        self.chat_history = ""

class QuestionBank:
    def __init__(self):
        self.questions = []
        self.data_file = "questions/physics/physics_questions.json"
        self.image_dir = "question_images"
        self.load_questions()
    
    def load_questions(self):
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                print(f"Loaded data: {data}")
                for q in data:
                    question = Question(**q)
                    self.questions.append(question)
                print(f"Loaded {len(self.questions)} questions")
        except FileNotFoundError:
            print(f"Could not find file: {self.data_file}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from: {self.data_file}")
        except Exception as e:
            print(f"Error loading questions: {str(e)}")
    
    def save_questions(self):
        data = []
        for q in self.questions:
            data.append(q.__dict__)
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)

    def add_question_with_image(self, question: Question, image_path: Optional[str] = None):
        if image_path:
            image_filename = f"{question.id}_{os.path.basename(image_path)}"
            destination = os.path.join(self.image_dir, image_filename)

            with Image.open(image_path) as img:
                if img.width > 800:
                    ratio = 800 / img.width
                    new_size = (800, int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                img.save(destination)
            
            question.image_path = destination

        self.questions.append(question)
        self.save_questions()

    def get_questions_by_subject(self, subject: str) -> List[Question]:
        return [q for q in self.questions if q.subject.lower() == subject.lower()]
    
    def get_questions_by_topic(self, topic: str) -> List[Question]:
        return [q for q in self.questions if q.topic.lower() == topic.lower()]
    
    def get_questions_by_difficulty(self, difficulty: int) -> List[Question]:
        return [q for q in self.questions if q.difficulty == difficulty]
    
    def get_questions_by_marks(self, marks: int) -> List[Question]:
        return [q for q in self.questions if q.marks == marks]
    
    def delete_question(self, question_id: str):
        question = next((q for q in self.questions if q.id == question_id), None)
        if question and question.image_path and os.path.exists(question.image_path):
            os.remove(question.image_path)
        self.questions = [q for q in self.questions if q.id != question_id]
        self.save_questions()

    def import_questions_from_file(self, filepath: str):
        
        try:
            with open(filepath, 'r') as f:
                new_questions = json.load(f)
                imported_questions = [Question(**q) for q in new_questions]
                
                self.questions.extend(imported_questions)
                
                self.save_questions()
                
                return len(imported_questions)
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")
            return 0
        except json.JSONDecodeError:
            print(f"Error: File {filepath} is not valid JSON")
            return 0
        except Exception as e:
            print(f"Error importing questions: {str(e)}")
            return 0 
        
    def get_multiple_choice_questions(self) -> List[Question]:
        """Get all multiple choice questions"""
        return [q for q in self.questions if q.is_multiple_choice()]

    def get_free_response_questions(self) -> List[Question]:
        """Get all free response questions"""
        return [q for q in self.questions if not q.is_multiple_choice()]

    def clear_questions(self):
        """Clear all questions from the database and save empty state"""
        self.questions = []
        
        with open(self.data_file, 'w') as f:
            json.dump([], f)
        
        for file in os.listdir(self.image_dir):
            file_path = os.path.join(self.image_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

def main():
    
    qb = QuestionBank()
    print(f"Number of questions loaded: {len(qb.questions)}")
    for q in qb.questions:
        print(f"Question: {q.question_text}")

if __name__ == "__main__":
    main()
