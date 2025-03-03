from flask import Blueprint, render_template, session, request, jsonify, redirect, url_for, flash
from routes.valid import login_required as role_required
from routes.mysql import get_db_connection
from flask_login import current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
import requests

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/dashboard', endpoint='user_dashboard')
@role_required('user')
def user_dashboard():
    # Mock weather data - replace with an actual API call later
    weather_data = {
        'location': 'Your City',
        'temperature': '25°C',
        'condition': 'Sunny',
        'humidity': '60%',
        'wind_speed': '10 km/h'
    }
    return render_template('users/user_dashboard.html',
                           username=session.get('username', 'Guest'),
                           weather_data=weather_data)

@bp.route('/profile')
@role_required('user')
def user_profile():
    return render_template('users/user_profile.html', user=current_user)

@bp.route('/reset-credentials', methods=['GET', 'POST'], endpoint='user_reset_credentials')
@role_required('user')
def user_reset_credentials():
    if request.method == 'POST':
        # Handle password reset logic here
        pass
    return render_template('users/user_reset_credentials.html')

@bp.route('/notifications')
@role_required('user')
def notifications():
    return render_template('users/notifications.html')

@bp.route('/main-room')
@role_required('user')
def main_room():
    return render_template('users/main_room.html')

@bp.route('/bedroom-1')
@role_required('user')
def bedroom_1():
    return render_template('users/bedroom_1.html')

@bp.route('/bedroom-2')
@role_required('user')
def bedroom_2():
    return render_template('users/bedroom_2.html')

@bp.route('/bedroom-3')
@role_required('user')
def bedroom_3():
    return render_template('users/bedroom_3.html')

@bp.route('/kitchen')
@role_required('user')
def kitchen():
    return render_template('users/kitchen.html')

@bp.route('/main-switch')
@role_required('user')
def main_switch():
    return render_template('users/main_switch.html')

@bp.route('/update-profile', methods=['POST'], endpoint='update_profile')
@role_required('user')
def update_profile():
    connection = get_db_connection()
    username = request.form.get('username')
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    profile_photo = request.files.get('profile_photo')

    # Perform validation checks
    if not current_user.check_password(current_password):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('user.user_profile'))

    if new_password and new_password != confirm_password:
        flash('New password and confirm password do not match', 'error')
        return redirect(url_for('user.user_profile'))

    # Update user fields
    current_user.username = username
    current_user.full_name = full_name
    current_user.email = email
    current_user.phone = phone

    if new_password:
        current_user.password = generate_password_hash(new_password)

    if profile_photo:
        # Save the uploaded profile photo
        filename = secure_filename(profile_photo.filename)
        profile_photo.save(os.path.join('uploads', filename))
        current_user.profile_photo = filename

    # Save the changes to the database
    connection.commit()

    flash('Profile updated successfully', 'success')
    return redirect(url_for('user.user_profile'))

@bp.route('/delete-profile', methods=['POST'], endpoint='delete_profile')
@role_required('user')
def delete_profile():
    user_id = session.get('id')
    password = request.form['password']
    # ... validate the password as needed ...

    connection = get_db_connection()
    if connection:
        with connection.cursor() as cursor:
            # Delete the user's profile from the database
            sql = "DELETE FROM users WHERE id=%s"
            cursor.execute(sql, (user_id,))
            connection.commit()

    # Clear the session and redirect to the login page
    session.clear()
    return redirect(url_for('auth.login'))

@bp.route('/search')
@role_required('user')
def search():
    query = request.args.get('query', '')
    # Add search logic here
    return render_template('users/search_results.html', query=query)
