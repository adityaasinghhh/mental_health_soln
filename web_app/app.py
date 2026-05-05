from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
import json
from datetime import datetime
from models import db, User, Assessment

nltk.download('vader_lexicon', quiet=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mental_health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

CORS(app)
vader = SentimentIntensityAnalyzer()

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

PSYCHOMETRIC_QUESTIONS = [
    {"text": "I feel nervous or anxious frequently", "category": "anxiety"},
    {"text": "I worry too much about different things", "category": "anxiety"},
    {"text": "I find it hard to relax", "category": "anxiety"},
    {"text": "I feel restless or on edge", "category": "anxiety"},
    {"text": "I feel sad or down most of the time", "category": "depression"},
    {"text": "I have lost interest in activities I used to enjoy", "category": "depression"},
    {"text": "I feel hopeless about the future", "category": "depression"},
    {"text": "I feel worthless or guilty", "category": "depression"},
    {"text": "I feel overwhelmed by responsibilities", "category": "stress"},
    {"text": "I find it hard to concentrate", "category": "stress"},
    {"text": "I get irritated easily", "category": "stress"},
    {"text": "I feel mentally exhausted", "category": "stress"},
    {"text": "I have trouble sleeping", "category": "general"},
    {"text": "I wake up feeling tired", "category": "general"},
    {"text": "I feel low on energy throughout the day", "category": "general"},
    {"text": "I avoid social interactions", "category": "general"}
]

NLP_QUESTIONS = [
    {"text": "How have you been feeling over the past 2 weeks?", "category": "Mood"},
    {"text": "What thoughts or worries keep running through your mind?", "category": "Cognition"},
    {"text": "How has your sleep and energy level been?", "category": "Physical"},
    {"text": "How are you managing your daily responsibilities?", "category": "Coping"},
    {"text": "What do you see or feel when you think about your future?", "category": "Outlook"}
]

def interpret_score(score):
    if score <= 8: return "Low"
    elif score <= 12: return "Mild"
    elif score <= 16: return "Moderate"
    else: return "High"

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username exists'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email registered'}), 400
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return jsonify({'success': True, 'redirect': '/dashboard'})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')
        remember = data.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True, 'redirect': '/dashboard'})
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/assessment')
@login_required
def assessment():
    return render_template('assessment.html')

@app.route('/api/user/stats')
@login_required
def get_user_stats():
    assessments = Assessment.query.filter_by(user_id=current_user.id).all()
    
    if not assessments:
        return jsonify({'has_data': False})
    
    latest = assessments[0]
    total = len(assessments)
    
    avg_anxiety = sum(a.anxiety_score or 0 for a in assessments) / total
    avg_depression = sum(a.depression_score or 0 for a in assessments) / total
    avg_stress = sum(a.stress_score or 0 for a in assessments) / total
    
    trend = 'stable'
    if len(assessments) > 1:
        if latest.total_score < assessments[1].total_score:
            trend = 'improving'
        elif latest.total_score > assessments[1].total_score:
            trend = 'declining'
    
    return jsonify({
        'has_data': True,
        'total_assessments': total,
        'latest': latest.to_dict(),
        'averages': {
            'anxiety': round(avg_anxiety, 1),
            'depression': round(avg_depression, 1),
            'stress': round(avg_stress, 1)
        },
        'trend': trend,
        'member_since': current_user.created_at.strftime('%B %Y')
    })

@app.route('/api/user/assessments')
@login_required
def get_user_assessments():
    assessments = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.assessment_date.desc()).all()
    return jsonify([a.to_dict() for a in assessments])

@app.route('/api/questions')
@login_required
def get_questions():
    return jsonify({
        'psychometric': PSYCHOMETRIC_QUESTIONS,
        'nlp': NLP_QUESTIONS
    })

@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.json
    psychometric_answers = data.get('psychometric', [])
    nlp_responses = data.get('nlp', [])
    
    scores = {"anxiety": 0, "depression": 0, "stress": 0, "general": 0}
    for i, answer in enumerate(psychometric_answers):
        if i < len(PSYCHOMETRIC_QUESTIONS):
            cat = PSYCHOMETRIC_QUESTIONS[i]['category']
            scores[cat] += answer
    
    total = sum(scores.values())
    if total < 40: overall = "Normal"
    elif total < 55: overall = "Mild"
    elif total < 70: overall = "Moderate"
    else: overall = "Severe"
    
    combined_text = " ".join(nlp_responses)
    vader_scores = vader.polarity_scores(combined_text)
    blob = TextBlob(combined_text)
    nlp_score = vader_scores['compound']
    
    if nlp_score >= 0.5: tone = "Positive/Resilient"
    elif nlp_score >= 0.05: tone = "Stable"
    elif nlp_score <= -0.5: tone = "High Distress"
    elif nlp_score <= -0.05: tone = "Struggling"
    else: tone = "Neutral"
    
    assessment = Assessment(
        user_id=current_user.id,
        anxiety_score=scores['anxiety'],
        depression_score=scores['depression'],
        stress_score=scores['stress'],
        general_score=scores['general'],
        total_score=total,
        overall_status=overall,
        nlp_sentiment_score=nlp_score,
        nlp_sentiment_tone=tone,
        nlp_subjectivity=blob.sentiment.subjectivity,
        nlp_polarity=blob.sentiment.polarity,
        combined_status=overall,
        psychometric_responses=json.dumps(psychometric_answers),
        nlp_responses=json.dumps(nlp_responses)
    )
    db.session.add(assessment)
    db.session.commit()
    
    recommendations = {
        'crisis': overall == "Severe" and nlp_score <= -0.7,
        'exercises': [],
        'lifestyle_tips': [],
        'resources': [
            {"name": "Helplines", "items": ["988 Lifeline", "Crisis Text: HOME to 741741"]},
            {"name": "Apps", "items": ["Calm", "Headspace", "BetterHelp"]}
        ]
    }
    
    if nlp_score <= -0.5:
        recommendations['exercises'].append("4-7-8 Breathing technique")
        recommendations['exercises'].append("5-minute journaling")
    
    if scores['anxiety'] >= 12:
        recommendations['exercises'].append("Deep breathing exercises")
    elif scores['anxiety'] >= 8:
        recommendations['lifestyle_tips'].append("Take short breaks during stressful tasks")
    
    if scores['depression'] >= 12:
        recommendations['exercises'].append("Daily journaling")
    elif scores['depression'] >= 8:
        recommendations['lifestyle_tips'].append("Get morning sunlight")
    
    return jsonify({
        'psychometric': {
            'scores': scores,
            'results': {k: {'score': v, 'level': interpret_score(v)} for k, v in scores.items()},
            'total': total,
            'overall_status': overall
        },
        'nlp': {
            'score': nlp_score,
            'tone': tone,
            'subjectivity': blob.sentiment.subjectivity,
            'polarity': blob.sentiment.polarity,
            'vader_scores': vader_scores
        },
        'combined': {'status': overall},
        'recommendations': recommendations,
        'assessment_id': assessment.id
    })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)