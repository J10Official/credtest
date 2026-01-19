import dspy

# --- Module 1: Context Enrichment Examples ---
context_examples = [
    dspy.Example(
        input_text="Ryanair to cut 1 million more passenger seats in Spain",
        task_type="headline",
        language="en",
        context_analysis="Fact: Ryanair is a budget airline known for cutting costs and reducing passenger comfort to the absolute minimum. Irony: 'Cutting seats' usually means reducing capacity, but given their reputation, it sounds like they are literally removing the physical seats to make people stand or save weight. Cultural Context: People love to hate Ryanair's stinginess."
    ),
    dspy.Example(
        input_text="spray, chair",
        task_type="words",
        language="en",
        context_analysis="Associations: 'Spray' implies cleaning, painting, or cats marking territory. 'Chair' is furniture. Potential Clash: Spraying a chair might be an accident (graffiti), a cleaning attempt gone wrong, or a prank. Ambiguity: 'Spray' could be a noun or a verb."
    ),
    dspy.Example(
        input_text="Image Description: A cat sitting on a glass table, viewed from below. The cat looks flattened and ridiculous.",
        task_type="b1",
        language="en",
        context_analysis="Visual: The 'liquid' nature of cats. The unflattering angle makes a majestic animal look silly. Mood: Derpy, exposed, awkward. Theme: Expectations vs. Reality of pet ownership."
    ),
    dspy.Example(
        input_text="Hombre muerde perro (Man bites dog)",
        task_type="headline",
        language="es",
        context_analysis="Fact: The classic example of 'news'. Irony: Reversal of the natural order. Cultural: 'Hot dog' (perrito caliente) is a food. Potential pun on eating a hot dog vs biting a real dog."
    )
]

# --- Module 2: Humor Theory Examples ---
theory_examples = [
    dspy.Example(
        input_text="Ryanair to cut 1 million more passenger seats in Spain",
        context_analysis="Fact: Ryanair is a budget airline known for cutting costs... Irony: 'Cutting seats' sounds like removing physical seats.",
        language="en",
        humor_strategy="Setup: Accept the premise of 'cutting seats' literally. Script Switch: Business decision (reducing capacity) -> Physical removal (making passengers stand/suffer). Trigger: The ambiguity of 'cut seats'. Target: Ryanair's cheapness."
    ),
    dspy.Example(
        input_text="spray, chair",
        context_analysis="Associations: 'Spray' implies cleaning... Potential Clash: Spraying a chair might be an accident...",
        language="en",
        humor_strategy="Setup: Describe a normal situation involving a chair. Trigger: Introduce 'spray' in an unexpected way (e.g., skunk spray, tanning spray). Script Switch: Furniture maintenance -> Personal disaster."
    ),
    dspy.Example(
        input_text="Image Description: A cat sitting on a glass table...",
        context_analysis="Visual: The 'liquid' nature of cats... Mood: Derpy...",
        language="en",
        humor_strategy="Setup: Present the cat as a high-status, elegant creature. Trigger: The visual evidence of it looking like a squashed loaf. Script Switch: Graceful predator -> UFO/Hovercraft landing gear."
    )
]

# --- Module 3: Draft Examples ---
draft_examples = [
    dspy.Example(
        input_text="Ryanair to cut 1 million more passenger seats in Spain",
        humor_strategy="Setup: Accept the premise of 'cutting seats' literally... Target: Ryanair's cheapness.",
        language="en",
        constraints="Max 20 words.",
        draft_text="Next they'll be charging extra for the privilege of standing."
    ),
    dspy.Example(
        input_text="spray, chair",
        humor_strategy="Setup: Describe a normal situation... Script Switch: Furniture maintenance -> Personal disaster.",
        language="en",
        constraints="Include 'spray' and 'chair'. Max 20 words.",
        draft_text="I used tanning spray on my chair. Now it looks like it spent a week in Ibiza."
    ),
    dspy.Example(
        input_text="Image Description: A cat sitting on a glass table...",
        humor_strategy="Setup: Present the cat as a high-status... Script Switch: Graceful predator -> UFO...",
        language="en",
        constraints="Max 20 words.",
        draft_text="The mothership has landed."
    ),
    dspy.Example(
        input_text="Hombre muerde perro",
        humor_strategy="Setup: Reversal of natural order... Pun on hot dog.",
        language="es",
        constraints="Max 20 words.",
        draft_text="Supongo que los perritos calientes finalmente se están defendiendo."
    )
]

# --- Module 4: Formatter Examples ---
formatter_examples = [
    dspy.Example(
        raw_draft="Here is a joke: Next they'll be charging extra for standing. I hope you like it!",
        constraints="Max 20 words. No intro.",
        final_joke="Next they'll be charging extra for standing."
    ),
    dspy.Example(
        raw_draft="Option 1: The mothership has landed. Option 2: Cat loaf.",
        constraints="Max 20 words. Single output.",
        final_joke="The mothership has landed."
    )
]
