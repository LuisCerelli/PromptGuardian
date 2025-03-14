## 📝 Proyecto: AI-Prompt-Validator  

### 📌 **Objetivo del Proyecto**  

El objetivo de este proyecto es diseñar un **sistema que valide y corrija los prompts antes de enviarlos a la IA**. Esto ayuda a optimizar las respuestas generadas, asegurando que sean **claras, conformes y libres de riesgos potenciales** (por ejemplo, sesgo, lenguaje dañino o datos sensibles).  

Para lograr esto, configuramos diferentes servicios en **Azure** y creamos una **arquitectura backend** basada en **Azure Functions** y **Azure OpenAI**.  

---

## ⚙️ **Configuración Paso a Paso**  

### 1️⃣ **Crear escenario en Python/local**
```
# Crear proyecto de Functions
func init myFunctionApp --worker-runtime python

# Entrar al directorio
cd myFunctionApp
```
- Debe quedar esta estructura: 
```
myFunctionApp/
├── .venv/
├── function_app.py
├── requirements.txt
└── local.settings.json
```
### 2️⃣ **Actualizamos el Homebrew (solo para Linux/Mac) e instalamos CLI y CORE TOOLS de Azure**
```
# Instalar Azure CLI
brew update
brew install azure-cli

# Instalar Azure Functions Core Tools
brew tap azure/functions
# Linux/Mac:
brew install azure-functions-core-tools@4 --unsafe-perm true
# Windows:
npm install -g azure-functions-core-tools@4 #Windows
choco install azure-functions-core-tools-4  # considerar también ai usa Chocolatey

# Verificar instalaciones
az --version
func --version
```

### 3️⃣ **Crear Azure Function App**  
💡 **Función principal donde correrá nuestra validación.**  

1. Iniciar sesión en Azure: 
```
az login
```
2. Crear proyecto de Functions: 
```
# Crear directorio del proyecto
mkdir azure-python-demo
cd azure-python-demo

# Inicializar proyecto de Azure Functions
func init . --worker-runtime python
```
3. Codigo en `function_app.py`:
```
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
```
### **Endpoints en el script:**
#### `/preprocess_prompt`(POST)

- Función: preprocess_prompt
- Descripción: Preprocesamiento completo del prompt
- Acciones:
    - Análisis de seguridad de contenido
    - Mejora del prompt con OpenAI
    - Corrección gramatical
    - Detección de lenguaje dañino
    - Validación de completitud
    
#### `/validate_prompt` (POST)

- Función: validate_prompt
- Descripción: Validación específica de la estructura del prompt
- Acciones:
    - Verificar longitud del prompt
    - Analizar estructura gramatical
    - Sugerir mejoras de claridad

#### `/detect_language_risks` (POST)

- Función: detect_language_risks
- Descripción: Detección de riesgos de lenguaje
- Acciones:
    - Identificar lenguaje dañino
    - Detectar posibles sesgos
    - Evaluar nivel de riesgo

4. Archivo `requirements.txt`:
```
azure-functions==1.17.0
azure-ai-contentsafety==1.0.0
openai==1.3.0
spacy==3.5.2
textblob==0.17.1
profanity-check==1.0.7
https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.5.0/es_core_news_sm-3.5.0-py3-none-any.whl
python-dotenv==1.0.0
setuptools
wheel
```

5. Archivo `host.json`:
```
{
    "version": "2.0",
    "logging": {
        "applicationInsights": {
            "samplingSettings": {
                "isEnabled": true,
                "excludedTypes": "Request"
            }
        }
    },
    "extensionBundle": {
        "id": "Microsoft.Azure.Functions.ExtensionBundle",
        "version": "[3.*, 4.0.0)"
    }
}
```
6. Archivo `local.settings.json`:
```
{
    "IsEncrypted": false,
    "Values": {
        "AzureWebJobsStorage": "",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "OPENAI_API_KEY": "tu_clave_de_openai",
        "AZURE_CONTENT_SAFETY_ENDPOINT": "tu_endpoint_de_content_safety",
        "AZURE_CONTENT_SAFETY_KEY": "tu_clave_de_content_safety",
        "SPACY_MODEL": "es_core_news_sm"  // Añadido para referencia del modelo
    }
}
```
7. Archivo `.gitignore`: 
```
venv/
__pycache__/
*.pyc
.env
local.settings.json
```
8. Crear recursos de Azure: 
```
 # Crear grupo de recursos
# Añadir región como variable
REGION="eastus"
az group create --name MyPythonFunctionsGroup --location $REGION

# Crear cuenta de storage (requerida para Functions)
az storage account create \
    --name mystorageaccount$RANDOM \
    --location eastus \
    --resource-group MyPythonFunctionsGroup \
    --sku Standard_LRS

# Crear Function App
az functionapp create \
    --resource-group MyPythonFunctionsGroup \
    --consumption-plan-location eastus \
    --runtime python \
    --runtime-version 3.9 \
    --functions-version 4 \
    --name mypythonfunctionapp$RANDOM \
    --storage-account mystorageaccount$RANDOM
```
9. Crear entorno virtual y descargar spacy:
```
# Antes de activar, asegurarse de tener la última versión de pip
python -m pip install --upgrade pip
```
```
# Crear entorno
python -m venv venv

# Activar
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar modelo de spaCy
python -m spacy download es_core_news_sm
```
10. Validar función
```
func validate
```
11. Probar localmente:
```
func start
```
12. Desplegar en Azure:
```
# Publicar Function App
func azure functionapp publish mypythonfunctionapp
# Tambien se podria añadir flag para mostrar mas detalles:
# func azure functionapp publish mypythonfunctionapp --verbose (opcional)
```


