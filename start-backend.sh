#!/bin/bash

echo "Starting Quiz Generator Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copy .env.example to .env and add your API key."
    echo "Running in demo mode..."
fi

echo "Backend starting on http://localhost:8000"
uvicorn main:app --reload --port 8000
