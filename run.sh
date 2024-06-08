#!/bin/bash

# Define the path to the dummy directory
DUMMY_DIR="$(pwd)/dummy_dir"

# Function to start the HTTP server
start_http_server() {
    cd "$DUMMY_DIR"
    python3 -m http.server 8000 --bind 0.0.0.0 &
    HTTP_SERVER_PID=$!
    cd -  # Return to the original directory
}

# Function to stop the HTTP server
stop_http_server() {
    if [ ! -z "$HTTP_SERVER_PID" ]; then
        echo "Stopping HTTP server..."
        kill $HTTP_SERVER_PID
        wait $HTTP_SERVER_PID 2>/dev/null
        unset HTTP_SERVER_PID  # Clear the PID after stopping the server
    fi
}

# Start the HTTP server
start_http_server

# Run the bot in a loop
until python3 -B -m bot; do
    echo "Bot crashed with exit code $?. Respawning.." >&2
    sleep 3
    stop_http_server  # Ensure the current HTTP server is stopped
    start_http_server  # Restart the HTTP server
done