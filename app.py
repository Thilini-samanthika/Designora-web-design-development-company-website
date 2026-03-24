from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

import os
import re

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'designora-secret-key')

# DATABASE CONFIG
app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DB_NAME')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# APP / MAIL CONFIG

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'designora-secret-key')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
mysql = MySQL(app)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

oauth = OAuth(app)

# GOOGLE OAUTH
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# FACEBOOK OAUTH
facebook = oauth.register(
    name='facebook',
    client_id=os.getenv('FACEBOOK_CLIENT_ID'),
    client_secret=os.getenv('FACEBOOK_CLIENT_SECRET'),
    access_token_url='https://graph.facebook.com/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    api_base_url='https://graph.facebook.com/',
    client_kwargs={'scope': 'email public_profile'},
)

# HELPERS
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

# ROUTES

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


# GOOGLE LOGIN
@app.route('/login/google')
def login_google():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/google/callback')
def google_callback():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')

        if not user_info:
            resp = google.get('userinfo')
            user_info = resp.json()

        email = user_info.get('email')
        name = user_info.get('name', 'Google User')
        google_id = user_info.get('sub')

        if not email:
            flash('Google account email not available.', 'error')
            return redirect(url_for('signin'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if not user:
            random_password = generate_password_hash(os.urandom(24).hex())
            cur.execute(
                "INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
                (name, email, random_password)
            )
            mysql.connection.commit()

            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()

        cur.close()

        session['user_id'] = user['id']
        session['user_name'] = user['full_name']
        session['user_email'] = user['email']
        session['google_id'] = google_id

        flash(f"Welcome {user['full_name']}!", 'success')
        return redirect(url_for('home'))

    except Exception as e:
        flash(f'Google login failed: {str(e)}', 'error')
        return redirect(url_for('signin'))



# FACEBOOK LOGIN

@app.route('/login/facebook')
def login_facebook():
    redirect_uri = url_for('facebook_callback', _external=True)
    return facebook.authorize_redirect(redirect_uri)


@app.route('/facebook/callback')
def facebook_callback():
    try:
        token = facebook.authorize_access_token()
        resp = facebook.get('me?fields=id,name,email', token=token)
        profile = resp.json()

        email = profile.get('email')
        name = profile.get('name', 'Facebook User')
        facebook_id = profile.get('id')

        if not email:
            flash('Facebook email permission not granted. Please use Google login or normal sign in.', 'error')
            return redirect(url_for('signin'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if not user:
            random_password = generate_password_hash(os.urandom(24).hex())
            cur.execute(
                "INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
                (name, email, random_password)
            )
            mysql.connection.commit()

            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cur.fetchone()

        cur.close()

        session['user_id'] = user['id']
        session['user_name'] = user['full_name']
        session['user_email'] = user['email']
        session['facebook_id'] = facebook_id

        flash(f"Welcome {user['full_name']}!", 'success')
        return redirect(url_for('home'))

    except Exception as e:
        flash(f'Facebook login failed: {str(e)}', 'error')
        return redirect(url_for('signin'))


# REGISTER
@limiter.limit("3 per minute")
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

@limiter.limit("5 per minute")
@app.route('/login', methods=['POST'])
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


# FORGOT PASSWORD
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not email:
            flash('Please enter your email address.', 'error')
            return redirect(url_for('forgot_password'))

        try:
            validate_email(email)
        except EmailNotValidError:
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('forgot_password'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            token = serializer.dumps(user['email'], salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)

            msg = Message(
                'Password Reset Request',
                recipients=[user['email']]
            )
            msg.body = f"""Hello,

Click the link below to reset your password:

{reset_url}

This link will expire in 1 hour.

If you did not request this, please ignore this email.
"""
            mail.send(msg)

            flash('Password reset link has been sent to your email.', 'success')
            return redirect(url_for('signin'))
        else:
            flash('No account found with that email address.', 'error')
            return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')


# RESET PASSWORD
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception:
        flash('The reset link is invalid or has expired.', 'error')
        return redirect(url_for('forgot_password'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()

    if not user:
        cur.close()
        flash('User not found.', 'error')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not new_password or not confirm_password:
            cur.close()
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('reset_password', token=token))

        if new_password != confirm_password:
            cur.close()
            flash('Passwords do not match.', 'error')
            return redirect(url_for('reset_password', token=token))

        if not is_strong_password(new_password):
            cur.close()
            flash('Password must be at least 8 characters and include uppercase, lowercase, and a number.', 'error')
            return redirect(url_for('reset_password', token=token))

        hashed_password = generate_password_hash(new_password)

        cur.execute(
            "UPDATE users SET password = %s WHERE email = %s",
            (hashed_password, email)
        )
        mysql.connection.commit()
        cur.close()

        flash('Your password has been reset successfully. Please sign in.', 'success')
        return redirect(url_for('signin'))

    cur.close()
    return render_template('reset_password.html', token=token)


# CONTACT FORM
@limiter.limit("5 per minute")
@app.route('/contact', methods=['POST'])
def contact():
    try:
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        company = request.form.get('company', '').strip()
        contact_number = request.form.get('contact_number', '').strip()
        service_type = request.form.get('service_type', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not message:
            return jsonify({
                "success": False,
                "message": "Please fill in all required fields."
            })

        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({
                "success": False,
                "message": "Please enter a valid email address."
            })

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO project_inquiries
            (name, email, company, contact_number, service_type, message)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, email, company, contact_number, service_type, message))
        mysql.connection.commit()
        cur.close()

        owner_email = "designoraallcoluds@gmail.com"

        owner_msg = Message(
            subject="New Contact Inquiry - Designora",
            recipients=[owner_email]
        )
        owner_msg.body = f"""
New contact inquiry received from Designora website.

Name: {name}
Email: {email}
Company: {company if company else 'N/A'}
Contact Number: {contact_number if contact_number else 'N/A'}
Service Type: {service_type if service_type else 'N/A'}

Message:
{message}
"""
        mail.send(owner_msg)

        user_msg = Message(
            subject="We Received Your Message - Designora",
            recipients=[email]
        )
        user_msg.body = f"""
Hello {name},

Thank you for contacting Designora.

We have received your message successfully.
Our team will get back to you soon.

Submitted details:
Name: {name}
Email: {email}
Company: {company if company else 'N/A'}
Contact Number: {contact_number if contact_number else 'N/A'}
Service Type: {service_type if service_type else 'N/A'}

Message:
{message}

Best regards,
Designora Team
"""
        mail.send(user_msg)

        return jsonify({
            "success": True,
            "message": "Message sent successfully!"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
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

    owner_email = "designoraallcoluds@gmail.com"

    try:
        owner_msg = Message(
            subject="New Start Project Submission - Designora",
            recipients=[owner_email]
        )
        owner_msg.body = f"""
A new project order has been submitted on Designora website.

User ID: {session.get('user_id')}
Full Name: {full_name}
Email: {email}
Service Type: {service_type}
Budget: {budget if budget else 'N/A'}

Project Details:
{project_details}
"""
        mail.send(owner_msg)

        user_msg = Message(
            subject="Your Project Request Was Received - Designora",
            recipients=[email]
        )
        user_msg.body = f"""
Hello {full_name},

Thank you for starting your project with Designora.

We have received your project request successfully.
Our team will review your requirements and contact you soon.

Submitted details:
Full Name: {full_name}
Email: {email}
Service Type: {service_type}
Budget: {budget if budget else 'N/A'}

Project Details:
{project_details}

Best regards,
Designora Team
"""
        mail.send(user_msg)

    except Exception as e:
        print("Email sending error:", str(e))

    flash('Your project order has been submitted successfully.', 'success')
    return redirect(url_for('home'))

# RATE LIMIT ERROR
@app.errorhandler(429)
def ratelimit_handler(e):
    return "Too many attempts. Please try again later.", 429

# RUN APP

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)