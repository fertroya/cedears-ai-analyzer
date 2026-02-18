# Guía de Configuración de API Keys Gratuitas

Este proyecto soporta múltiples proveedores de IA, incluyendo opciones **100% gratuitas**.

## 🆓 Opción 1: Google Gemini (RECOMENDADO - Gratis)

### Ventajas
- ✅ Completamente gratis
- ✅ No requiere tarjeta de crédito
- ✅ 60 requests por minuto
- ✅ Fácil de configurar
- ✅ Buena calidad de análisis

### Cómo obtener tu API key

1. Ve a [Google AI Studio](https://aistudio.google.com/)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en "Get API key" o "Create API key"
4. Copia la API key generada
5. Agrega a tu archivo `.env`:
   ```bash
   GEMINI_API_KEY=tu_api_key_aqui
   ```
6. En `config/config.yaml` asegúrate de tener:
   ```yaml
   ai:
     api_provider: "gemini"
     model: "gemini-1.5-flash"  # Modelo gratuito
   ```

### Modelos disponibles
- `gemini-1.5-flash` - Gratis, rápido, recomendado
- `gemini-2.5-flash` - Gratis, mejor calidad

---

## 🆓 Opción 2: Ollama (Gratis - Local)

### Ventajas
- ✅ 100% gratis y sin límites
- ✅ Privacidad total (corre localmente)
- ✅ Sin necesidad de internet después de instalar
- ✅ Múltiples modelos disponibles

### Desventajas
- ⚠️ Requiere instalación local
- ⚠️ Necesita recursos de tu computadora
- ⚠️ Primera descarga de modelos puede ser grande

### Instalación

#### macOS
```bash
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Windows
Descarga desde [ollama.ai](https://ollama.ai/)

### Configuración

1. Inicia Ollama:
   ```bash
   ollama serve
   ```

2. Descarga un modelo (opciones recomendadas):
   ```bash
   ollama pull llama3        # Modelo general (4.7GB)
   ollama pull mistral        # Alternativa más pequeña (4.1GB)
   ollama pull codellama      # Mejor para código/análisis técnico
   ```

3. En `config/config.yaml`:
   ```yaml
   ai:
     api_provider: "ollama"
     model: "llama3"  # o "mistral", "codellama"
     ollama_base_url: "http://localhost:11434"
   ```

4. No necesitas API key en `.env` para Ollama

### Verificar que funciona
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Hola"
}'
```

---

## 🆓 Opción 3: Hugging Face (Gratis con límites)

### Ventajas
- ✅ Gratis con tier gratuito
- ✅ Miles de modelos disponibles
- ✅ Sin tarjeta de crédito inicialmente

### Desventajas
- ⚠️ Límites de rate en tier gratuito
- ⚠️ Puede requerir tarjeta para algunos modelos

### Cómo obtener tu token

1. Ve a [Hugging Face](https://huggingface.co/)
2. Crea una cuenta o inicia sesión
3. Ve a [Settings > Access Tokens](https://huggingface.co/settings/tokens)
4. Crea un nuevo token con permisos de lectura
5. Agrega a tu `.env`:
   ```bash
   HUGGINGFACE_API_KEY=tu_token_aqui
   ```
6. En `config/config.yaml`:
   ```yaml
   ai:
     api_provider: "huggingface"
     model: "meta-llama/Llama-3-8b"  # Ejemplo
   ```

---

## 💰 Opción 4: OpenAI (Pago)

Si prefieres usar OpenAI (GPT-4 o GPT-3.5):

1. Ve a [platform.openai.com](https://platform.openai.com/)
2. Crea una cuenta
3. Ve a API Keys y crea una nueva
4. Agrega a tu `.env`:
   ```bash
   OPENAI_API_KEY=sk-tu_api_key_aqui
   ```
5. En `config/config.yaml`:
   ```yaml
   ai:
     api_provider: "openai"
     model: "gpt-3.5-turbo"  # Más económico que gpt-4
   ```

---

## Comparación Rápida

| Proveedor | Costo | Calidad | Facilidad | Privacidad |
|-----------|-------|---------|-----------|------------|
| **Gemini** | 🆓 Gratis | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Ollama** | 🆓 Gratis | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Hugging Face** | 🆓 Gratis* | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **OpenAI** | 💰 Pago | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

*Con límites de rate

## Recomendación

Para empezar rápidamente: **Google Gemini** (Opción 1)
- Es gratis
- Fácil de configurar
- Buena calidad
- No requiere instalación

Para máxima privacidad: **Ollama** (Opción 2)
- Corre completamente local
- Sin límites
- Requiere más setup inicial
