import json
import logging
import os
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Dict

# Initialize Gemini client
api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyCSonrCzHrJZ8eYc8RrAq4gWrifk7ZshW8")
client = genai.Client(api_key=api_key)

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
            "You are an expert educator creating quiz questions for Class 10 students (age 15-16). "
            "Create multiple-choice questions with exactly 4 options (A, B, C, D). "
            "Questions should be at Class 10 curriculum level - challenging but appropriate. "
            "Each question must be educationally valuable, clear, and accurate. "
            "Always provide a detailed explanation for the correct answer. "
            "Respond with JSON in the specified format only."
        )
        
        user_prompt = (
            f"Generate {num_questions} multiple-choice questions about {topic} suitable for Class 10 students. "
            f"Each question should: "
            f"- Be at Class 10 difficulty level (age 15-16) "
            f"- Have exactly 4 options labeled A, B, C, and D "
            f"- Cover important concepts from the topic "
            f"- Include one clearly correct answer and three plausible distractors "
            f"- Be educational and curriculum-relevant "
            f"Format your response as JSON with this exact structure: "
            f'{{"questions": [{{"question": "question text here", "options": {{"A": "first option", "B": "second option", "C": "third option", "D": "fourth option"}}, "correct_answer": "A", "explanation": "detailed explanation why this answer is correct"}}]}}'
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
    Class 10 level fallback questions when Gemini API fails
    """
    fallback_templates = [
        {
            'question': f'Which of the following is a fundamental concept in {topic}?',
            'options': {
                'A': 'Basic principles and definitions',
                'B': 'Only advanced applications',
                'C': 'Historical dates only',
                'D': 'None of the above'
            },
            'correct_answer': 'A',
            'explanation': 'Understanding basic principles and definitions is essential for mastering any subject at Class 10 level.'
        },
        {
            'question': f'When studying {topic}, which approach is most effective for Class 10 students?',
            'options': {
                'A': 'Memorizing facts only',
                'B': 'Understanding concepts and practicing problems',
                'C': 'Reading textbook once',
                'D': 'Ignoring practical applications'
            },
            'correct_answer': 'B',
            'explanation': 'Understanding concepts combined with regular practice helps students build strong foundations in any subject.'
        },
        {
            'question': f'What is the importance of {topic} in the Class 10 curriculum?',
            'options': {
                'A': 'It has no relevance',
                'B': 'Only for competitive exams',
                'C': 'Builds foundation for higher studies and practical applications',
                'D': 'Just for passing exams'
            },
            'correct_answer': 'C',
            'explanation': 'Class 10 subjects build essential foundations for higher education and real-world applications.'
        }
    ]
    
    # Use different templates to create variety
    questions = []
    for i in range(min(num_questions, len(fallback_templates))):
        questions.append(fallback_templates[i])
    
    # If more questions needed, repeat with modifications
    while len(questions) < num_questions:
        base_question = fallback_templates[len(questions) % len(fallback_templates)].copy()
        base_question['question'] = f"Additional question: {base_question['question']}"
        questions.append(base_question)
    
    return questions[:num_questions]
