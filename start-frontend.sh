#!/bin/bash

echo "Starting Quiz Generator Frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Node modules not found. Installing dependencies..."
    npm install
fi

echo "Frontend starting on http://localhost:3000"
npm run dev
