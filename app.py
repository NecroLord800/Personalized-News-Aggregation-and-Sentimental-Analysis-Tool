from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from textblob import TextBlob
import sqlite3
import re
import random
import string
import os
from flask_session import Session  # Import Session

app = Flask(__name__)

# Configurations for the Flask app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_default_secret_key')
app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem for persistent sessions
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_FILE_DIR'] = './.flask_sessions'  # Optional, specify session storage location

Session(app)  # Initialize session with Flask-Session

DATABASE = 'user.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  password TEXT NOT NULL,
                  email TEXT NOT NULL,
                  preferences TEXT,
                  reset_token TEXT, 
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Validate username
        if len(username) < 3 or len(username) > 20:
            flash("Username must be between 3 and 20 characters.")
            return redirect(url_for('register'))

        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format.")
            return redirect(url_for('register'))

        # Check if password is strong enough
        if len(password) < 6:
            flash("Password must be at least 6 characters.")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db()
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', (username, hashed_password, email))
        conn.commit()
        conn.close()

        flash("Account created successfully! Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()

        if user:
            app.logger.debug(f"User Found: {user['username']}")
        else:
            app.logger.debug("User Not Found")

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Logged in successfully!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('login'))

    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("You need to log in first.")
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

# Forgot password functionality
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user:
            reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
            conn = get_db()
            conn.execute('UPDATE users SET reset_token = ? WHERE email = ?', (reset_token, email))
            conn.commit()
            conn.close()

            reset_url = url_for('reset_password', token=reset_token, _external=True)
            print(f"Password reset link: {reset_url}")
            flash("Password reset link has been sent to your email.", "success")
            return redirect(url_for('login'))
        else:
            flash("Email not found", "error")
    
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE reset_token = ?', (token,)).fetchone()
    conn.close()

    if not user:
        flash("Invalid or expired token", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form['password']
        hashed_password = generate_password_hash(new_password)
        conn = get_db()
        conn.execute('UPDATE users SET password = ?, reset_token = NULL WHERE reset_token = ?', (hashed_password, token))
        conn.commit()
        conn.close()

        flash("Password successfully reset. Please login with your new password.", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html')

@app.route("/api/dashboard")
def api_dashboard():
    dashboard_data = {
        "personalized_feed": [
            {"title": "Tech Advances in 2024", "category": "Technology", "sentiment": "Positive"},
            {"title": "Global Warming Crisis", "category": "Environment", "sentiment": "Negative"},
        ],
        "topic_popularity": {
            "Technology": 45,
            "Health": 30,
            "Politics": 25
        },
        "most_read_articles": [
            {"title": "Election Updates 2024", "read_count": 1200},
            {"title": "COVID-19 New Variants", "read_count": 950},
        ],
        "user_stats": {
            "articles_read": 120,
            "preferred_topics": ["Technology", "Health"]
        },
        "trending_topics": ["AI Innovations", "Climate Change"]
    }
    return jsonify(dashboard_data)

@app.route("/api/sentiment_trends")
def api_sentiment_trends():
    trends = [
        {"category": "Technology", "avg_score": 0.7},
        {"category": "Health", "avg_score": 0.3},
        {"category": "Politics", "avg_score": -0.2},
    ]
    return jsonify(trends)

@app.route("/api/heatmap_data")
def api_heatmap_data():
    heatmap_data = [
        {"topic": "AI", "positive": 70, "neutral": 20, "negative": 10},
        {"topic": "Climate", "positive": 40, "neutral": 30, "negative": 30},
    ]
    return jsonify(heatmap_data)

@app.route("/analyze_sentiment", methods=["POST"])
def analyze_sentiment_route():
    article = request.json.get("article")
    if not article:
        return jsonify({"error": "No article content provided"}), 400
    blob = TextBlob(article)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        sentiment = "Positive"
    elif polarity < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    return jsonify({"polarity": polarity, "sentiment": sentiment})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
