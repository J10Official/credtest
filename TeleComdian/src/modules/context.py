import dspy
from src.signatures.en import DescribeImageEn, EnrichContextEn
from src.signatures.es import DescribeImageEs, EnrichContextEs
from src.signatures.zh import DescribeImageZh, EnrichContextZh
from src.examples_en import context_examples_en
from src.examples_es import context_examples_es
from src.examples_zh import context_examples_zh

class ContextModule(dspy.Module):
    def __init__(self, language='en'):
        super().__init__()
        self.language = language
        
        if language == 'es':
            self.describe_image = dspy.Predict(DescribeImageEs)
            self.generate_context = dspy.ChainOfThought(EnrichContextEs)
            self.generate_context.demos = context_examples_es
        elif language == 'zh':
            self.describe_image = dspy.Predict(DescribeImageZh)
            self.generate_context = dspy.ChainOfThought(EnrichContextZh)
            self.generate_context.demos = context_examples_zh
        else:
            self.describe_image = dspy.Predict(DescribeImageEn)
            self.generate_context = dspy.ChainOfThought(EnrichContextEn)
            self.generate_context.demos = context_examples_en
    
    def forward(self, input_text, task_type, language, image_data=None):
        # Note: language arg in forward is redundant if we init per language, 
        # but kept for compatibility if needed, though we rely on self.language
        
        text_context = input_text
        
        if image_data:
             # VLM Step: Generate description from image
             desc_res = self.describe_image(image_input=image_data)
             description = desc_res.description
             
             # Combine description with original prompt if any
             if input_text:
                 text_context = f"Image Description: {description}\nTask Prompt: {input_text}"
             else:
                 text_context = f"Image Description: {description}"
        
        return self.generate_context(input_text=text_context, task_type=task_type)
