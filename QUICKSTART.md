# Quick Start Guide

Get your Quiz Generator app running in 5 minutes!

## Step 1: Backend Setup

Open a terminal and run:

```bash
cd backend

# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment (optional for demo mode)
cp .env.example .env
# Edit .env and add your Perplexity API key (or skip for demo mode)

# Start the backend
uvicorn main:app --reload --port 8000
```

Backend is now running at `http://localhost:8000`

## Step 2: Frontend Setup

Open a NEW terminal window and run:

```bash
cd frontend

# Install dependencies
npm install

# Start the frontend
npm run dev
```

Frontend is now running at `http://localhost:3000`

## Step 3: Use the App

1. Open your browser and go to `http://localhost:3000`
2. Upload a document (PDF, TXT, or DOCX) OR paste a URL
3. Click "Generate Quiz"
4. Answer the 5 questions
5. See your results!

## Using Shell Scripts (Mac/Linux)

You can also use the provided scripts:

```bash
# Terminal 1
./start-backend.sh

# Terminal 2
./start-frontend.sh
```

## Getting Perplexity API Key

1. Go to [perplexity.ai](https://www.perplexity.ai/)
2. Sign up for an account
3. Navigate to API settings
4. Generate an API key
5. Add it to `backend/.env`:
   ```
   PERPLEXITY_API_KEY=your_key_here
   ```
6. Restart the backend

## Troubleshooting

**Port already in use?**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

**Python dependencies not installing?**
- Make sure you're using Python 3.10+
- Try: `pip install --upgrade pip` first

**Frontend not connecting?**
- Make sure backend is running on port 8000
- Check the browser console for errors
- Verify CORS settings in `backend/main.py`

## Demo Mode

Without a Perplexity API key, the app runs in demo mode with sample questions. This is perfect for testing the app!

## Need Help?

Check the main [README.md](README.md) for detailed documentation.
