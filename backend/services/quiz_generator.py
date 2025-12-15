import os
import httpx
import json
from models.quiz import QuizResponse, Question


class QuizGenerator:
    """
    Generates quiz questions using Perplexity API
    """

    def __init__(self):
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            print("WARNING: PERPLEXITY_API_KEY not set. Using demo mode.")
        self.base_url = "https://api.perplexity.ai/chat/completions"
        # Try different model names in order
        self.models_to_try = [
            "sonar",
            "sonar-small-chat",
            "llama-3.1-sonar-small-128k-chat",
            "llama-3.1-8b-instruct"
        ]

    async def generate_quiz(self, content: str) -> QuizResponse:
        """
        Generate a 5-question MCQ quiz from the provided content
        """
        if not self.api_key:
            print("❌ No API key found")
            raise ValueError("API key not configured. Please set PERPLEXITY_API_KEY environment variable.")

        print(f"✓ Using Perplexity API to generate quiz from {len(content)} characters of content")

        prompt = self._create_prompt(content)

        # Try different models until one works
        for model_name in self.models_to_try:
            try:
                print(f"🔄 Trying model: {model_name}")

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.base_url,
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model_name,
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You are an expert educator and quiz creator. Your specialty is creating thoughtful, content-specific questions that test real understanding. Always generate questions about the ACTUAL CONTENT provided, never about meta-information. Return ONLY valid JSON without any markdown formatting or code blocks."
                                },
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            "temperature": 0.8,
                            "max_tokens": 3000
                        },
                        timeout=30.0
                    )

                    if response.status_code == 200:
                        result = response.json()
                        quiz_text = result['choices'][0]['message']['content']
                        print(f"✓ Successfully using model: {model_name}")
                        print(f"✓ Received response from Perplexity API")

                        quiz_text = quiz_text.strip()
                        if quiz_text.startswith('```json'):
                            quiz_text = quiz_text[7:]
                        if quiz_text.startswith('```'):
                            quiz_text = quiz_text[3:]
                        if quiz_text.endswith('```'):
                            quiz_text = quiz_text[:-3]
                        quiz_text = quiz_text.strip()

                        quiz_data = json.loads(quiz_text)
                        print(f"✓ Successfully generated {len(quiz_data['questions'])} questions")

                        return QuizResponse(**quiz_data)
                    else:
                        error_detail = response.text
                        print(f"❌ Model {model_name} failed ({response.status_code}): {error_detail[:200]}")
                        continue

            except Exception as e:
                print(f"❌ Model {model_name} error: {str(e)[:200]}")
                continue

        # If all models failed, raise an error
        print(f"❌ All models failed to generate quiz")
        raise ValueError("Could not generate quiz. Please try again later.")

    def _create_prompt(self, content: str) -> str:
        """
        Create a prompt for the AI model
        """
        # Clean up the content first
        content = ' '.join(content.split())  # Remove extra whitespace

        # Limit to 2500 characters for the content portion (leaving room for the prompt instructions)
        max_content_length = 2500
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
            print(f"📝 Content truncated to {max_content_length} characters for API efficiency")

        return f"""You are an expert educator creating a comprehensive quiz. Read the following content carefully and create exactly 5 multiple-choice questions that test deep understanding of the KEY FACTS, CONCEPTS, and DETAILS mentioned in the content.

IMPORTANT: Your questions MUST be about the SPECIFIC INFORMATION in the content below. DO NOT ask generic questions about the document format or meta-information.

Content to analyze:
{content}

Generate the questions in the following JSON format:
{{
    "questions": [
        {{
            "id": 1,
            "question": "Question text here?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correctAnswer": 0
        }}
    ]
}}

Requirements:
1. Each question MUST test knowledge of SPECIFIC FACTS, CONCEPTS, or DETAILS from the content above
2. Questions should cover different key points or sections from the content
3. Make questions clear and unambiguous
4. Each question must have exactly 4 distinct options
5. Include plausible wrong answers that someone who didn't read carefully might choose
6. correctAnswer is the index (0-3) of the correct option
7. Vary difficulty: include 2 easy, 2 medium, and 1 challenging question
8. Return ONLY valid JSON without any markdown formatting, code blocks, or additional text

Examples of GOOD questions (specific to content):
- "According to the document, what year was [specific event] mentioned?"
- "What is the main purpose of [specific concept mentioned]?"
- "Which of the following best describes [specific term from content]?"

Examples of BAD questions (avoid these):
- "What format is this document?"
- "How long is the content?"
- "What type of file was uploaded?"

Now create 5 questions based ONLY on the specific information in the content provided above."""

    def _generate_demo_quiz(self, content: str) -> QuizResponse:
        """
        Generate a demo quiz when API key is not available
        """
        return QuizResponse(
            questions=[
                Question(
                    id=1,
                    question="What is the main topic of the provided content?",
                    options=[
                        "Technology",
                        "Science",
                        "History",
                        "General Knowledge"
                    ],
                    correctAnswer=3
                ),
                Question(
                    id=2,
                    question="How many words approximately are in the content?",
                    options=[
                        f"About {len(content.split()) // 4} words",
                        f"About {len(content.split()) // 2} words",
                        f"About {len(content.split())} words",
                        f"About {len(content.split()) * 2} words"
                    ],
                    correctAnswer=2
                ),
                Question(
                    id=3,
                    question="What format was the content provided in?",
                    options=[
                        "Document or URL",
                        "Audio file",
                        "Video file",
                        "Image file"
                    ],
                    correctAnswer=0
                ),
                Question(
                    id=4,
                    question="This is a demo quiz. What should you do to get real questions?",
                    options=[
                        "Nothing, this is perfect",
                        "Add a PERPLEXITY_API_KEY to .env file",
                        "Restart the computer",
                        "Wait for an hour"
                    ],
                    correctAnswer=1
                ),
                Question(
                    id=5,
                    question="How many questions are in this quiz?",
                    options=[
                        "3 questions",
                        "4 questions",
                        "5 questions",
                        "6 questions"
                    ],
                    correctAnswer=2
                )
            ]
        )
