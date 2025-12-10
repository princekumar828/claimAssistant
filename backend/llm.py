from typing import List, Dict, Any
import os
from .config import settings

class BaseLLM:
    def generate_answer(self, query: str, context: List[Dict[str, Any]]) -> str:
        raise NotImplementedError

class MockLLM(BaseLLM):
    def generate_answer(self, query: str, context: List[Dict[str, Any]]) -> str:
        # Simple rule-based generation for testing without model
        return (
            f"**[MOCK ANSWER]** Based on the retrieved records, here is the information.\n\n"
            f"I found {len(context)} related claims.\n"
            f"Top result: {context[0]['text'][:200]}..."
        )

class OpenAILLM(BaseLLM):
    def __init__(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        except ImportError:
            raise ImportError("openai package not found.")
            
    def generate_answer(self, query: str, context: List[Dict[str, Any]]) -> str:
        context_str = "\n\n".join([f"Document {i+1}:\n{doc['text']}" for i, doc in enumerate(context)])
        
        system_prompt = (
            "You are a helpful insurance claims assistant. "
            "Answer the user query based ONLY on the provided context documents. "
            "Cite the Claim ID for every fact you mention. "
            "If the answer is not in the documents, say you don't know."
        )
        
        user_prompt = f"Context:\n{context_str}\n\nQuestion: {query}"
        
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content

class GeminiLLM(BaseLLM):
    def __init__(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        except ImportError:
            raise ImportError("google-generativeai package not found.")
            
    def generate_answer(self, query: str, context: List[Dict[str, Any]]) -> str:
        context_str = "\n\n".join([f"Document {i+1}:\n{doc['text']}" for i, doc in enumerate(context)])
        
        prompt = (
            "You are a helpful insurance claims assistant. "
            "Answer the user query based ONLY on the provided context documents. "
            "Cite the Claim ID for every fact you mention. "
            "If the answer is not in the documents, say you don't know.\n\n"
            f"Context:\n{context_str}\n\nQuestion: {query}"
        )
        
        response = self.model.generate_content(prompt)
        return response.text

class GPT4AllLLM(BaseLLM):
    def __init__(self):
        try:
            from gpt4all import GPT4All
            # This might download the model which takes time
            print(f"Loading GPT4All model: {settings.GPT4ALL_MODEL}...")
            self.model = GPT4All(settings.GPT4ALL_MODEL) 
        except ImportError:
            raise ImportError("gpt4all package not found.")
            
    def generate_answer(self, query: str, context: List[Dict[str, Any]]) -> str:
        context_str = "\n".join([f"- {doc['text']}" for doc in context])
        
        prompt = (
            f"### System:\nYou are an insurance assistant. Use the context below to answer the question.\n\n"
            f"### Context:\n{context_str}\n\n"
            f"### User:\n{query}\n\n"
            f"### Assistant:\n"
        )
        
        output = self.model.generate(prompt, max_tokens=300, temp=0.1)
        return output

def get_llm():
    llm_type = settings.LLM_TYPE.lower()
    print(f"Initializing LLM: {llm_type}")
    
    if llm_type == "openai":
        return OpenAILLM()
    elif llm_type == "gemini":
        return GeminiLLM()
    elif llm_type == "gpt4all":
        try:
            return GPT4AllLLM()
        except Exception as e:
            print(f"Failed to load GPT4All: {e}. Falling back to Mock.")
            return MockLLM()
    else:
        return MockLLM()
