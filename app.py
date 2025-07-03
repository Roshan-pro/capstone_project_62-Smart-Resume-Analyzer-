from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
import requests
import os
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
from Roshan_kumar557.calculate_similarity import SimplecalculateSimilarity,Similarity
from Roshan_kumar557.cleantext import SimpleCleanText,cleanText
from Roshan_kumar557.extract_text_from_pdf import ExtractText,simpleExtractTextPdf
from Roshan_kumar557.fetch_job import FindJobs,SimpleFetchJobsStrategy
from Roshan_kumar557.get_suggestion import SimpleResumeSuggestions,ResumeSuggestion
from dotenv import load_dotenv
load_dotenv()

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import pdfplumber
from sentence_transformers import SentenceTransformer, util
import torch
import secrets
import pickle
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Load models
model = SentenceTransformer('all-MiniLM-L6-v2')
with open('resume_category_model.pkl', 'rb') as f:
    category_model = pickle.load(f)
with open('tfidf_vectorizer.pkl', 'rb') as f:
    tfidf_vectorizer = pickle.load(f)


def get_keywords_for_category(category, skills_db):
    """
    Retrieves a combination of top job roles and important skills for a given category.
    """
    if category in skills_db:
        category_info = skills_db[category]
        job_roles = category_info.get("job_roles", [])
        expected_skills = category_info.get("expected_skills", [])

        # Combine roles and a few top skills for the query
        keywords = []
        if job_roles:
            keywords.append(job_roles[0]) # Take the primary job role
            if len(job_roles) > 1:
                keywords.append(job_roles[1]) # Take a secondary role if available

        # Add a few key skills (e.g., top 3-5)
        keywords.extend(expected_skills[:3])

        # Join them to form a comprehensive search query
        return ", ".join(keywords)
    return category # Fallback to just the category name if no specific info
def remove_double_asterisks(text):
    return text.replace("**", "")


def predict_resume_category(resume_text):
    X = tfidf_vectorizer.transform([resume_text])
    category = category_model.predict(X)[0]
    return category
# In main.py, near your other imports
import json
SKILLS_DB_PATH = 'skills_database.json'

# Function to load the skills database
def load_skills_database(filepath):
    """Loads the skills database from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found. Please create the skills database.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}. Check file format.")
        return {}

# Load the skills database when the app starts
skills_database = load_skills_database(SKILLS_DB_PATH)

# --- Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))

        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please login.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('upload_resume'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_resume():
    if request.method == 'POST':
        resume_file = request.files['resume']
        job_desc = request.form['job_description']

        if resume_file and job_desc:
            filename = secure_filename(resume_file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            resume_file.save(path)

            resume_text = ExtractText(simpleExtractTextPdf()).extractTextFromPdf(path)
            score = Similarity(SimplecalculateSimilarity(resume_text,job_desc)).calculate_similarity()
            suggestions = ResumeSuggestion(SimpleResumeSuggestions(resume_text,job_desc)).suggest()
            suggestions = remove_double_asterisks(suggestions)
            category = predict_resume_category(resume_text)
            # category = predict_resume_category(resume_text)
            print(f"Predicted category for job search: {category}") 

            # Generate a more specific job query based on the predicted category
            job_search_query = get_keywords_for_category(category, skills_database)
            if not job_search_query: # Fallback if category info is missing in DB
                # As a last resort, try to extract some keywords from the resume itself.
                # This would need a more robust NLP skill extraction method,
                # but a simple fallback is to use the predicted category.
                job_search_query = category
                print(f"Falling back to category name query: {job_search_query}")

            session['resume_text'] = resume_text
            session['job_description'] = job_desc

            # Fetch jobs using the refined query
            jobs = FindJobs(SimpleFetchJobsStrategy(job_search_query)).findJobs()

            matched_jobs = []
            for job in jobs:
                job_desc_api = job.get("job_description") or ""
                if not job_desc_api.strip():
                    continue  

                job_score = Similarity(SimplecalculateSimilarity(resume_text,job_desc_api)).calculate_similarity()

                # Compose location string safely
                job_city = job.get('job_city') or ''
                job_country = job.get('job_country') or ''
                location = ", ".join(filter(None, [job_city, job_country]))

                matched_jobs.append({
                    'title': job.get('job_title', 'N/A'),
                    'company': job.get('employer_name', 'N/A'),
                    'description': job_desc_api,
                    'location': location,
                    'score': job_score,
                    'job_apply_link': job.get('job_apply_link', '#') # Added job link
                })

            # Sort jobs by similarity score descending
            matched_jobs = sorted(matched_jobs, key=lambda x: x['score'], reverse=True)

            # Filter jobs with score >= 50 to ensure relevance
            filtered_jobs = [job for job in matched_jobs if job['score'] >= 50]

            if not filtered_jobs:
                flash("No jobs matched. Try improving your resume or trying again later.")

            return render_template('result.html', score=score, suggestions=suggestions, category=category, jobs=filtered_jobs, resume_text=resume_text)

    return render_template('upload.html')

from flask import send_file
import io

@app.route('/download_suggestions', methods=['POST'])
def download_suggestions():
    suggestions = request.form.get('suggestions', 'No suggestions available.')
    buffer = io.BytesIO()
    buffer.write(suggestions.encode('utf-8'))
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='text/plain',
        as_attachment=True,
        download_name='resume_suggestions.txt'
    )

@app.route('/search_jobs', methods=['POST'])
def search_jobs():
    resume_text = request.form.get('resume_text', session.get('resume_text', '')) # Get from form or session

    if not resume_text:
        flash("Please upload a resume first to search for jobs.")
        return redirect(url_for('upload_resume'))

    # Re-predict category and generate keywords for job search
    category_for_search = predict_resume_category(resume_text)
    job_search_query = get_keywords_for_category(category_for_search, skills_database)
    if not job_search_query:
        job_search_query = category_for_search # Fallback if no specific keywords

    jobs = FindJobs(SimpleFetchJobsStrategy(job_search_query)).findJobs()

    matched_jobs = []
    for job in jobs:
        job_desc_api = job.get("job_description") or ""
        if not job_desc_api.strip():
            continue

        score = Similarity(SimplecalculateSimilarity(resume_text,job_desc_api)).calculate_similarity()
        job_city = job.get('job_city') or ''
        job_country = job.get('job_country') or ''
        location = ", ".join(filter(None, [job_city, job_country]))

        matched_jobs.append({
            'title': job.get('job_title', 'N/A'),
            'company': job.get('employer_name', 'N/A'),
            'description': job.get('job_description', 'N/A'),
            'location': location,
            'score': score,
            'job_apply_link': job.get('job_apply_link', '#') # Added job link
        })

    matched_jobs = sorted(matched_jobs, key=lambda x: x['score'], reverse=True)
    filtered_jobs = [job for job in matched_jobs if job['score'] >= 50] # Filter for relevance

    if not filtered_jobs:
        flash("No jobs matched your resume with a score of 50% or higher. Try improving your resume or adjusting the job description you provided.")
        # Still render the template, so the flash message is displayed
    return render_template('job_results.html', jobs=filtered_jobs)

# --- Run App ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
