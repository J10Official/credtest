import dspy

class JudgeJoke(dspy.Signature):
    """
    Evaluates a generated joke based on constraints, humor theory, and overall quality.
    """
    joke = dspy.InputField(desc="The generated joke.")
    constraints = dspy.InputField(desc="The constraints it must follow.")
    
    is_valid = dspy.OutputField(desc="Boolean: Does it meet all hard constraints?")
    score = dspy.OutputField(desc="Score from 1-10 on humor quality.")
    feedback = dspy.OutputField(desc="Critique and suggestions for improvement.")

class JudgeModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.judge = dspy.ChainOfThought(JudgeJoke)
    
    def forward(self, joke, constraints):
        return self.judge(joke=joke, constraints=constraints)
