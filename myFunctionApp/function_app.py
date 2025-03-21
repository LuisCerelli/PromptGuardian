import azure.functions as func
import logging
import json
import re
import random


import os
import openai

from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

# Cargar credenciales desde variables de entorno
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

CONTENT_SAFETY_KEY = os.getenv("AZURE_CONTENT_SAFETY_API_KEY")
CONTENT_SAFETY_ENDPOINT = os.getenv("AZURE_CONTENT_SAFETY_API_URL")

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
    
def analyze_content_safety(text, max_severity=3):
    """Analiza el texto y devuelve una respuesta en español indicando posibles problemas y sugerencias."""
    result = {
        "original_prompt": text,
        "processed_prompt": text,
        "issues": [],
        "suggestions": [],
        "risk_level": "low",
        "intention": None,
        "context": None,
        "complexity": None
    }

    # Validar credenciales antes de ejecutar
    if not CONTENT_SAFETY_ENDPOINT or not CONTENT_SAFETY_KEY:
        logging.error("Las credenciales de Content Safety no están configuradas correctamente.")
        return {"error": "Error de configuración: faltan credenciales de Content Safety."}

    try:
        client = ContentSafetyClient(endpoint=CONTENT_SAFETY_ENDPOINT, credential=AzureKeyCredential(str(CONTENT_SAFETY_KEY)))
        response = client.analyze_text(AnalyzeTextOptions(text=text))

        # 🔍 Imprimir la respuesta de Azure en logs
        logging.info(f"Respuesta de Azure: {response}")

        # Verificar si hay datos en categoriesAnalysis
        if not response.categories_analysis:
            logging.warning("La respuesta de Azure no contiene análisis de categorías.")
            return {"error": "No se recibieron datos de análisis de contenido."}

        # Procesar las categorías de la respuesta
        for category_analysis in response.categories_analysis:
            category = category_analysis.category.lower()  # Convertimos a minúsculas para evitar errores de comparación
            severity = category_analysis.severity

            if severity > max_severity:
                result["issues"].append(category)
                result["risk_level"] = "high"

        # Agregar sugerencias basadas en las categorías detectadas
        messages = {
            "hate": "Se detectó lenguaje de odio. Por favor, use un lenguaje respetuoso.",
            "selfharm": "Se detectaron indicios de autolesión. Si necesita ayuda, por favor busque apoyo profesional.",
            "sexual": "El texto contiene contenido sexual. Considere reformularlo para mayor adecuación.",
            "violence": "Se detectó contenido violento. Evite promover la violencia en su mensaje."
        }

        for issue in result["issues"]:
            if issue in messages:
                result["suggestions"].append(messages[issue])

        return result
    
    except HttpResponseError as ex:
        logging.error(f"Error en el análisis de contenido: {ex.message}")
        return {"error": f"Error en la API de Azure: {ex.message}"}
    except Exception as e:
        logging.error(f"Error inesperado en el análisis de contenido: {str(e)}")
        return {"error": f"Error inesperado: {str(e)}"}

def analyze_with_openai(prompt):
    """Usa Azure OpenAI para analizar el prompt y mejorar su calidad."""
    try:
        client = openai.AzureOpenAI(
            api_key=OPENAI_API_KEY,
            api_version=OPENAI_API_VERSION,
            azure_endpoint=OPENAI_ENDPOINT
        )
        
        response = client.chat.completions.create(
            model=OPENAI_DEPLOYMENT,
            messages=[{"role": "system", "content": "Eres un asistente útil que analiza y mejora prompts."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error en OpenAI: {str(e)}")
        return None

@app.route(route="preprocess_prompt", methods=["OPTIONS", "POST"])
def preprocess_prompt_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    # Manejando la solicitud OPTIONS (preflight)
    if req.method == "OPTIONS":
        return func.HttpResponse(
            "",
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
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
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
            )

        # 🔹 1. Inicializar resultado
        result = {
            'original_prompt': prompt,
            'processed_prompt': prompt,  # Solo cambiará si OpenAI se ejecuta
            'issues': [],
            'suggestions': [],
            'risk_level': 'low',
            'intention': None,
            'context': None,
            'complexity': None
        }

        # 🔹 2. Analizar seguridad con Content Safety
        content_safety_result = analyze_content_safety(prompt)
        result['issues'].extend(content_safety_result.get('issues', []))
        result['suggestions'].extend(content_safety_result.get('suggestions', []))
        result['risk_level'] = content_safety_result.get('risk_level', 'low')

        # 🔹 3. Detectar lenguaje inapropiado
        if contains_inappropriate_language(prompt):
            result['issues'].append('inappropriate_language')
            result['suggestions'].append('Se detectaron palabras inapropiadas. El procesamiento fue detenido.')
            result['risk_level'] = 'high'

        # 🔹 4. Si hay lenguaje inapropiado o riesgo alto, detener aquí
        if 'inappropriate_language' in result['issues'] or result['risk_level'] == 'high':
            return func.HttpResponse(
                json.dumps(result),
                status_code=200,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
            )

        # 🔹 5. Detección de intención, contexto y complejidad
        result['intention'] = detect_prompt_intention(prompt)
        result['context'] = detect_context_and_improve(prompt)
        result['complexity'] = analyze_prompt_complexity(prompt)

        # 🔹 6. Generar sugerencias de mejora
        improvement_suggestions = generate_improvement_suggestions(
            result['intention'], 
            result['context'],
            result['complexity']
        )
        result['suggestions'].extend(improvement_suggestions)

        # 🔹 7. Ejecutar OpenAI solo si no hay lenguaje inapropiado
        improved_prompt = analyze_with_openai(prompt)
        if improved_prompt:
            result['processed_prompt'] = improved_prompt

        # 🔹 8. Responder con los resultados
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
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
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )