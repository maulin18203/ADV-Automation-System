from flask import Blueprint, jsonify
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (RuntimeError, ImportError):
    GPIO_AVAILABLE = False
    print("GPIO module not available. Running in simulation mode.")

bp = Blueprint('gpio', __name__)

class GPIOController:
    def __init__(self):
        self.DEVICE_PINS = {
            'bedroom1_light': 32,
            'bedroom1_fan': 36,
            'bedroom1_ac': 37,
            'bedroom1_tv': 38,
            'bedroom1_geyser': 40
        }
        self.init_gpio()

    def init_gpio(self):
        """Initialize GPIO settings"""
        if GPIO_AVAILABLE:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)  # Set pin numbering mode to BCM
            for pin in self.DEVICE_PINS.values():
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)

    def cleanup_gpio(self):
        """Cleanup GPIO settings"""
        if GPIO_AVAILABLE:
            GPIO.cleanup()

    def toggle_device(self, device, state):
        if device in self.DEVICE_PINS:
            pin = self.DEVICE_PINS[device]
            if state == 'on':
                GPIO.output(pin, GPIO.LOW)  # Low is ON for most configurations
            elif state == 'off':
                GPIO.output(pin, GPIO.HIGH)  # High is OFF for most configurations
            else:
                return jsonify({"message": "Invalid state."}), 400
            return jsonify({"message": f"{device} turned {state}."})
        else:
            return jsonify({"message": "Invalid device."}), 400

    def toggle_all_devices(self, state):
        if state == 'on':
            for pin in self.DEVICE_PINS.values():
                GPIO.output(pin, GPIO.LOW)
            return jsonify({"message": "All devices turned on."})
        elif state == 'off':
            for pin in self.DEVICE_PINS.values():
                GPIO.output(pin, GPIO.HIGH)
            return jsonify({"message": "All devices turned off."})
        else:
            return jsonify({"message": "Invalid state."}), 400

    def get_device_status(self, device=None):
        if not GPIO_AVAILABLE:
            return jsonify({"message": "GPIO module not available."}), 503

        if device:
            if device in self.DEVICE_PINS:
                pin = self.DEVICE_PINS[device]
                status = 'on' if GPIO.input(pin) == GPIO.LOW else 'off'
                return jsonify({"status": status})
            else:
                return jsonify({"message": "Invalid device."}), 400
        else:
            status = {}
            for device, pin in self.DEVICE_PINS.items():
                status[device] = 'on' if GPIO.input(pin) == GPIO.LOW else 'off'
            return jsonify(status)

gpio_controller = GPIOController()

@bp.route('/toggle-device/<device>/<state>', methods=['GET'])
def route_toggle_device(device, state):
    return gpio_controller.toggle_device(device, state)

@bp.route('/toggle-all-devices/<state>', methods=['GET'])
def route_toggle_all_devices(state):
    return gpio_controller.toggle_all_devices(state)

@bp.route('/get-all-device-status', methods=['GET'])
@bp.route('/get-device-status/<device>', methods=['GET'])
def route_get_device_status(device=None):
    return gpio_controller.get_device_status(device) 