import dspy
from src.signatures.en import DraftJokeEn
from src.signatures.es import DraftJokeEs
from src.signatures.zh import DraftJokeZh
from src.examples_en import draft_examples_en
from src.examples_es import draft_examples_es
from src.examples_zh import draft_examples_zh

class DrafterModule(dspy.Module):
    def __init__(self, language='en'):
        super().__init__()
        self.language = language
        
        if language == 'es':
            self.draft = dspy.Predict(DraftJokeEs)
            self.draft.demos = draft_examples_es
        elif language == 'zh':
            self.draft = dspy.Predict(DraftJokeZh)
            self.draft.demos = draft_examples_zh
        else:
            self.draft = dspy.Predict(DraftJokeEn)
            self.draft.demos = draft_examples_en
    
    def forward(self, input_text, humor_strategy, language, constraints, temperature=0.8):
        # DSPy allows context managers for settings
        with dspy.context(lm=dspy.settings.lm.configure(temperature=temperature)):
            return self.draft(input_text=input_text, humor_strategy=humor_strategy, constraints=constraints)
