from flask import Blueprint, request, jsonify
import requests
from routes.valid import login_required
from routes.mysql import execute_query
import json

bp = Blueprint('esp', __name__)

ESP_CONFIG = {
    'IP': '192.168.31.210',  # ESP8266 IP
    'PORT': 80
}

def get_esp_url(endpoint):
    return f"http://{ESP_CONFIG['IP']}:{ESP_CONFIG['PORT']}/{endpoint}"

@bp.route('/esp/status', methods=['GET'])
@login_required()
def esp_status():
    try:
        response = requests.get(get_esp_url('get-status'), timeout=5)
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 503

@bp.route('/esp-toggle-device')
@login_required()
def esp_toggle_device():
    pin = request.args.get('pin')
    state = request.args.get('state')
    
    # Send request to ESP to toggle the device
    url = get_esp_url(f'toggle-device?pin={pin}&state={state}')
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return jsonify({'message': 'Device toggled successfully'})
        else:
            return jsonify({'error': 'Failed to toggle device'}), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 503

@bp.route('/esp-toggle-all-devices')
@login_required()
def esp_toggle_all_devices():
    state = request.args.get('state')
    
    # Send request to ESP to toggle all devices
    url = get_esp_url(f'toggle-all?state={state}')
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return jsonify({'message': 'All devices toggled successfully'})
        else:
            return jsonify({'error': 'Failed to toggle all devices'}), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 503

@bp.route('/esp/config', methods=['GET', 'POST'])
@login_required('admin')
def esp_config():
    if request.method == 'POST':
        data = request.get_json()
        ESP_CONFIG['IP'] = data.get('ip', ESP_CONFIG['IP'])
        ESP_CONFIG['PORT'] = data.get('port', ESP_CONFIG['PORT'])
        return jsonify({'message': 'Configuration updated'}), 200
    
    return jsonify(ESP_CONFIG), 200

@bp.route('/esp/logs', methods=['GET'])
@login_required()
def esp_logs():
    logs = execute_query("SELECT * FROM device_logs ORDER BY timestamp DESC LIMIT 100")
    return jsonify(logs or [])