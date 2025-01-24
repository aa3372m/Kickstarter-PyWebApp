#!/bin/bash

# Function to check if port is in use
check_port() {
    local port=$1
    if netstat -an | grep "LISTEN" | grep -q "\.${port}[[:space:]]"; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Default Flask port
PORT=5000

# Check if port is in use
if check_port $PORT; then
    echo "Port $PORT is currently in use."
    echo "Would you like to:"
    echo "1) Kill the process using port $PORT"
    echo "2) Use a different port"
    echo "3) Exit"
    read -p "Enter your choice (1-3): " choice

    case $choice in
        1)
            echo "Killing process on port $PORT..."
            kill -9 $(lsof -ti :$PORT)
            sleep 2  # Wait for the port to be freed
            ;;
        2)
            read -p "Enter new port number: " PORT
            ;;
        3)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid choice. Exiting..."
            exit 1
            ;;
    esac
fi

# Source conda.sh to enable conda activate
#source ~/anaconda3/etc/profile.d/conda.sh

# Activate conda environment and start Flask
# conda activate kickstarter101 && \
# export FLASK_APP=run.py && \
#export FLASK_ENV=development && \
#export FLASK_DEBUG=1 && \
#flask run --port $PORT 

conda activate kickstarter101 && export FLASK_APP=run.py && export FLASK_ENV=development && export FLASK_DEBUG=1 && flask run