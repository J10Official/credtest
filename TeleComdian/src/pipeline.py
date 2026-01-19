import dspy
from .modules.context import ContextModule
from .modules.theory import TheoryModule
from .modules.draft import DrafterModule
from .modules.formatter import FormatterModule
from .config import setup_dspy
from .validator import Validator

class TeleComedianPipeline(dspy.Module):
    def __init__(self, language='en'):
        super().__init__()
        self.lm = setup_dspy()
        self.language = language
        
        self.context_module = ContextModule(language=language)
        self.theory_module = TheoryModule(language=language)
        self.drafter_module = DrafterModule(language=language)
        self.formatter_module = FormatterModule(language=language)
        self.validator = Validator()
        
    def forward(self, input_item, task_type, language='en', constraints=None, image_data=None, word1=None, word2=None):
        """
        Main pipeline execution flow.
        """
        # 1. Context Enrichment
        # Pass image_data if available (for Task B)
        context_res = self.context_module(input_text=input_item, task_type=task_type, language=language, image_data=image_data)
        context_analysis = context_res.context_analysis
        
        # 2. Humor Theory (Chain of Thought)
        # For Task B, input_item might be empty (B1), so we use the context analysis (which has the image description) as the primary driver
        theory_input = input_item if input_item else context_analysis
        theory_res = self.theory_module(input_text=theory_input, context_analysis=context_analysis, language=language)
        humor_strategy = theory_res.humor_strategy
        
        # Retry Loop
        max_retries = 3
        best_attempt = ""
        current_constraints = constraints
        
        for attempt in range(max_retries):
            # 3. Dynamic Drafting
            # We can use different temperatures for different phases.
            # Here we use a slightly higher temp for drafting to encourage creativity.
            draft_res = self.drafter_module(
                input_text=input_item, 
                humor_strategy=humor_strategy, 
                language=language, 
                constraints=current_constraints,
                temperature=0.9 # High creativity
            )
            raw_draft = draft_res.draft_text
            
            # 4. Post-Hoc Formatting
            # Low temp for strict formatting
            with dspy.context(lm=dspy.settings.lm.configure(temperature=0.1)):
                format_res = self.formatter_module(raw_draft=raw_draft, constraints=constraints)
                
            final_joke = format_res.final_joke

            # Task B2 Logic: Ensure full sentence
            if task_type == 'b2' and input_item:
                prompt_clean = input_item.replace("______", "").strip()
                if not final_joke.strip().lower().startswith(prompt_clean.lower()):
                    # Prepend prompt if missing
                    final_joke = f"{prompt_clean} {final_joke}"

            # Validation
            is_valid_len = self.validator.check_length(final_joke, language)
            
            is_valid_words = True
            if task_type == 'words':
                is_valid_words = self.validator.check_word_inclusion(final_joke, word1, word2)
            
            is_valid_b2 = True
            if task_type == 'b2':
                is_valid_b2 = self.validator.check_task_b2_alignment(final_joke, input_item)
                
            is_funny = self.validator.check_humor(input_item if input_item else context_analysis, final_joke)
            
            if is_valid_len and is_valid_words and is_valid_b2 and is_funny:
                return final_joke
            
            best_attempt = final_joke
            
            # Update constraints for next attempt
            feedback = []
            if not is_valid_len: feedback.append("Too long.")
            if not is_valid_words: feedback.append(f"Must include {word1} and {word2}.")
            if not is_valid_b2: feedback.append("Must complete the prompt.")
            if not is_funny: feedback.append("Make it funnier.")
            
            current_constraints = f"{constraints} (Attempt {attempt+2}: {'; '.join(feedback)})"
            
        # Fallback: Clip to length
        limit = 300 if language == 'zh' else 900
        return best_attempt[:limit]

# Example usage
if __name__ == "__main__":
    pipeline = TeleComedianPipeline()
    
    # Test Task A (Headline)
    headline = "Ryanair to cut 1 million more passenger seats in Spain"
    joke = pipeline(input_item=headline, task_type="headline", language="en", constraints="Max 20 words")
    print(f"Headline: {headline}")
    print(f"Joke: {joke}")
