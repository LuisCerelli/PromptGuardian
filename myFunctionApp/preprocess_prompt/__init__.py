import logging
import json
import os
import azure.functions as func
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI


# Configuración de logging
logging.basicConfig(level=logging.INFO)

# 🔹 Cargar credenciales desde variables de entorno
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

CONTENT_SAFETY_KEY = os.getenv("AZURE_CONTENT_SAFETY_KEY")
CONTENT_SAFETY_ENDPOINT = os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT")
logging.info(CONTENT_SAFETY_ENDPOINT)

# 🔹 Verificar si todas las variables están definidas
if not all([OPENAI_API_KEY, OPENAI_ENDPOINT, OPENAI_DEPLOYMENT, OPENAI_API_VERSION,
            CONTENT_SAFETY_KEY, CONTENT_SAFETY_ENDPOINT]):
    raise ValueError("❌ Faltan variables de entorno. Verifica la configuración en Azure.")

def analyze_content_safety(text):
    try:
        logging.info(f"ENDPOINT: {CONTENT_SAFETY_ENDPOINT}")
        client = ContentSafetyClient(
            endpoint=CONTENT_SAFETY_ENDPOINT,
            credential=AzureKeyCredential(CONTENT_SAFETY_KEY),
            api_version="2024-09-01"
        )
        response = client.analyze_text(AnalyzeTextOptions(text=text))

        # 👇 DEBUG: imprime toda la respuesta del servicio
        logging.info(f"🔍 Resultado completo de Content Safety: {response}")
        
        # 👇 Forzamos logging detallado de cada categoría
        if "categoriesAnalysis" in response:
            for item in response["categoriesAnalysis"]:
                logging.info(f"📌 Categoría: {item['category']} - Severidad: {item['severity']}")

        return [item["category"] for item in response["categoriesAnalysis"]]

    except Exception as e:
        logging.error(f"❌ Error en Content Safety: {str(e)}")
        return []


def analyze_with_openai(prompt):
    """🔹 Usa Azure OpenAI para corregir errores ortográficos sin alterar la intención original."""
    try:
        client = AzureOpenAI(
            api_key=OPENAI_API_KEY,
            api_version=OPENAI_API_VERSION,
            azure_endpoint=OPENAI_ENDPOINT
)
        response = client.chat.completions.create(
            model=OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "Corrige los errores ortográficos y gramaticales en la pregunta del usuario sin cambiar su significado original. No elimines ni reemplaces palabras clave como 'AI', 'inteligencia artificial', 'machine learning', 'EE.UU.', 'CIA', 'datos', 'seguridad', etc. Si el usuario hace una pregunta confusa, corrige la gramática y la ortografía pero mantén el significado. Devuelve únicamente la pregunta corregida, sin agregar explicaciones ni comentarios adicionales."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1, # Super bajo para evitar creatividad innecesaria 
            max_tokens=50 # Mantener la respuesta corta y precisa 
        )

        logging.info(f"📌 OpenAI respuesta: {response.choices[0].message.content}")
        return response.choices[0].message.content if response.choices else prompt

    except Exception as e:
        logging.error(f"❌ Error en OpenAI: {str(e)}")
        return prompt  # Retorna el prompt original si OpenAI falla

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("📌 La función preprocess_prompt fue invocada.")

    try:
        req_body = req.get_json()
        logging.info(f"📌 Cuerpo de la petición: {req_body}")

        prompt = req_body.get("prompt", "")
        if not prompt:
            logging.warning("⚠️ No se recibió un prompt válido.")
            return func.HttpResponse(
                json.dumps({"error": "Prompt no proporcionado"}),
                status_code=400,
                mimetype="application/json"
            )

        logging.info(f"📌 Prompt recibido: {prompt}")

        # 🔹 Análisis de contenido inapropiado
        categories = analyze_content_safety(prompt)
        logging.info(f"✅ Categorías detectadas por Content Safety: {categories}")
        if categories:
            logging.warning(f"⚠️ El prompt contiene contenido sensible: {categories}")
    
            # 🚨 Si la categoría de riesgo es alta, bloqueamos el prompt
            if any(cat in ["Fraude", "Hacking", "Violencia"] for cat in categories):
                return func.HttpResponse(
                    json.dumps({"error": "El prompt contiene contenido no permitido.", "categories_detected": categories}),
                    status_code=400,
                    mimetype="application/json"
                )

            # ✅ Si el contenido es moderadamente riesgoso, lo reformulamos
            sanitized_prompt = analyze_with_openai(f"Reformula esta pregunta para que sea ética y segura: {prompt}")

            return func.HttpResponse(
                json.dumps({"original_prompt": prompt, "sanitized_prompt": sanitized_prompt, "categories_detected": categories}),
                status_code=200,
                mimetype="application/json"
            )


        # 🔹 Análisis y mejora del prompt con OpenAI
        improved_prompt = analyze_with_openai(prompt)

        return func.HttpResponse(
            json.dumps({"original_prompt": prompt, "processed_prompt": improved_prompt}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"❌ Error en la función: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
