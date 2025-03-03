from functools import wraps
from flask import render_template, session, redirect, url_for, flash, request
import hashlib
from routes.mysql import get_db_connection

def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'loggedin' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('home.login'))
            
            if role and session.get('role') != role:
                flash('Access denied.', 'danger')
                return redirect(url_for('home.login'))
            
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper 

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def log_action(username, role, action):
    """Log user actions to the database"""
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO login_logs (username, role, ip_address, action)
                    VALUES (%s, %s, %s, %s)""",
                    (username, role, request.remote_addr, action)
                )
                connection.commit()
        finally:
            connection.close() 

def view_logs():
    connection = get_db_connection()
    logs = []
    try:
        if connection:
            with connection.cursor() as cursor:
                # Fetch all logs, including IP address and timestamp
                cursor.execute("SELECT id, username, action, ip_address, timestamp FROM login_logs")
                logs = cursor.fetchall()
    except Exception as e:
        flash(f"Error loading logs: {str(e)}", "danger")
    finally:
        if connection:
            connection.close()
    return logs
