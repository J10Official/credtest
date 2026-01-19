import dspy
from src.signatures.en import FormatJokeEn
from src.signatures.es import FormatJokeEs
from src.signatures.zh import FormatJokeZh
from src.examples_en import formatter_examples_en
from src.examples_es import formatter_examples_es
from src.examples_zh import formatter_examples_zh

class FormatterModule(dspy.Module):
    def __init__(self, language='en'):
        super().__init__()
        self.language = language
        
        if language == 'es':
            self.format = dspy.Predict(FormatJokeEs)
            self.format.demos = formatter_examples_es
        elif language == 'zh':
            self.format = dspy.Predict(FormatJokeZh)
            self.format.demos = formatter_examples_zh
        else:
            self.format = dspy.Predict(FormatJokeEn)
            self.format.demos = formatter_examples_en
    
    def forward(self, raw_draft, constraints):
        return self.format(raw_draft=raw_draft, constraints=constraints)
