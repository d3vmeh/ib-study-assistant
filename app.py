from flask import Flask, render_template, request, jsonify, render_template_string, url_for
from question_database import QuestionBank, Question
import markdown2
from querying import get_chat_response, grade_frq_response
from config import SUBJECTS_AND_TOPICS
import os

app = Flask(__name__, static_folder='static')
question_bank = QuestionBank()

@app.route('/')
def index():
    return render_template('index.html',
                         questions=question_bank.questions,
                         subjects=list(SUBJECTS_AND_TOPICS.keys()),
                         topics_by_subject=SUBJECTS_AND_TOPICS)

@app.route('/answer/<question_id>', methods=['POST'])
def submit_answer(question_id):
    data = request.json
    answer = data.get('answer')
    
    question = next((q for q in question_bank.questions if q.id == question_id), None)
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    if question.is_multiple_choice():
        is_correct = answer.upper() == question.answer.upper()
        return jsonify({
            'is_correct': is_correct,
            'feedback': 'Correct!' if is_correct else 'Incorrect. Try again.'
        })
    else:
        context = f"""
        Question: {question.question_text}
        Correct Answer: {question.answer}
        Markscheme: {question.markscheme}

        Please evaluate the student's answer based on the markscheme and provide detailed feedback.
        """
        
        feedback = grade_frq_response(context, answer)
        print(feedback)
        # Add this interaction to chat history
        question.add_to_chat_history("Student", f"Submitted answer: {answer}")
        question.add_to_chat_history("You", feedback)
        
        return jsonify({
            'explanation': feedback
        })

@app.route('/chat/<question_id>', methods=['POST'])
def chat(question_id):
    data = request.json
    message = data.get('message')
    
    question = next((q for q in question_bank.questions if q.id == question_id), None)
    if not question or not message:
        return jsonify({'error': 'Invalid request'}), 400

    # Add message to chat history
    question.add_to_chat_history("Student", message)
    
    answer_options = "This is a free response question, so no answer options are provided."
    if question.question_type == "mcq":
        answer_options = question.options
        
    context = f"""
    Question: {question.question_text}
    Answer Options: {answer_options}
    Markscheme: {question.markscheme}
    
    Chat History:
    {question.chat_history}
    """


    response = get_chat_response(context, data['message'], image_name = question.id)
    # Add AI response to chat history
    question.add_to_chat_history("AI", response)
    
    return jsonify({'response': response})

@app.route('/clear-chat/<question_id>', methods=['POST'])
def clear_chat(question_id):
    question = next((q for q in question_bank.questions if q.id == question_id), None)
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    question.clear_chat_history()
    return jsonify({'status': 'success'})

@app.route('/filter_questions', methods=['POST'])
def filter_questions():
    data = request.json
    subject = data.get('subject')
    topics = data.get('topics', [])
    
    print(f"Filtering - Subject: {subject}, Topics: {topics}")  # Debug log
    
    filtered_questions = question_bank.questions
    
    if subject:
        filtered_questions = [q for q in filtered_questions if q.subject == subject]
        print(f"After subject filter: {len(filtered_questions)} questions")  # Debug log
    
    if topics:
        filtered_questions = [q for q in filtered_questions if q.topic in topics]
        print(f"After topic filter: {len(filtered_questions)} questions")  # Debug log
    
    # Sort questions by ID
    filtered_questions.sort(key=lambda q: q.id)
    
    # Debug log
    print(f"Returning {len(filtered_questions)} questions")
    for q in filtered_questions:
        print(f"- {q.id}: {q.subject} - {q.topic}")
    
    questions_html = render_template('question_cards.html', questions=filtered_questions)
    return jsonify({'html': questions_html})

@app.route('/markscheme/<question_id>')
def get_markscheme(question_id):
    question = next((q for q in question_bank.questions if q.id == question_id), None)
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    return jsonify({
        'markscheme': question.markscheme
    })

if __name__ == '__main__':
    app.run(debug=True) 