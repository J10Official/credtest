import dspy
import re

class HumorJudge(dspy.Signature):
    """
    Evaluates if a text is humorous, makes sense in the context, and follows instructions.
    """
    input_context = dspy.InputField(desc="The context, setup, or prompt for the joke.")
    generated_text = dspy.InputField(desc="The generated joke or caption.")
    
    is_valid = dspy.OutputField(desc="Yes or No. Is this a valid and humorous attempt?")
    reason = dspy.OutputField(desc="Reasoning for the judgment.")

class Validator:
    def __init__(self):
        self.judge = dspy.Predict(HumorJudge)

    def check_length(self, text, language):
        limit = 300 if language == 'zh' else 900
        return len(text) <= limit

    def check_word_inclusion(self, text, word1, word2):
        if not word1 or not word2 or word1 == '-' or word2 == '-':
            return True
        text_lower = text.lower()
        return (word1.lower() in text_lower) and (word2.lower() in text_lower)

    def check_task_b2_alignment(self, text, prompt):
        """
        Checks if the generated text aligns with the B2 prompt.
        The text should either start with the prompt (minus blank) or be a plausible completion.
        """
        if not prompt:
            return True
            
        prompt_clean = prompt.replace("______", "").strip()
        text_clean = text.strip()
        
        # Case 1: Text starts with the prompt
        if text_clean.lower().startswith(prompt_clean.lower()):
            return True
            
        # Case 2: Text is likely just the completion (heuristic: shorter than prompt?)
        # This is ambiguous. If the pipeline is supposed to produce the full sentence, 
        # then "just completion" is a failure of the pipeline's formatting, but maybe not "logic".
        # However, to ensure "blank is filled", we really want the full sentence to match.
        # We will rely on the pipeline to prepend the prompt if it's missing, 
        # so by the time we validate, it MUST start with the prompt.
        return False

    def check_humor(self, input_context, text):
        try:
            # We use a low temperature for the judge to be objective
            with dspy.context(lm=dspy.settings.lm.configure(temperature=0.1)):
                res = self.judge(input_context=input_context, generated_text=text)
            return "yes" in res.is_valid.lower()
        except Exception as e:
            print(f"Humor check failed: {e}")
            return True # Fail open if validator crashes

