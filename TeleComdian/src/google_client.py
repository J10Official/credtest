import dspy
import google.generativeai as genai
import time
from dspy.clients.lm import LM

class GoogleGenAI(LM):
    def __init__(self, model, api_key, **kwargs):
        super().__init__(model=model)
        genai.configure(api_key=api_key)
        self.api_key = api_key
        self.model_name = model
        self.client = genai.GenerativeModel(model)
        self.kwargs = kwargs
        self.provider = "google"

    def configure(self, **kwargs):
        new_kwargs = self.kwargs.copy()
        new_kwargs.update(kwargs)
        return GoogleGenAI(model=self.model_name, api_key=self.api_key, **new_kwargs)

    def __call__(self, prompt=None, messages=None, **kwargs):
        # Combine kwargs with init kwargs
        generation_config = {**self.kwargs, **kwargs}
        
        # Handle input
        if messages:
            # DSPy chat format to Gemini format
            # Gemini expects history + last message or just text
            # For simplicity in this custom wrapper, we'll concatenate to text
            # or use the chat session if we want to be fancy.
            # Let's try simple text concatenation for robustness first.
            text_input = ""
            for msg in messages:
                role = msg['role']
                content = msg['content']
                text_input += f"{role.upper()}: {content}\n"
            text_input += "ASSISTANT:" # Prompt for completion
        else:
            text_input = prompt

        # Retry logic: 10s, 20s, 30s, 60s, 60s
        delays = [10, 20, 30, 60, 60]
        
        for attempt, delay in enumerate(delays + [None]):
            try:
                response = self.client.generate_content(text_input, generation_config=generation_config)
                if response.text:
                    return [response.text]
                return [""]
            except Exception as e:
                if delay is not None:
                    print(f"Error in GoogleGenAI (Attempt {attempt+1}): {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    print(f"Error in GoogleGenAI (Final Attempt): {e}. Giving up.")
                    return [""]

