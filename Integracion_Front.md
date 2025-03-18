# 📌 Integración del Frontend con Azure Function

## 🔹 **Endpoint de la API**
```plaintext
https://myfunctionapphackathonmarzo2025.azurewebsites.net/api/preprocess_prompt
```

---

## 🔹 **Método HTTP**
**`POST`**

---

## 🔹 **Autenticación y Obtención del Código de Acceso**
Azure Functions puede requerir una clave de acceso (`code`) si el `authLevel` no está configurado como `"anonymous"`.  
Para obtener esta clave, puedes ejecutar el siguiente comando en **Azure CLI**:

```sh
az functionapp keys list --name functionforhackmar25 --resource-group equipo3 --query "functionKeys.default" --output tsv
```

Una vez obtenida la clave, debes agregarla a las solicitudes a la API como un parámetro en la URL:

```plaintext
https://myfunctionapphackathonmarzo2025.azurewebsites.net/api/preprocess_prompt?code=TU_CODIGO_DE_ACCESO
```

Si en el futuro la autenticación se configura como `"anonymous"`, este parámetro ya no será necesario.

---

## 🔹 **Headers requeridos**
```json
{
  "Content-Type": "application/json"
}
```

---

## 🔹 **Body de la solicitud (JSON)**
```json
{
  "prompt": "Quiero aprender machine learning"
}
```

---

## 🔹 **Respuesta esperada (JSON)**
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

---

