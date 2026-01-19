import dspy

# --- Spanish Signatures ---

class DescribeImageEs(dspy.Signature):
    """
    Genera una descripción densa y descriptiva de una imagen para usarla como contexto para la generación de humor.
    Concéntrese en los detalles visuales, las acciones y el estado de ánimo.
    """
    image_input = dspy.InputField(desc="La imagen a describir.")
    description = dspy.OutputField(desc="Una descripción textual densa de la imagen.")

class EnrichContextEs(dspy.Signature):
    """
    Analiza la entrada y recupera el contexto fáctico y cultural relevante para ayudar en la generación de chistes.
    Para los titulares, identifica la ironía central o el absurdo.
    Para pares de palabras, identifica asociaciones comunes y posibles choques.
    """
    input_text = dspy.InputField(desc="El titular de la noticia, par de palabras o descripción de la imagen.")
    task_type = dspy.InputField(desc="Tipo de tarea: 'headline' (titular), 'words' (palabras) o 'image' (imagen).")
    
    context_analysis = dspy.OutputField(desc="Contexto fáctico, asociaciones culturales y posibles ángulos para el humor.")

class DevelopHumorStrategyEs(dspy.Signature):
    """
    Aplica la Teoría Semántica del Humor Basada en Guiones (SSTH) para desarrollar un concepto de chiste.
    Identifica dos guiones opuestos y un mecanismo lógico para conectarlos.
    """
    input_text = dspy.InputField(desc="La entrada original (titular, palabras o descripción de imagen).")
    context_analysis = dspy.InputField(desc="Contexto enriquecido, asociaciones y hechos.")
    
    script_opposition = dspy.OutputField(desc="Los dos guiones en conflicto (ej. Real vs. Irreal, Normal vs. Anormal).")
    logical_mechanism = dspy.OutputField(desc="La regla cognitiva que conecta los guiones (ej. Inversión, Exageración, Yuxtaposición).")
    target = dspy.OutputField(desc="El objetivo del chiste (persona, grupo, institución o concepto).")
    humor_strategy = dspy.OutputField(desc="Un plan paso a paso: Configuración (Guion 1) -> Desencadenante -> Remate (Guion 2).")

class DraftJokeEs(dspy.Signature):
    """
    Redacta un chiste basado en la estrategia de humor proporcionada.
    El chiste debe ser corto, contundente y seguir estrictamente las restricciones.
    """
    input_text = dspy.InputField(desc="La entrada original.")
    humor_strategy = dspy.InputField(desc="El plan estructural para el chiste.")
    constraints = dspy.InputField(desc="Restricciones específicas (por ejemplo, longitud máxima, palabras incluidas).")
    
    draft_text = dspy.OutputField(desc="El texto del chiste generado sin procesar.")

class FormatJokeEs(dspy.Signature):
    """
    Formatea el borrador del chiste en el formato de envío final.
    Asegura que no haya texto introductorio, explicaciones y un cumplimiento estricto de los límites de longitud.
    """
    raw_draft = dspy.InputField(desc="El chiste generado sin procesar.")
    constraints = dspy.InputField(desc="Restricciones a cumplir.")
    
    final_joke = dspy.OutputField(desc="La cadena del chiste limpia y formateada.")
