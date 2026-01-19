import dspy
import os

from .google_client import GoogleGenAI

# Placeholder for API Key - in production use env vars
API_KEY = "AIzaSyCHOT98OXqydAPksLXnWT8Pdws5pTm6ejw" 
MODEL_NAME = "models/gemma-3-27b-it" 

def setup_dspy():
    """
    Configures the DSPy default language model using the custom GoogleGenAI client.
    """
    lm = GoogleGenAI(model=MODEL_NAME, api_key=API_KEY)
    dspy.settings.configure(lm=lm)
    return lm
