import json
import logging
import os
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Dict

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "default_key"))

class QuizQuestion(BaseModel):
    question: str
    options: Dict[str, str]  # {"A": "option1", "B": "option2", etc.}
    correct_answer: str  # "A", "B", "C", or "D"
    explanation: str
    
    class Config:
        extra = "forbid"

class QuizResponse(BaseModel):
    questions: List[QuizQuestion]
    
    class Config:
        extra = "forbid"

def generate_quiz_questions(topic: str, num_questions: int = 5) -> List[Dict]:
    """
    Generate quiz questions for a given topic using Gemini API
    """
    try:
        system_prompt = (
            "You are an expert quiz generator. Create multiple-choice questions "
            "with exactly 4 options (A, B, C, D) for educational purposes. "
            "Each question should be clear, accurate, and at an appropriate difficulty level. "
            "Provide a brief explanation for the correct answer. "
            "Respond with JSON in the specified format."
        )
        
        user_prompt = (
            f"Generate {num_questions} multiple-choice questions about {topic}. "
            f"Each question should have exactly 4 options labeled A, B, C, and D. "
            f"Make sure the questions are educational and cover different aspects of the topic. "
            f"Format your response as JSON with this structure: "
            f'{{"questions": [{{"question": "text", "options": {{"A": "option1", "B": "option2", "C": "option3", "D": "option4"}}, "correct_answer": "A", "explanation": "why A is correct"}}]}}'
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=user_prompt)])
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
            ),
        )

        raw_json = response.text
        logging.info(f"Raw JSON response: {raw_json}")

        if raw_json:
            data = json.loads(raw_json)
            
            # Extract questions directly from JSON response
            questions = []
            if 'questions' in data and isinstance(data['questions'], list):
                for q_data in data['questions']:
                    questions.append({
                        'question': q_data.get('question', ''),
                        'options': q_data.get('options', {}),
                        'correct_answer': q_data.get('correct_answer', 'A'),
                        'explanation': q_data.get('explanation', 'No explanation provided')
                    })
            
            return questions
        else:
            raise ValueError("Empty response from Gemini API")

    except Exception as e:
        logging.error(f"Failed to generate quiz questions: {e}")
        # Return sample fallback questions
        return get_fallback_questions(topic, num_questions)

def get_fallback_questions(topic: str, num_questions: int) -> List[Dict]:
    """
    Fallback questions when Gemini API fails
    """
    fallback = [
        {
            'question': f'This is a sample question about {topic}. What is the primary focus of this topic?',
            'options': {
                'A': 'Understanding basic concepts',
                'B': 'Advanced applications only',
                'C': 'Historical context only',
                'D': 'None of the above'
            },
            'correct_answer': 'A',
            'explanation': 'Understanding basic concepts is typically the foundation of any subject.'
        }
    ]
    
    # Repeat the fallback question with slight variations
    questions = []
    for i in range(min(num_questions, 5)):
        question = fallback[0].copy()
        question['question'] = f'Question {i+1}: ' + question['question']
        questions.append(question)
    
    return questions
