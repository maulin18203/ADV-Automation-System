//USER.JS
function toggleSwitch(deviceId, state) {
    var statusElement = document.getElementById(deviceId);

    if (state === 'on') {
        statusElement.textContent = 'ON';
        statusElement.classList.remove('status-red');
        statusElement.classList.add('status-green');
    } else if (state === 'off') {
        statusElement.textContent = 'OFF';
        statusElement.classList.remove('status-green');
        statusElement.classList.add('status-red');
    }
}
