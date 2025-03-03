#!/bin/bash

# Define the network interfaces (update if necessary)
INTERFACE="wlan0"  # Change to "eth0" for wired or use appropriate interface

# Log file for Flask history
ACCESS_LOG_FILE="flask_access.log"  # Log file for Flask access logs

# Get the IP address for localhost (127.0.0.1)
LOCALHOST_IP="127.0.0.1"
echo "Localhost IP: $LOCALHOST_IP"

# Get current IP address of the system (either dynamic or static) for wlan0 (or other interface)
CURRENT_IP=$(ip addr show $INTERFACE | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)

# Check if the IP address is successfully retrieved
if [ -z "$CURRENT_IP" ]; then
  echo "No IP address found for interface $INTERFACE."
  exit 1
else
  echo "Current IP address of $INTERFACE: $CURRENT_IP"
  FLASK_RUN_HOST=$CURRENT_IP
fi

# Start MariaDB with password
echo "18203" | sudo -S service mariadb start &> /dev/null &
mariadb_pid=$!
wait $mariadb_pid

if [ $? -eq 0 ]; then
  echo "MariaDB service started successfully."
else
  echo "Failed to start MariaDB service."
  exit 1
fi

# Function to check if a port is available
is_port_busy() {
  local port=$1
  netstat -tuln | grep -q ":$port"
}

# Function to find an available port dynamically
find_available_port() {
  for port in {1000..9000}; do
    if ! is_port_busy $port; then
      echo $port
      return
    fi
  done
  echo "No available ports found!"
  exit 1
}

# Function to clean up processes and close the port
cleanup() {
  echo "Stopping Flask and Chrome..."
  kill $flask_pid $chrome_pid &> /dev/null || true
  echo "Processes stopped."
  # Ensure the port is released
  if is_port_busy $port; then
    echo "Killing any remaining process on port $port"
    fuser -k $port/tcp
  fi
}

# Function to restart Flask on the same or next available port
restart_flask() {
  # First try to restart on the same port
  port=$(find_available_port)
  echo "Restarting Flask on port $port"
  
  flask run --debug --host=$FLASK_RUN_HOST -p $port 2>&1 | tee flask_error.log &
  flask_pid=$!
  sleep 2  # Wait briefly for Flask to initialize
  if ps -p $flask_pid > /dev/null; then
    echo "Flask restarted successfully on $FLASK_RUN_HOST:$port with PID $flask_pid"
  else
    echo "Failed to restart Flask on port $port. Check flask_error.log for details."
    cat flask_error.log
    exit 1
  fi

  # Open Chrome with the appropriate port
  google-chrome "http://127.0.0.1:$port" &> /dev/null &
  chrome_pid_1=$!
  if ps -p $chrome_pid_1 > /dev/null; then
    echo "Chrome opened successfully pointing to http://127.0.0.1:$port with PID $chrome_pid_1"
  else
    echo "Failed to open Chrome for localhost on port $port."
    exit 1
  fi

  google-chrome "http://$FLASK_RUN_HOST:$port" &> /dev/null &
  chrome_pid_2=$!
  if ps -p $chrome_pid_2 > /dev/null; then
    echo "Chrome opened successfully pointing to http://$FLASK_RUN_HOST:$port with PID $chrome_pid_2"
  else
    echo "Failed to open Chrome for $FLASK_RUN_HOST on port $port."
    exit 1
  fi
}

# Set trap to clean up on exit (when Ctrl+C is pressed)
trap cleanup EXIT

# Start Flask and Chrome
start_flask() {
  port=$(find_available_port)
  echo "Starting Flask on port $port"

  flask run --debug --host 0.0.0.0 -p $port 2>&1 | tee flask_error.log &
  flask_pid=$!
  sleep 2  # Wait briefly for Flask to initialize
  if ps -p $flask_pid > /dev/null; then
    echo "Flask started successfully on $FLASK_RUN_HOST:$port with PID $flask_pid"
    echo "Flask is running on:"
    echo "  - http://127.0.0.1:$port"
    echo "  - http://$FLASK_RUN_HOST:$port"
  else
    echo "Failed to start Flask on port $port. Check flask_error.log for details."
    cat flask_error.log
    exit 1
  fi

  # Open Chrome with both localhost (127.0.0.1) and the dynamic IP
  google-chrome "http://127.0.0.1:$port" &> /dev/null &
  chrome_pid_1=$!
  if ps -p $chrome_pid_1 > /dev/null; then
    echo "Chrome opened successfully pointing to http://127.0.0.1:$port with PID $chrome_pid_1"
  else
    echo "Failed to open Chrome for localhost on port $port."
    exit 1
  fi

  google-chrome "http://$FLASK_RUN_HOST:$port" &> /dev/null &
  chrome_pid_2=$!
  if ps -p $chrome_pid_2 > /dev/null; then
    echo "Chrome opened successfully pointing to http://$FLASK_RUN_HOST:$port with PID $chrome_pid_2"
  else
    echo "Failed to open Chrome for $FLASK_RUN_HOST on port $port."
    exit 1
  fi
}

# Start Flask and Chrome
start_flask

# Wait for Flask to finish (optional)
wait $flask_pid

# After Flask finishes, restart it if necessary
restart_flask
