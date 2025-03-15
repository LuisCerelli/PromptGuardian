# import azure.functions as func
# import datetime
# import json
# import logging

# app = func.FunctionApp()

import azure.functions as func
import json
import re
import os
import spacy
from typing import Dict, Any
from profanity_check import predict
from textblob import TextBlob
import logging
import openai

# Importaciones de Azure Content Safety
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import AnalyzeTextOptions

# Cargar modelos de procesamiento de lenguaje
nlp = spacy.load("es_core_news_sm")

class PromptPreprocessor:
    @staticmethod
    def analyze_content_safety(prompt: str) -> Dict[str, Any]:
        """
        Análisis de seguridad de contenido con Azure Content Safety
        """
        try:
            # Configuración de Content Safety desde variables de entorno
            content_safety_endpoint = os.environ.get('AZURE_CONTENT_SAFETY_ENDPOINT')
            content_safety_key = os.environ.get('AZURE_CONTENT_SAFETY_KEY')
            
            content_safety_client = ContentSafetyClient(
                content_safety_endpoint, 
                AzureKeyCredential(content_safety_key)
            )
            
            # Preparar solicitud de análisis
            request = AnalyzeTextOptions(text=prompt)
            
            # Realizar análisis
            response = content_safety_client.analyze_text(request)
            
            # Evaluar resultados
            safety_results = {
                'hate': response.hate_result.severity if response.hate_result else 0,
                'sexual': response.sexual_result.severity if response.sexual_result else 0,
                'self_harm': response.self_harm_result.severity if response.self_harm_result else 0,
                'violence': response.violence_result.severity if response.violence_result else 0
            }
            
            return {
                'is_safe': all(severity <= 2 for severity in safety_results.values()),
                'details': safety_results
            }
        except Exception as e:
            logging.error(f"Error en análisis de seguridad: {str(e)}")
            return {
                'is_safe': False,
                'error': str(e)
            }

    @staticmethod
    def enhance_prompt_with_openai(prompt: str) -> str:
        """
        Mejora del prompt utilizando GPT para claridad
        """
        try:
            # Configuración de OpenAI desde variables de entorno
            openai.api_key = os.environ.get('OPENAI_API_KEY')
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente que mejora la claridad y precisión de los prompts."},
                    {"role": "user", "content": f"Mejora la claridad de este prompt: {prompt}"}
                ]
            )
            
            enhanced_prompt = response.choices[0].message.content.strip()
            return enhanced_prompt
        except Exception as e:
            logging.error(f"Error en mejora de prompt: {str(e)}")
            return prompt

    @staticmethod
    def grammatical_correction(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Corrección gramatical usando TextBlob
        """
        prompt = result['processed_prompt']
        corrected = TextBlob(prompt).correct()
        
        if str(corrected) != prompt:
            result['issues'].append('grammatical_errors')
            result['suggestions'].append({
                'type': 'grammar',
                'original': prompt,
                'corrected': str(corrected)
            })
            result['processed_prompt'] = str(corrected)
        
        return result

    @staticmethod
    def detect_harmful_language(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detección de lenguaje dañino o inapropiado
        """
        prompt = result['processed_prompt']
        
        # Verificación de profanidad
        profanity_score = predict([prompt])[0]
        
        if profanity_score > 0.5:
            result['issues'].append('harmful_language')
            result['risk_level'] = 'high'
            result['suggestions'].append({
                'type': 'language_filter',
                'recommendation': 'Utilice un lenguaje más respetuoso y constructivo'
            })
        
        # Detección de contenido sensible
        sensitive_keywords = [
            'violencia', 'discriminación', 'odio', 
            'contenido sexual explicito', 'autolesión'
        ]
        
        for keyword in sensitive_keywords:
            if keyword in prompt.lower():
                result['issues'].append('sensitive_content')
                result['risk_level'] = 'critical'
                result['suggestions'].append({
                    'type': 'content_warning',
                    'recommendation': f'El prompt contiene palabras sensibles relacionadas con {keyword}'
                })
        
        return result

    @staticmethod
    def validate_prompt_completeness(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validación de la completitud del prompt
        """
        prompt = result['processed_prompt']
        doc = nlp(prompt)
        
        # Verificar longitud mínima
        if len(prompt.split()) < 3:
            result['issues'].append('incomplete_prompt')
            result['suggestions'].append({
                'type': 'completeness',
                'recommendation': 'El prompt es demasiado corto. Proporcione más contexto.'
            })
        
        # Verificar estructura gramatical
        if not any(token.pos_ in ['VERB', 'NOUN'] for token in doc):
            result['issues'].append('unclear_structure')
            result['suggestions'].append({
                'type': 'clarity',
                'recommendation': 'Incluya verbos o sustantivos clave para mayor claridad'
            })
        
        return result

    @staticmethod
    def preprocess_prompt(prompt: str) -> Dict[str, Any]:
        """
        Función principal de preprocesamiento de prompts
        """
        result = {
            'original_prompt': prompt,
            'processed_prompt': prompt,
            'issues': [],
            'suggestions': [],
            'risk_level': 'low'
        }
        
        # Análisis de seguridad de contenido
        safety_analysis = PromptPreprocessor.analyze_content_safety(prompt)
        
        if not safety_analysis['is_safe']:
            result['issues'].append('content_safety_risk')
            result['risk_level'] = 'critical'
            result['safety_details'] = safety_analysis['details']
            
            return result
        
        # Mejora de prompt con OpenAI
        enhanced_prompt = PromptPreprocessor.enhance_prompt_with_openai(prompt)
        result['processed_prompt'] = enhanced_prompt
        
        # Corrección gramatical
        result = PromptPreprocessor.grammatical_correction(result)
        
        # Detección de lenguaje dañino
        result = PromptPreprocessor.detect_harmful_language(result)
        
        # Validación de completitud
        result = PromptPreprocessor.validate_prompt_completeness(result)
        
        return result

# Definición de funciones de Azure Functions con decoradores
app = func.FunctionApp()

@app.route(route="preprocess_prompt", methods=["POST"])
def preprocess_prompt_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Función de preprocesamiento de prompts
    """
    try:
        req_body = req.get_json()
        prompt = req_body.get('prompt', '')
        
        if not prompt:
            return func.HttpResponse(
                json.dumps({"error": "Prompt vacío"}),
                status_code=400,
                mimetype="application/json"
            )
        
        processed_result = PromptPreprocessor.preprocess_prompt(prompt)
        
        return func.HttpResponse(
            json.dumps(processed_result),
            status_code=200,
            mimetype="application/json"
        )
    
    except Exception as e:
        logging.error(f"Error en procesamiento: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="validate_prompt", methods=["POST"])
def validate_prompt_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Función de validación específica de prompts
    """
    try:
        req_body = req.get_json()
        prompt = req_body.get('prompt', '')
        
        if not prompt:
            return func.HttpResponse(
                json.dumps({"error": "Prompt vacío"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Validación específica de completitud y estructura
        result = {
            'original_prompt': prompt,
            'processed_prompt': prompt,
            'issues': [],
            'suggestions': []
        }
        
        result = PromptPreprocessor.validate_prompt_completeness(result)
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
    
    except Exception as e:
        logging.error(f"Error en validación: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="detect_language_risks", methods=["POST"])
def detect_language_risks_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    Función de detección de riesgos de lenguaje
    """
    try:
        req_body = req.get_json()
        prompt = req_body.get('prompt', '')
        
        if not prompt:
            return func.HttpResponse(
                json.dumps({"error": "Prompt vacío"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Detección específica de lenguaje dañino
        result = {
            'original_prompt': prompt,
            'processed_prompt': prompt,
            'issues': [],
            'suggestions': [],
            'risk_level': 'low'
        }
        
        result = PromptPreprocessor.detect_harmful_language(result)
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
    
    except Exception as e:
        logging.error(f"Error en detección de riesgos: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )