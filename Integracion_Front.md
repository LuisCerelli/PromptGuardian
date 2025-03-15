# Integración del Frontend con Azure Function

## 🔹 Endpoint de la API
```plaintext
https://myfunctionapphackathonmarzo2025.azurewebsites.net/api/preprocess_prompt
```

## 🔹 Método HTTP
**`POST`**

## 🔹 Headers requeridos
```json
{
  "Content-Type": "application/json"
}
```

## 🔹 Body de la solicitud (JSON)
```json
{
  "prompt": "Quiero aprender machine learning"
}
```

## 🔹 Respuesta esperada (JSON)
```json
{
    "original_prompt": "Quiero aprender machine learning",
    "processed_prompt": "Quiero aprender machine learning",
    "issues": [],
    "suggestions": [
        "Profundice en los conceptos fundamentales.",
        "Considere incluir ejemplos prácticos para una mejor comprensión."
    ],
    "risk_level": "low",
    "intention": ["learning"],
    "context": "technical",
    "complexity": {
        "word_count": 4,
        "unique_words": 4,
        "technical_words": 1,
        "complexity_level": "basic",
        "depth": "simple"
    }
}
```





