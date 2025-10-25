# ollama_integration.py
import ollama
from typing import List, Dict

class AICRUDAssistant:
    def __init__(self, model="llama3.1:latest"):
        self.client = ollama.Client()
        self.model = model
    
    def natural_language_query(self, query: str, user_context: Dict) -> str:
        prompt = f"""
        You are a CRUD operations assistant. Help with: {query}
        User Role: {user_context.get('role')}
        Available operations: categories, products, user management
        """
        response = self.client.generate(model=self.model, prompt=prompt)
        return response['response']