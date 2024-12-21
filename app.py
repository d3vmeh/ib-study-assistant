from flask import Flask, render_template, request, jsonify
from question_database import QuestionBank, Question
import markdown2
from querying import get_chat_response

app = Flask(__name__)
question_bank = QuestionBank()

@app.route('/')
def index():
    questions = question_bank.questions
    return render_template('index.html', questions=questions)

@app.route('/answer/<question_id>', methods=['POST'])
def submit_answer(question_id):
    student_answer = request.form.get('answer')
    question = next((q for q in question_bank.questions if q.id == question_id), None)
    
    if question:
        is_correct, explanation = question.check_answer(student_answer)
        if explanation:
            explanation = markdown2.markdown(explanation)
        
        return jsonify({
            'is_correct': is_correct,
            'explanation': explanation
        })
    
    return jsonify({'error': 'Question not found'}), 404

@app.route('/chat/<question_id>', methods=['POST'])
def chat(question_id):
    data = request.json
    question = next((q for q in question_bank.questions if q.id == question_id), None)
    
    if question and data.get('message'):
        # Add student message to chat history
        question.add_to_chat_history("Student", data['message'])
        
        answer_options = "This is a free response question, so no answer options are provided."
        if question.question_type == "mcq":
            answer_options = question.get_options()
        
        context = f"""
        Question: {question.question_text}
        Answer Options: {answer_options}
        Markscheme: {question.markscheme}
        
        Chat History:
        {question.chat_history}
        """
        
        response = get_chat_response(context, data['message'])
        
        # Add AI response to chat history
        question.add_to_chat_history("You", response)
        
        response_html = markdown2.markdown(response)
        return jsonify({
            'response': response_html,
            'questionId': question_id
        })
    
    return jsonify({'error': 'Invalid request'}), 400

@app.route('/clear-chat/<question_id>', methods=['POST'])
def clear_chat(question_id):
    question = next((q for q in question_bank.questions if q.id == question_id), None)
    if question:
        question.clear_chat_history()
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Question not found'}), 404

if __name__ == '__main__':
    app.run(debug=True) 