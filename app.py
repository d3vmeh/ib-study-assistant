from flask import Flask, render_template, request, redirect, url_for
from question_database import QuestionBank, Question
import markdown2

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
        # Convert markdown to HTML if explanation exists
        if explanation:
            explanation = markdown2.markdown(explanation)
        return render_template('result.html', 
                             question=question, 
                             student_answer=student_answer, 
                             is_correct=is_correct,
                             explanation=explanation)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 