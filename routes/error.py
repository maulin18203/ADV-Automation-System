from flask import Blueprint, render_template

bp = Blueprint('error', __name__)

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('error/error.html', error_code=404), 404

@bp.app_errorhandler(500)
def internal_error(error):
    return render_template('error/error.html', error_code=500), 500

@bp.app_errorhandler(403)
def forbidden_error(error):
    return render_template('error/error.html', error_code=403), 403

@bp.app_errorhandler(401)
def unauthorized_error(error):
    return render_template('error/error.html', error_code=401), 401

@bp.app_errorhandler(400)
def bad_request_error(error):
    return render_template('error/error.html', error_code=400), 400

@bp.app_errorhandler(503)
def service_unavailable_error(error):
    return render_template('error/error.html', error_code=503), 503

@bp.app_errorhandler(408)
def request_timeout_error(error):
    return render_template('error/error.html', error_code=408), 408

@bp.app_errorhandler(405)
def method_not_allowed_error(error):
    return render_template('error/error.html', error_code=405), 405

@bp.app_errorhandler(409)
def conflict_error(error):
    return render_template('error/error.html', error_code=409), 409

@bp.app_errorhandler(413)
def payload_too_large_error(error):
    return render_template('error/error.html', error_code=413), 413
