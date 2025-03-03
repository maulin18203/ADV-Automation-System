from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.mysql import get_db_connection
from routes.valid import hash_password, log_action
import re
import smtplib
from email.mime.text import MIMEText

bp = Blueprint('home', __name__)

# @bp.route('/home')
# def home():
#     try:
#         return render_template('home/home.html')
#     except Exception as e:
#         flash(f"Error loading home page: {str(e)}", "danger")
#         return redirect(url_for('home.login'))
    
@bp.route('/')
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template('home/login.html')

        hashed_password = hash_password(password)
        ip_address = request.remote_addr

        connection = get_db_connection()
        try:
            if connection:
                with connection.cursor() as cursor:
                    # Check admin login
                    cursor.execute('SELECT * FROM admin WHERE username = %s', (username,))
                    admin = cursor.fetchone()
                    if admin and admin['password'] == hashed_password:
                        session['loggedin'] = True
                        session['username'] = admin['username']
                        session['role'] = 'admin'
                        session['id'] = admin['id']
                        log_action(username, 'admin', 'Admin login successful')
                        return redirect(url_for('admin.dashboard'))
                    
                    # Check user login
                    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
                    user = cursor.fetchone()
                    if user and user['password'] == hashed_password:
                        session['loggedin'] = True
                        session['username'] = user['username']
                        session['role'] = 'user'
                        session['id'] = user['id']
                        log_action(username, 'user', 'User login successful')
                        return redirect(url_for('user.user_dashboard'))
                    
                    log_action(username, 'unknown', 'Login failed - Invalid credentials')
                    flash("Invalid username or password.", "danger")
        except Exception as e:
            log_action(username, 'unknown', f'Login error: {str(e)}')
            flash(f"Error during login: {str(e)}", "danger")
        finally:
            if connection:
                connection.close()
    return render_template('home/login.html')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        full_name = request.form['full_name']

        # Add validation
        if not all([username, email, password, confirm_password, full_name]):
            flash("All fields are required.", "danger")
            return redirect(url_for('home.signup'))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('home.signup'))

        connection = get_db_connection()
        try:
            if connection:
                with connection.cursor() as cursor:
                    # Create users table if it doesn't exist
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            username VARCHAR(255) NOT NULL UNIQUE,
                            email VARCHAR(255) NOT NULL UNIQUE,
                            password VARCHAR(255) NOT NULL,
                            full_name VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    connection.commit()

                    # Check for existing user
                    cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", 
                                (username, email))
                    existing_user = cursor.fetchone()
                    if existing_user:
                        flash("Username or email already exists.", "danger")
                        return redirect(url_for('home.signup'))

                    # Create the user
                    hashed_password = hash_password(password)
                    cursor.execute("""
                        INSERT INTO users (username, email, password, full_name) 
                        VALUES (%s, %s, %s, %s)
                    """, (username, email, hashed_password, full_name))
                    connection.commit()
                    flash("Signup successful! You can now log in.", "success")
                    return redirect(url_for('home.login'))
        except Exception as e:
            flash(f"Error during signup: {str(e)}", "danger")
        finally:
            if connection:
                connection.close()

    return render_template('home/signup.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home.login'))

@bp.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            email = request.form.get('email')
            subject = request.form.get('subject')
            message = request.form.get('message')

            # Validate required fields
            if not all([name, email, subject, message]):
                flash('All fields are required.', 'danger')
                return redirect(url_for('home.contact_us'))

            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash('Please enter a valid email address.', 'danger')
                return redirect(url_for('home.contact_us'))

            # Connect to database
            connection = get_db_connection()
            try:
                with connection.cursor() as cursor:
                    sql = """INSERT INTO contacts 
                            (name, email, subject, message, created_at) 
                            VALUES (%s, %s, %s, %s, NOW())"""
                    cursor.execute(sql, (name, email, subject, message))
                    connection.commit()
                    
                    # Send email notification
                    send_notification_email(name, email, subject, message)
                    
                    flash("Thank you! Your message has been sent successfully.", "success")
                    return redirect(url_for('home.contact_us'))
            finally:
                connection.close()

        except Exception as e:
            flash("An error occurred while sending your message. Please try again later.", "danger")
            # Log the error (implement your logging mechanism)
            print(f"Contact form error: {str(e)}")
            return redirect(url_for('home.contact_us'))

    return render_template('home/contact_us.html')

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Add password reset logic here
        flash('If the email exists in our system, you will receive password reset instructions.', 'info')
        return redirect(url_for('home.login'))
    return render_template('home/forgot_password.html')

def send_notification_email(name, email, subject, message):
    sender = 'kalilinux18203@gmail.com'
    recipient = 'maulin18203@gmail.com'
    msg = MIMEText(f"Name: {name}\nEmail: {email}\nSubject: {subject}\nMessage: {message}")
    msg['Subject'] = 'New Contact Form Submission'
    msg['From'] = sender
    msg['To'] = recipient

    with smtplib.SMTP('smtp.example.com') as server:
        server.login('kalilinux18203@gmail.com', '9909618203')
        server.sendmail(sender, [recipient], msg.as_string())
