import dspy
from src.signatures.en import DevelopHumorStrategyEn
from src.signatures.es import DevelopHumorStrategyEs
from src.signatures.zh import DevelopHumorStrategyZh
from src.examples_en import theory_examples_en
from src.examples_es import theory_examples_es
from src.examples_zh import theory_examples_zh

class TheoryModule(dspy.Module):
    def __init__(self, language='en'):
        super().__init__()
        self.language = language
        
        if language == 'es':
            self.reasoning = dspy.ChainOfThought(DevelopHumorStrategyEs)
            self.reasoning.demos = theory_examples_es
        elif language == 'zh':
            self.reasoning = dspy.ChainOfThought(DevelopHumorStrategyZh)
            self.reasoning.demos = theory_examples_zh
        else:
            self.reasoning = dspy.ChainOfThought(DevelopHumorStrategyEn)
            self.reasoning.demos = theory_examples_en
    
    def forward(self, input_text, context_analysis, language):
        return self.reasoning(input_text=input_text, context_analysis=context_analysis)
