import dspy

# --- English Signatures ---

class DescribeImageEn(dspy.Signature):
    """
    Generates a dense, descriptive caption for an image to be used as context for humor generation.
    Focus on visual details, actions, and mood.
    """
    image_input = dspy.InputField(desc="The image to describe.")
    description = dspy.OutputField(desc="A dense textual description of the image.")

class EnrichContextEn(dspy.Signature):
    """
    Analyzes the input and retrieves relevant factual and cultural context to aid in joke generation.
    For headlines, it identifies the core irony or absurdity.
    For word pairs, it identifies common associations and potential clashes.
    """
    input_text = dspy.InputField(desc="The news headline, word pair, or image description.")
    task_type = dspy.InputField(desc="Type of task: 'headline', 'words', or 'image'.")
    
    context_analysis = dspy.OutputField(desc="Factual context, cultural associations, and potential angles for humor.")

class DevelopHumorStrategyEn(dspy.Signature):
    """
    Applies the Semantic Script Theory of Humor (SSTH) to develop a joke concept.
    Identifies two opposing scripts and a logical mechanism to connect them.
    """
    input_text = dspy.InputField(desc="The original input (headline, words, or image description).")
    context_analysis = dspy.InputField(desc="Enriched context, associations, and facts.")
    
    script_opposition = dspy.OutputField(desc="The two conflicting scripts (e.g., Real vs. Unreal, Normal vs. Abnormal, Life vs. Death).")
    logical_mechanism = dspy.OutputField(desc="The cognitive rule that connects the scripts (e.g., Reversal, Exaggeration, Juxtaposition).")
    target = dspy.OutputField(desc="The target of the joke (person, group, institution, or concept).")
    humor_strategy = dspy.OutputField(desc="A step-by-step plan: Setup (Script 1) -> Trigger -> Punchline (Script 2).")

class DraftJokeEn(dspy.Signature):
    """
    Drafts a joke based on the provided humor strategy.
    The joke must be short, punchy, and strictly follow the constraints.
    """
    input_text = dspy.InputField(desc="The original input.")
    humor_strategy = dspy.InputField(desc="The structural plan for the joke.")
    constraints = dspy.InputField(desc="Specific constraints (e.g., max length, included words).")
    
    draft_text = dspy.OutputField(desc="The raw generated joke text.")

class FormatJokeEn(dspy.Signature):
    """
    Formats the raw joke draft into the final submission format.
    Ensures no introductory text, no explanations, and strict adherence to length limits.
    """
    raw_draft = dspy.InputField(desc="The raw generated joke.")
    constraints = dspy.InputField(desc="Constraints to enforce.")
    
    final_joke = dspy.OutputField(desc="The clean, formatted joke string.")
