# Prompt Preprocessor: Sistema Inteligente de Validación de Prompts

## 🎯 Objetivo
Diseñar un sistema de preprocesamiento de prompts que:
- Valide y corrija entradas antes de enviarlas a modelos de IA
- Optimice la calidad y seguridad de las generaciones
- Mitigue riesgos potenciales en la interacción con IA

## 🛡️ Características Principales
- Corrección gramatical automática
- Detección de lenguaje dañino o inapropiado
- Evaluación de sesgos y contenido sensible
- Mejora de la claridad y precisión de prompts

## 🏗️ Arquitectura
- **Backend:** Azure Functions
- **Servicios de Seguridad:** 
  * Azure Content Safety
  * OpenAI (Modelo GPT para mejora de prompts)
- **Procesamiento de Lenguaje:** 
  * spaCy
  * TextBlob

## 🔒 Componentes de Seguridad
- Análisis de riesgos de contenido
- Filtrado de lenguaje inapropiado
- Sugerencias de alternativas éticas y constructivas
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
├── function_app.py
├── host.json
├── local.settings.json
└── requirements.txt
```
### 2️⃣ **Actualizamos el Homebrew (solo para Linux/Mac) e instalamos CLI y CORE TOOLS de Azure**
```
# Instalar Azure CLI
brew update
brew install azure-cli
```
```
# Instalar Azure Functions Core Tools
brew tap azure/functions
# Linux/Mac:
brew install azure-functions-core-tools@4 
# Windows:
npm install -g azure-functions-core-tools@4 #Windows
choco install azure-functions-core-tools-4  # considerar también si usa Chocolatey
```
```
# Verificar instalaciones
az --version
func --version
```
### 3️⃣ **Completamos los archivos:**

1. Codigo en `function_app.py`:
```
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

@app.route(route="preprocess_prompt", methods=["POST"])
def preprocess_prompt_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        prompt = req_body.get('prompt', '')
        
        if not prompt:
            return func.HttpResponse(
                json.dumps({"error": "Prompt vacío"}),
                status_code=400,
                mimetype="application/json"
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
        
        return func.HttpResponse(
            json.dumps(result),
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
```
### **Acciones:**

- Verifica si el prompt contiene lenguaje inapropiado.
- Detecta la intención del prompt.
- Identifica el contexto del prompt.
- Analiza la complejidad del prompt.
- Genera sugerencias de mejora.
- Asigna un nivel de riesgo basado en el contenido del prompt.


2. Archivo `requirements.txt`:
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

3. Archivo `host.json`:
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
4. Archivo `local.settings.json`:
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
5. Agregarle al archivo `.gitignore`: 
```

*.pyc

```
### 4️⃣ **Crear Azure Function App**  
💡 **Función principal donde correrá nuestra validación.**  

1. Iniciar sesión en Azure: 
```
az login
```
2. Crear recursos de Azure: 
```
 # Crear grupo de recursos
# Añadir región como variable, elegimos 'eastus2' ya que soporta el plan flex-consumption(y dentro de él tenemos python)
REGION="eastus2"
az group create --name MyPythonFunctionsGroup --location $REGION
```
```

# Crear cuenta de storage (requerida para Functions)
STORAGE_ACCOUNT="almacenhackathonmarzo"
az storage account create \
    --name $STORAGE_ACCOUNT \
    --location $REGION \
    --resource-group MyPythonFunctionsGroup \
    --sku Standard_LRS

```
```
# A veces hay demasiada latencia y no nos permite continuar con los scripts ya que no llegan a crearse las instancias en el portal, para que ello no suceda, he aqui un scrip que esperará dinamicamente que la cuenta de almacenamiento esté disponible: 

echo "Verificando la cuenta de almacenamiento..."
while ! az storage account show --name $STORAGE_ACCOUNT --resource-group MyPythonFunctionsGroup &>/dev/null; do
    echo "Esperando a que la cuenta de almacenamiento esté disponible..."
    sleep 10
done
echo "Cuenta de almacenamiento detectada, continuando..."
```
```
# Crear el plan de consumo Flex Consumption que, como ya dijimos mas arriba es el que soporta Python
az functionapp plan create \
    --resource-group MyPythonFunctionsGroup \
    --name my-flex-consumption-plan \
    --location $REGION \
    --sku EP1 \
    --is-linux
```
```

# Crear Function App
az functionapp create \
    --resource-group MyPythonFunctionsGroup \
    --plan my-flex-consumption-plan \
    --os-type Linux \
    --runtime python \
    --runtime-version 3.9 \
    --functions-version 4 \
    --name mypythonfunctionapp \
    --storage-account $STORAGE_ACCOUNT
```
3. Verificacion:
```
az functionapp list --resource-group MyPythonFunctionsGroup --query "[].{Name:name, Runtime:siteConfig.linuxFxVersion, OS:reserved}"
```
    . Este comando deberia devolver: 
```
[
  {
    "Name": "mypythonfunctionapp",
    "OS": true,
    "Runtime": "Python|3.9"
  }
]
```

### 5️⃣ **Continuar trabajando en local:**
1. Crear entorno virtual y descargar spacy:
```
# Antes de activar, asegurarse de tener la última versión de pip
python -m pip install --upgrade pip
```
```
# Crear entorno en Python 3.9, en este caso lo instalaré usando "pyenv"
pyenv install 3.9.21
```
```
python -m venv venv
```
```
# Activar en windows:
.\venv\Scripts\activate

# Activar en Linux/Mac:
source venv/bin/activate
```
```
# Instalar dependencias
pip install -r requirements.txt

# Instalar modelo de spaCy
python -m spacy download es_core_news_sm
```
2. Probar localmente:
```
func start
```
### 6️⃣ **Desplegar en Azure:**
```
# Publicar Function App
func azure functionapp publish mypythonfunctionapp
# Tambien se podria añadir flag para mostrar mas detalles:
# func azure functionapp publish mypythonfunctionapp --verbose (opcional)
```
---
