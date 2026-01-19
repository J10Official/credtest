import dspy

# --- Module 1: Context Enrichment Examples ---
context_examples_es = [
    dspy.Example(
        input_text="Hombre muerde perro",
        task_type="headline",
        context_analysis="Hecho: El ejemplo clásico de 'noticia'. Ironía: Inversión del orden natural. Cultural: 'Perrito caliente' (hot dog) es una comida. Posible juego de palabras sobre comer un perrito caliente vs morder un perro real."
    ),
    dspy.Example(
        input_text="rociar, silla",
        task_type="words",
        context_analysis="Asociaciones: 'Rociar' implica limpiar, pintar o gatos marcando territorio. 'Silla' es un mueble. Posible choque: Rociar una silla podría ser un accidente (grafiti), un intento de limpieza fallido o una broma."
    )
]

# --- Module 2: Humor Theory Examples ---
theory_examples_es = [
    dspy.Example(
        input_text="Hombre muerde perro",
        context_analysis="Hecho: El ejemplo clásico de 'noticia'... Ironía: Inversión del orden natural...",
        script_opposition="Normal (Perro muerde hombre) vs. Anormal (Hombre muerde perro)",
        logical_mechanism="Inversión de roles",
        target="Periodismo / La situación",
        humor_strategy="Configuración: Aceptar la premisa literalmente. Desencadenante: La inversión de roles. Remate: Los perros calientes (comida) se defienden."
    ),
    dspy.Example(
        input_text="rociar, silla",
        context_analysis="Asociaciones: 'Rociar' implica limpiar... Posible choque: Rociar una silla podría ser un accidente...",
        script_opposition="Mantenimiento (Bueno) vs. Desastre (Malo)",
        logical_mechanism="Error de objeto / Malentendido",
        target="Uno mismo",
        humor_strategy="Configuración: Describir una situación normal con una silla. Desencadenante: Introducir 'rociar' de una manera inesperada (autobronceador). Remate: La silla ahora está 'bronceada' (arruinada)."
    )
]

# --- Module 3: Draft Examples ---
draft_examples_es = [
    dspy.Example(
        input_text="Hombre muerde perro",
        humor_strategy="Configuración: Aceptar la premisa literalmente... Objetivo: Lo absurdo de la situación.",
        constraints="Máx 20 palabras.",
        draft_text="Supongo que los perritos calientes finalmente se están defendiendo."
    ),
    dspy.Example(
        input_text="rociar, silla",
        humor_strategy="Configuración: Describir una situación normal con una silla... Cambio de Guion: Mantenimiento de muebles -> Desastre personal.",
        constraints="Incluir 'rociar' y 'silla'. Máx 20 palabras.",
        draft_text="Rocié mi silla con autobronceador. Ahora parece que pasó una semana en Ibiza."
    )
]

# --- Module 4: Formatter Examples ---
formatter_examples_es = [
    dspy.Example(
        raw_draft="Aquí hay un chiste: Supongo que los perritos calientes finalmente se están defendiendo. ¡Espero que te guste!",
        constraints="Máx 20 palabras. Sin introducción.",
        final_joke="Supongo que los perritos calientes finalmente se están defendiendo."
    )
]
