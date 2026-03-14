from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import os
import re

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'designora-secret-key')

app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DB_NAME')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True

def is_valid_name(name):
    return len(name.strip()) >= 3 and len(name.strip()) <= 100

def is_safe_length(text, max_length):
    return len(text.strip()) <= max_length

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)
    
# Splash page
@app.route('/')
def splash():
    return render_template('splash.html')

# Home page after login
@app.route('/home')
def home():
    if 'user_id' not in session:
        flash('Please sign in first.', 'error')
        return redirect(url_for('signin'))
    return render_template('index.html', user_name=session.get('user_name'))

# Sign in page
@app.route('/signin')
def signin():
    return render_template('signin.html')

# Sign up page
@app.route('/signup')
def signup():
    return render_template('signup.html')

# REGISTER

@app.route('/register', methods=['POST'])
def register():
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()

    if not full_name or not email or not password or not confirm_password:
        flash('Please fill in all fields.', 'error')
        return redirect(url_for('signup'))

    if not is_valid_name(full_name):
        flash('Please enter a valid full name.', 'error')
        return redirect(url_for('signup'))

    if not is_safe_length(full_name, 100):
        flash('Name is too long.', 'error')
        return redirect(url_for('signup'))

    try:
        validate_email(email)
    except EmailNotValidError:
        flash('Please enter a valid email address.', 'error')
        return redirect(url_for('signup'))

    if password != confirm_password:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('signup'))

    if not is_strong_password(password):
        flash('Password must be at least 8 characters and include uppercase, lowercase, and a number.', 'error')
        return redirect(url_for('signup'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cur.fetchone()

    if existing_user:
        cur.close()
        flash('This email is already registered.', 'error')
        return redirect(url_for('signup'))

    hashed_password = generate_password_hash(password)

    cur.execute(
        "INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
        (full_name, email, hashed_password)
    )
    mysql.connection.commit()
    cur.close()

    flash('Account created successfully. Please sign in.', 'success')
    return redirect(url_for('signin'))

# LOGIN
@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()

    if not email or not password:
        flash('Please enter email and password.', 'error')
        return redirect(url_for('signin'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['user_name'] = user['full_name']
        session['user_email'] = user['email']
        flash(f"Welcome {user['full_name']}!", 'success')
        return redirect(url_for('home'))

    flash('Invalid email or password.', 'error')
    return redirect(url_for('signin'))

# LOGOUT

@app.route('/logout')
def logout():
    session.clear()
    flash('You have logged out successfully.', 'success')
    return redirect(url_for('splash'))

# CONTACT FORM
@app.route('/contact', methods=['POST'])
def contact():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({'success': False, 'message': 'Invalid request format.'}), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    company = data.get('company', '').strip()
    message = data.get('message', '').strip()

    if not name or not email or not message:
        return jsonify({'success': False, 'message': 'Please fill in all required fields.'}), 400

    if len(name) > 100 or len(email) > 100 or len(company) > 100 or len(message) > 1000:
        return jsonify({'success': False, 'message': 'Input is too long.'}), 400

    try:
        validate_email(email)
    except EmailNotValidError:
        return jsonify({'success': False, 'message': 'Invalid email address.'}), 400

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO contacts (name, email, company, message) VALUES (%s, %s, %s, %s)",
        (name, email, company, message)
    )
    mysql.connection.commit()
    cur.close()

    return jsonify({
        'success': True,
        'message': f'Thank you {name}! Your message has been received.'
    })

# START PROJECT / ORDER
@app.route('/start-project', methods=['POST'])
def start_project():
    if 'user_id' not in session:
        flash('Please sign in before placing an order.', 'error')
        return redirect(url_for('signin'))

    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip()
    service_type = request.form.get('service_type', '').strip()
    budget = request.form.get('budget', '').strip()
    project_details = request.form.get('project_details', '').strip()

    if not full_name or not email or not service_type or not project_details:
        flash('Please fill in all required project fields.', 'error')
        return redirect(url_for('home'))

    if len(full_name) > 100 or len(email) > 100 or len(service_type) > 100 or len(budget) > 100 or len(project_details) > 2000:
        flash('Project input is too long.', 'error')
        return redirect(url_for('home'))

    try:
        validate_email(email)
    except EmailNotValidError:
        flash('Please enter a valid email address.', 'error')
        return redirect(url_for('home'))

    cur = mysql.connection.cursor()
    cur.execute(
        """
        INSERT INTO project_orders (user_id, full_name, email, service_type, budget, project_details)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (session['user_id'], full_name, email, service_type, budget, project_details)
    )
    mysql.connection.commit()
    cur.close()

    flash('Your project order has been submitted successfully.', 'success')
    return redirect(url_for('home'))
@app.errorhandler(429)
def ratelimit_handler(e):
    return "Too many login attempts. Please try again later.", 429

# RUN APP
if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)