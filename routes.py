from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, db
from models import QuizSession, Question
from gemini_service import generate_quiz_questions
from datetime import datetime
import logging

@app.route('/')
def index():
    """Home page with quiz topic selection"""
    return render_template('index.html')

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    """Start a new quiz session"""
    try:
        student_name = request.form.get('student_name', '').strip()
        topic = request.form.get('topic', '').strip()
        num_questions = int(request.form.get('num_questions', 5))
        
        if not student_name or not topic:
            flash('Please provide both student name and topic', 'error')
            return redirect(url_for('index'))
        
        # Create new quiz session
        quiz_session = QuizSession(
            student_name=student_name,
            topic=topic,
            total_questions=num_questions
        )
        db.session.add(quiz_session)
        db.session.flush()  # Get the ID
        
        # Generate questions using Gemini API
        questions_data = generate_quiz_questions(topic, num_questions)
        
        # Save questions to database
        for i, q_data in enumerate(questions_data, 1):
            question = Question(
                quiz_session_id=quiz_session.id,
                question_text=q_data['question'],
                correct_answer=q_data['correct_answer'],
                question_number=i
            )
            question.set_options(q_data['options'])
            db.session.add(question)
        
        db.session.commit()
        
        # Store quiz session ID in session
        session['quiz_session_id'] = quiz_session.id
        session['current_question'] = 1
        
        return redirect(url_for('quiz'))
        
    except Exception as e:
        logging.error(f"Error starting quiz: {e}")
        flash('Error starting quiz. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/quiz')
def quiz():
    """Display current quiz question"""
    quiz_session_id = session.get('quiz_session_id')
    current_question_num = session.get('current_question', 1)
    
    if not quiz_session_id:
        flash('No active quiz session', 'error')
        return redirect(url_for('index'))
    
    quiz_session = QuizSession.query.get_or_404(quiz_session_id)
    question = Question.query.filter_by(
        quiz_session_id=quiz_session_id,
        question_number=current_question_num
    ).first()
    
    if not question:
        # Quiz completed
        return redirect(url_for('complete_quiz'))
    
    return render_template('quiz.html', 
                         quiz_session=quiz_session,
                         question=question,
                         current_question=current_question_num)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    """Submit answer for current question"""
    quiz_session_id = session.get('quiz_session_id')
    current_question_num = session.get('current_question', 1)
    answer = request.form.get('answer')
    
    if not quiz_session_id or not answer:
        flash('Invalid submission', 'error')
        return redirect(url_for('quiz'))
    
    # Find and update the question
    question = Question.query.filter_by(
        quiz_session_id=quiz_session_id,
        question_number=current_question_num
    ).first()
    
    if question:
        is_correct = question.check_answer(answer)
        db.session.commit()
        
        # Update quiz session score
        quiz_session = QuizSession.query.get(quiz_session_id)
        if is_correct:
            quiz_session.correct_answers += 1
        db.session.commit()
    
    # Move to next question
    session['current_question'] = current_question_num + 1
    
    return redirect(url_for('quiz'))

@app.route('/complete_quiz')
def complete_quiz():
    """Complete the quiz and show results"""
    quiz_session_id = session.get('quiz_session_id')
    
    if not quiz_session_id:
        flash('No active quiz session', 'error')
        return redirect(url_for('index'))
    
    quiz_session = QuizSession.query.get_or_404(quiz_session_id)
    quiz_session.end_time = datetime.utcnow()
    quiz_session.completed = True
    quiz_session.calculate_score()
    db.session.commit()
    
    # Clear session
    session.pop('quiz_session_id', None)
    session.pop('current_question', None)
    
    return redirect(url_for('results', session_id=quiz_session.id))

@app.route('/results/<int:session_id>')
def results(session_id):
    """Display quiz results"""
    quiz_session = QuizSession.query.get_or_404(session_id)
    questions = Question.query.filter_by(quiz_session_id=session_id).all()
    
    return render_template('results.html', 
                         quiz_session=quiz_session,
                         questions=questions)

@app.route('/history')
def history():
    """Display quiz history"""
    # Get all completed quiz sessions, ordered by most recent
    quiz_sessions = QuizSession.query.filter_by(completed=True).order_by(
        QuizSession.end_time.desc()
    ).all()
    
    return render_template('history.html', quiz_sessions=quiz_sessions)

@app.route('/api/performance_data/<int:session_id>')
def performance_data(session_id):
    """API endpoint for performance chart data"""
    quiz_session = QuizSession.query.get_or_404(session_id)
    questions = Question.query.filter_by(quiz_session_id=session_id).all()
    
    # Calculate performance metrics
    correct_count = quiz_session.correct_answers
    incorrect_count = quiz_session.total_questions - correct_count
    
    data = {
        'labels': ['Correct', 'Incorrect'],
        'data': [correct_count, incorrect_count],
        'backgroundColor': ['#28a745', '#dc3545'],
        'score_percentage': quiz_session.score_percentage,
        'duration_minutes': quiz_session.get_duration_minutes(),
        'total_questions': quiz_session.total_questions
    }
    
    return jsonify(data)
