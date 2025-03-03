from flask import Flask, jsonify, request
from routes import admin, user, home, error, esp, mysql, valid, get_db_config, init_db, view_logs
import os

try:
    import RPi.GPIO as GPIO
except (RuntimeError, ImportError):
    import mock  # Mock the GPIO module
    GPIO = mock.Mock()
    print("GPIO module unavailable: Running in mock mode")


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_key')

# Configure MySQL
app.config.update(get_db_config())

# Initialize database
init_db()

# Register blueprints
app.register_blueprint(admin)
app.register_blueprint(user)
app.register_blueprint(home)
app.register_blueprint(error)
app.register_blueprint(esp)
# app.register_blueprint(gpio_bp)  # Uncomment if you want to use the GPIO blueprint

# Initialize GPIO pins if available
if GPIO:
    GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
    GPIO_PINS = [32, 36, 37, 38, 40]
    for pin in GPIO_PINS:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)

@app.route('/')
def index():
    return "Welcome to the GPIO Control App!"


@app.route('/toggle-device/<device>/<state>', methods=['GET'])
def toggle_device(device, state):
    # Map device names to GPIO pins
    device_to_pin = {
        'bedroom1_light': 32,
        'bedroom1_fan': 36,
        'bedroom1_geyser': 37,
        'bedroom1_ac': 38,
        'bedroom1_tv': 40,
    }

    if device not in device_to_pin:
        return jsonify({"message": "Invalid device."}), 400

    pin = device_to_pin[device]

    if state == 'on':
        GPIO.output(pin, GPIO.LOW)  # Low is ON for most configurations
    elif state == 'off':
        GPIO.output(pin, GPIO.HIGH)  # High is OFF for most configurations
    else:
        return jsonify({"message": "Invalid state. Use 'on' or 'off'."}), 400

    return jsonify({"message": f"{device} turned {state}."})


@app.route('/toggle-all-devices/<state>', methods=['GET'])
def toggle_all_devices(state):
    if state not in ['on', 'off']:
        return jsonify({"message": "Invalid state. Use 'on' or 'off'."}), 400
    for pin in GPIO_PINS:
        if state == 'on':
            GPIO.output(pin, GPIO.LOW)
        else:
            GPIO.output(pin, GPIO.HIGH)

    return jsonify({"message": f"All devices turned {state}."})

@app.route('/get-all-device-status', methods=['GET'])
def get_all_device_status():
    status = {}
    for pin in GPIO_PINS:
        status[pin] = 'on' if GPIO.input(pin) == GPIO.LOW else 'off'
    return jsonify(status)

@app.route('/get-device-status/<device>', methods=['GET'])
def get_device_status(device):
    # Device to pin mapping
    device_mapping = {
        'bedroom1_light': 32,
        'bedroom1_fan': 36,
        'bedroom1_geyser': 37,
        'bedroom1_ac': 38,
        'bedroom1_tv': 40,
          # Just an example, adjust accordingly
    }

    if device not in device_mapping:
        return jsonify({"message": "Invalid device."}), 400

    pin = device_mapping[device]
    status = 'on' if GPIO.input(pin) == GPIO.LOW else 'off'
    return jsonify({"status": status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
