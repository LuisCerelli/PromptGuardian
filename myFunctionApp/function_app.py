import azure.functions as func
import logging
import json
import re
import random

app = func.FunctionApp()

def contains_inappropriate_language(prompt):
    inappropriate_words = [
        'mierda', 'idiota', 'estúpido', 'imbécil', 
        'pendejo', 'hijo de puta', 'gilipollas'
    ]
    
    prompt_lower = prompt.lower()
    
    for word in inappropriate_words:
        if word in prompt_lower:
            return True
    
    return False

def detect_prompt_intention(prompt):
    """
    Análisis más detallado de la intención del prompt
    """
    intention_patterns = {
        'learning': [
            r'\b(aprender|explicar|entender|comprender)\b',
            r'\b(cómo funciona|qué es|significado)\b'
        ],
        'problem_solving': [
            r'\b(resolver|ayuda|solución|problema|diagnosticar)\b',
            r'\b(cómo puedo|qué debo hacer)\b'
        ],
        'creative': [
            r'\b(imaginar|crear|diseñar|inventar|proponer)\b',
            r'\b(nueva idea|innovación|concepto)\b'
        ],
        'analytical': [
            r'\b(analizar|investigar|estudiar|examinar)\b',
            r'\b(impacto|consecuencias|desarrollo)\b'
        ],
        'technical': [
            r'\b(algoritmo|inteligencia artificial|machine learning|tecnología)\b',
            r'\b(programación|código|sistema|computación)\b'
        ]
    }
    
    detected_intentions = []
    
    for intention, patterns in intention_patterns.items():
        for pattern in patterns:
            if re.search(pattern, prompt.lower()):
                detected_intentions.append(intention)
                break
    
    return detected_intentions if detected_intentions else ['general']

def detect_context_and_improve(prompt):
    """
    Detecta el contexto del prompt
    """
    context_patterns = {
        'learning': [
            r'\b(explicame|qué es|cómo funciona)\b',
            r'\b(entender|comprender)\b'
        ],
        'problem_solving': [
            r'\b(resolver|problema|ayuda|solución)\b',
            r'\b(cómo puedo|qué debo hacer)\b'
        ],
        'creative': [
            r'\b(imagina|crea|diseña|inventa|propón)\b',
            r'\b(nueva idea|innovación|concepto)\b'
        ],
        'technical': [
            r'\b(tecnología|algoritmo|sistema|método)\b',
            r'\b(desarrollo|implementación)\b'
        ]
    }
    
    for context, patterns in context_patterns.items():
        for pattern in patterns:
            if re.search(pattern, prompt.lower()):
                return context
    
    return 'general'

def analyze_prompt_complexity(prompt):
    """
    Analiza la complejidad y profundidad del prompt
    """
    # Métricas de complejidad
    word_count = len(prompt.split())
    unique_words = len(set(prompt.lower().split()))
    
    # Detección de palabras técnicas o especializadas
    technical_words = [
        'algoritmo', 'inteligencia', 'machine learning', 
        'neural', 'computacional', 'cuántico', 'blockchain'
    ]
    
    technical_word_count = sum(1 for word in technical_words if word in prompt.lower())
    
    # Clasificación de complejidad
    complexity_level = 'basic'
    if word_count > 10 and unique_words > 8:
        complexity_level = 'intermediate'
    if technical_word_count > 0 or word_count > 15:
        complexity_level = 'advanced'
    
    # Análisis de profundidad
    depth_indicators = {
        'basic': ['simple', 'general', 'introducción'],
        'intermediate': ['detallado', 'explicación', 'análisis'],
        'advanced': ['profundo', 'complejo', 'especializado']
    }
    
    depth = random.choice(depth_indicators[complexity_level])
    
    return {
        'word_count': word_count,
        'unique_words': unique_words,
        'technical_words': technical_word_count,
        'complexity_level': complexity_level,
        'depth': depth
    }

def generate_improvement_suggestions(intentions, context, complexity=None):
    """
    Genera sugerencias de mejora basadas en la intención, contexto y complejidad
    """
    suggestion_templates = {
        'learning': [
            "Profundice en los conceptos fundamentales.",
            "Considere incluir ejemplos prácticos para una mejor comprensión."
        ],
        'problem_solving': [
            "Proporcione más detalles sobre el contexto del problema.",
            "Incluya información sobre los recursos o herramientas disponibles."
        ],
        'creative': [
            "Explore límites y restricciones para guiar la creatividad.",
            "Considere el impacto potencial de su idea innovadora."
        ],
        'technical': [
            "Especifique el nivel de conocimiento técnico requerido.",
            "Considere el ecosistema tecnológico relevante."
        ],
        'general': [
            "Sea más específico en su solicitud.",
            "Proporcione contexto adicional para una mejor comprensión."
        ]
    }
    
    # Combinar sugerencias basadas en intenciones y contexto
    suggestions = []
    for intention in intentions:
        if intention in suggestion_templates:
            suggestions.extend(
                random.sample(suggestion_templates[intention], 
                              min(1, len(suggestion_templates[intention])))
            )
    
    # Sugerencias basadas en complejidad
    if complexity:
        if complexity.get('complexity_level') == 'basic':
            suggestions.append("Considere expandir su prompt para obtener información más detallada.")
        elif complexity.get('complexity_level') == 'advanced':
            suggestions.append("Su prompt parece ser muy técnico. Asegúrese de que la audiencia comprenderá la terminología.")
    
    return suggestions

@app.route(route="preprocess_prompt", methods=["OPTIONS", "POST"])
def preprocess_prompt_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    # Manejando la solicitud OPTIONS (preflight)
    if req.method == "OPTIONS":
        return func.HttpResponse(
            "",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",  # Permitir solicitudes desde cualquier origen
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    try:
        req_body = req.get_json()
        prompt = req_body.get('prompt', '')

        if not prompt:
            return func.HttpResponse(
                json.dumps({"error": "Prompt vacío"}),
                status_code=400,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "*",  # CORS permitido
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
            )

        # Inicializar resultado
        result = {
            'original_prompt': prompt,
            'processed_prompt': prompt,
            'issues': [],
            'suggestions': [],
            'risk_level': 'low',
            'intention': None,
            'context': None,
            'complexity': None
        }

        # Validación de longitud
        if len(prompt) < 5:
            result['issues'].append('short_prompt')
            result['suggestions'].append(
                'El prompt es demasiado corto. Por favor, proporcione más contexto.'
            )

        # Validación de lenguaje inapropiado
        if contains_inappropriate_language(prompt):
            result['issues'].append('inappropriate_language')
            result['suggestions'].append(
                'Se detectaron palabras inapropiadas. Por favor, use un lenguaje respetuoso.'
            )
            result['risk_level'] = 'high'

        # Detección de intención
        intentions = detect_prompt_intention(prompt)
        result['intention'] = intentions

        # Detección de contexto
        context = detect_context_and_improve(prompt)
        result['context'] = context

        # Análisis de complejidad
        complexity_analysis = analyze_prompt_complexity(prompt)
        result['complexity'] = complexity_analysis

        # Generar sugerencias de mejora
        improvement_suggestions = generate_improvement_suggestions(
            intentions, 
            context,
            result['complexity']
        )
        result['suggestions'].extend(improvement_suggestions)

        # Responder con los resultados
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",  # CORS permitido
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    except Exception as e:
        logging.error(f"Error en procesamiento: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",  # CORS permitido
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )
