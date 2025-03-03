from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from routes.valid import hash_password, login_required, log_action
from routes.mysql import get_db_connection

bp = Blueprint('admin', __name__, url_prefix='/admin')

def get_connected_devices_count():
    # Implement the logic to fetch the count of connected devices
    # For example, query the database or use an external API
    # Return the count as an integer
    return 42  # Placeholder value

def get_active_users_count():
    # Implement the logic to fetch the count of active users
    # For example, query the database or use an external API
    # Return the count as an integer
    return 10  # Placeholder value

def get_energy_consumption():
    # Implement the logic to fetch the energy consumption data
    # For example, query the database or use an external API
    # Return the energy consumption value
    return 1500  # Placeholder value

def get_system_temperature():
    # Implement the logic to fetch the system temperature
    # For example, query the database or use an external API
    # Return the system temperature value
    return 25  # Placeholder value

def get_network_status():
    # Implement the logic to fetch the network status
    # For example, query the database or use an external API
    # Return the network status as a string
    return "Online"  # Placeholder value

def get_battery_usage():
    # Implement the logic to fetch the battery usage
    # For example, query the database or use an external API
    # Return the battery usage as a percentage
    return 80  # Placeholder value

def get_latest_login():
    # Implement the logic to fetch the latest login timestamp
    # For example, query the database or use an external API
    # Return the latest login timestamp as a string
    return "2023-06-01 10:30:00"  # Placeholder value

def get_recent_devices():
    # Implement the logic to fetch the recently added devices
    # For example, query the database or use an external API
    # Return the list of recently added devices
    return ["Device 1", "Device 2", "Device 3"]  # Placeholder value

def get_system_alerts():
    # Implement the logic to fetch the system alerts
    # For example, query the database or use an external API
    # Return the list of system alerts
    return ["Alert 1", "Alert 2", "Alert 3"]  # Placeholder value

def get_energy_consumption_data():
    # Implement the logic to fetch the energy consumption data for the chart
    # For example, query the database or use an external API
    # Return the energy consumption data as a dictionary
    return {
        "labels": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "values": [12, 19, 3, 5, 2, 3, 9]
    }  # Placeholder value

@bp.route('/dashboard')
@login_required('admin')
def dashboard():
    # Fetch dashboard data from the database or other sources
    dashboard_data = {
        'connected_devices': get_connected_devices_count(),
        'active_users': get_active_users_count(),
        'energy_consumption': get_energy_consumption(),
        'system_temperature': get_system_temperature(),
        'network_status': get_network_status(),
        'battery_usage': get_battery_usage(),
        'latest_login': get_latest_login(),
        'recent_devices': get_recent_devices(),
        'system_alerts': get_system_alerts(),
        'energy_consumption_data': get_energy_consumption_data()
    }
    return render_template('admin/admin_dashboard.html', dashboard_data=dashboard_data)

@bp.route('/user-management')
@login_required('admin')
def user_management():
    connection = get_db_connection()
    users = []
    admins = []
    try:
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, username, full_name, email, phone FROM users")
                users = cursor.fetchall()
                cursor.execute("SELECT id, username, full_name, email, phone FROM admin")
                admins = cursor.fetchall()
    finally:
        if connection:
            connection.close()
    return render_template('admin/user_management.html', users=users, admins=admins)

# Optional: Endpoint for AJAX data retrieval
@bp.route('/user_management/get_all_users')
@login_required('admin')
def get_all_users():
    connection = get_db_connection()
    users = []
    admins = []
    try:
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, username, full_name, email, phone FROM users")
                users = cursor.fetchall()
                cursor.execute("SELECT id, username, full_name, email, phone FROM admin")
                admins = cursor.fetchall()
    finally:
        if connection:
            connection.close()
    return {
        "success": True,
        "data": {
            "users": users,
            "admins": admins
        }
    }

@bp.route('/device-management')
@login_required('admin')
def device_management():
    return render_template('admin/device_management.html')

@bp.route('/logs')
@login_required('admin')
def logs():
    connection = get_db_connection()
    logs = []
    try:
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, username, action, ip_address, timestamp FROM login_logs")
                logs = cursor.fetchall()
    finally:
        if connection:
            connection.close()
    return render_template('admin/logs.html', logs=logs)

@bp.route('/notifications')
@login_required('admin')
def notifications():
    connection = get_db_connection()
    contact_requests = []
    try:
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, username, email, message, timestamp FROM contacts")
                contact_requests = cursor.fetchall()
    finally:
        if connection:
            connection.close()
    return render_template('admin/admin_notifications.html', contact_requests=contact_requests)

@bp.route('/settings', methods=['GET', 'POST'])
@login_required('admin')
def settings():
    if request.method == 'POST':
        # Handle form submission and save settings
        pass

    # Fetch settings from the database or configuration
    settings = {
        "system_name": "My System",
        "notification_level": "all",
        "theme": "light",
        "font_size": 14,
        "maintenance_mode": False,
        "two_factor": False,
        "api_key": "your-api-key",
        "enable_logging": True
    }

    return render_template('admin/settings.html', settings=settings)

@bp.route('/reports')
@login_required('admin')
def reports():
    return render_template('admin/reports.html')

@bp.route('/profile')
@login_required('admin')
def profile():
    # Check if admin_id is in session
    if 'admin_id' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('home.login'))

    admin_id = session['admin_id']
    connection = get_db_connection()
    admin = None
    try:
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, username, full_name, email FROM admin WHERE id = %s", (admin_id,))
                admin = cursor.fetchone()
                if admin:
                    admin = {
                        'id': admin[0],
                        'username': admin[1],
                        'full_name': admin[2],
                        'email': admin[3]
                    }
    finally:
        if connection:
            connection.close()
    return render_template('admin/admin_profile.html', admin=admin)

@bp.route('/update_profile', methods=['POST'])
@login_required('admin')
def update_profile():
    admin_id = session['admin_id']
    full_name = request.form.get('full_name')
    email = request.form.get('email')

    connection = get_db_connection()
    try:
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE admin SET full_name = %s, email = %s WHERE id = %s", (full_name, email, admin_id))
            connection.commit()
    finally:
        if connection:
            connection.close()

    return jsonify(success=True)

@bp.route('/delete_profile', methods=['POST'])
@login_required('admin')
def delete_profile():
    admin_id = session['admin_id']

    connection = get_db_connection()
    try:
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM admin WHERE id = %s", (admin_id,))
            connection.commit()
            session.clear()
    finally:
        if connection:
            connection.close()

    return jsonify(success=True)

@bp.route('/reset_credentials', methods=['GET', 'POST'])
@login_required('admin')
def reset_credentials():
    if request.method == 'POST':
        # Handle password reset logic here
        pass
    return render_template('admin/admin_reset_credentials.html')

@bp.route('/search')
@login_required('admin')
def search():
    query = request.args.get('query', '')
    # Add search logic here
    return render_template('admin/search_results.html', query=query)

@bp.route('/monitoring')
@login_required('admin')
def monitoring():
    return render_template('admin/monitoring.html')

@bp.route('/privacy')
@login_required('admin')
def privacy():
    return render_template('admin/privacy.html')

# Add other admin routes as needed


@bp.route('/add_user', methods=['GET', 'POST'])
@login_required('admin')
def add_user():
    connection = get_db_connection()
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')

        # Hash the password
        hashed_password = hash_password(password)
        
        try:
            with connection.cursor() as cursor:
                # Insert new user with role 'user'
                cursor.execute("""
                    INSERT INTO users (username, password, full_name, email, phone, role)
                    VALUES (%s, %s, %s, %s, %s, 'user')
                """, (username, hashed_password, full_name, email, phone))
                connection.commit()
            flash("User added successfully.", "success")
        except Exception as e:
            flash(f"Error adding user: {str(e)}", "danger")
        finally:
            connection.close()
        return redirect(url_for('admin.user_management'))
    else:
        return render_template('admin/add_user.html')
    
@bp.route('/view_user/<int:id>')
@login_required('admin')
def view_user(id):
    connection = get_db_connection()
    user = None
    try:
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
                user = cursor.fetchone()
    finally:
        if connection:
            connection.close()
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('admin.user_management'))
    return render_template('admin/view_user.html', profile=user, role='user')

@bp.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required('admin')
def edit_user(id):
    connection = get_db_connection()
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        # You can add additional fields if needed
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE users SET full_name=%s, email=%s, phone=%s WHERE id=%s
                """, (full_name, email, phone, id))
                connection.commit()
            flash("User updated successfully.", "success")
        except Exception as e:
            flash(f"Error updating user: {str(e)}", "danger")
        finally:
            connection.close()
        return redirect(url_for('admin.view_user', id=id))
    else:
        user = None
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
                user = cursor.fetchone()
        finally:
            connection.close()
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for('admin.user_management'))
        return render_template('admin/edit_user.html', user=user)

@bp.route('/delete_user/<int:id>', methods=['POST'])
@login_required('admin')
def delete_user(id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (id,))
            connection.commit()
    except Exception as e:
        flash(f"Error deleting user: {str(e)}", "danger")
        return redirect(url_for('admin.user_management'))
    finally:
        connection.close()
    flash("User deleted successfully.", "success")
    return redirect(url_for('admin.user_management'))

# ---------- Admin Account Endpoints (from "admin" table) ----------

@bp.route('/view_admin/<int:id>')
@login_required('admin')
def view_admin(id):
    connection = get_db_connection()
    admin_profile = None
    try:
        if connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM admin WHERE id = %s", (id,))
                admin_profile = cursor.fetchone()
    finally:
        if connection:
            connection.close()
    if not admin_profile:
        flash("Admin profile not found.", "danger")
        return redirect(url_for('admin.user_management'))
    return render_template('admin/view_admin.html', profile=admin_profile, role='admin')

@bp.route('/delete_admin/<int:id>', methods=['POST'])
@login_required('admin')
def delete_admin(id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM admin WHERE id = %s", (id,))
            connection.commit()
    except Exception as e:
        flash(f"Error deleting admin: {str(e)}", "danger")
        return redirect(url_for('admin.user_management'))
    finally:
        connection.close()
    flash("Admin deleted successfully.", "success")
    return redirect(url_for('admin.user_management'))