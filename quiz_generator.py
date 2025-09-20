import json
import os
import re
from typing import Dict, List, Any
from openai import OpenAI

class QuizGenerator:
    def __init__(self):
        """Initialize the quiz generator with OpenAI client."""
        self.api_key = os.getenv("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")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=self.api_key)
        
    def extract_key_concepts(self, content: str) -> Dict[str, List[str]]:
        """Extract key concepts from the content using simple text processing."""
        # Remove extra whitespace and split into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Extract potential key terms (capitalized words, repeated terms)
        key_terms = set()
        words = re.findall(r'\b[A-Z][a-z]+\b', content)  # Capitalized words
        
        # Count word frequency for important terms
        word_count = {}
        for word in re.findall(r'\b\w+\b', content.lower()):
            if len(word) > 3:  # Only consider words longer than 3 characters
                word_count[word] = word_count.get(word, 0) + 1
        
        # Get frequently mentioned terms
        frequent_terms = [word for word, count in word_count.items() if count > 1]
        
        return {
            'sentences': sentences[:10],  # First 10 sentences for context
            'key_terms': list(set(words[:20])),  # Unique capitalized words
            'frequent_terms': frequent_terms[:10]  # Most frequent terms
        }
    
    def generate_assignments(self, content: str, concepts: Dict) -> List[Dict]:
        """Generate assignment questions using OpenAI."""
        prompt = f"""
        Based on the following content, generate exactly 2 assignment questions (essay prompts or discussion questions).
        
        Content: {content[:2000]}  # Limit content length
        
        Key concepts identified: {', '.join(concepts.get('key_terms', []))}
        
        Requirements:
        - Create thought-provoking essay prompts or discussion questions
        - Questions should encourage critical thinking and analysis
        - Include guidance or tips for each question
        - Focus on the main themes and concepts from the content
        
        Respond with JSON in this exact format:
        {{
            "assignments": [
                {{
                    "question": "Your essay prompt or discussion question here",
                    "guidance": "Helpful tips and guidance for answering this question"
                }},
                {{
                    "question": "Your second essay prompt or discussion question here",
                    "guidance": "Helpful tips and guidance for answering this question"
                }}
            ]
        }}
        """
        
        try:
            # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert educational content creator. Generate high-quality assignment questions that promote deep learning and critical thinking."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Received empty response from OpenAI")
            result = json.loads(content)
            return result.get('assignments', [])
            
        except Exception as e:
            print(f"Error generating assignments: {e}")
            return []
    
    def generate_quiz(self, content: str, concepts: Dict) -> List[Dict]:
        """Generate multiple choice quiz questions using OpenAI."""
        prompt = f"""
        Based on the following content, generate exactly 3 multiple-choice quiz questions.
        
        Content: {content[:2000]}  # Limit content length
        
        Key concepts identified: {', '.join(concepts.get('key_terms', []))}
        
        Requirements:
        - Each question must have exactly 4 options (A, B, C, D)
        - Only one correct answer per question
        - Questions should test understanding of key concepts
        - Include brief explanations for the correct answers
        - Make incorrect options plausible but clearly wrong
        
        Respond with JSON in this exact format:
        {{
            "quiz": [
                {{
                    "question": "Your multiple choice question here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option B",
                    "explanation": "Brief explanation of why this is correct"
                }},
                {{
                    "question": "Your second multiple choice question here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option C",
                    "explanation": "Brief explanation of why this is correct"
                }},
                {{
                    "question": "Your third multiple choice question here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": "Brief explanation of why this is correct"
                }}
            ]
        }}
        """
        
        try:
            # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert quiz creator. Generate challenging but fair multiple-choice questions that test comprehension and application of knowledge."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('quiz', [])
            
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return []
    
    def generate_educational_content(self, content: str) -> Dict[str, Any]:
        """Generate both assignments and quiz from the provided content."""
        if not content or len(content.strip()) < 50:
            raise ValueError("Content is too short. Please provide at least 50 characters of meaningful content.")
        
        try:
            # Extract key concepts from content
            concepts = self.extract_key_concepts(content)
            
            # Generate assignments and quiz
            assignments = self.generate_assignments(content, concepts)
            quiz = self.generate_quiz(content, concepts)
            
            if not assignments or not quiz:
                raise Exception("Failed to generate complete educational content")
            
            return {
                'assignments': assignments,
                'quiz': quiz,
                'content_length': len(content),
                'key_concepts': concepts.get('key_terms', [])
            }
            
        except Exception as e:
            print(f"Error in generate_educational_content: {e}")
            raise e
