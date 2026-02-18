# CEDEARS AI Analyzer

Herramienta de análisis de inversión en CEDEARS usando IA para generar recomendaciones semanales de compra/venta para inversores de perfil moderado-riesgoso en Argentina.

## Características

- 📊 Análisis automático de los CEDEARS más líquidos del mercado argentino
- 🤖 Análisis con IA de tendencias, indicadores técnicos y contexto de mercado
- 📈 Recomendaciones semanales de COMPRAR/VENDER/MANTENER
- 📧 Envío automático de reportes por email
- 🔄 Ejecución semanal automatizada

## Requisitos

- Python 3.9+
- Acceso a internet para web scraping
- **API key gratuita** (Google Gemini recomendado) o API key de OpenAI
- Credenciales SMTP para envío de emails

### 🆓 Opciones Gratuitas de IA

Este proyecto soporta múltiples proveedores de IA **gratuitos**:
- **Google Gemini** (recomendado) - Gratis, sin tarjeta de crédito
- **Ollama** - Gratis, corre localmente
- **Hugging Face** - Gratis con límites

Ver [docs/API_KEYS_SETUP.md](docs/API_KEYS_SETUP.md) para instrucciones detalladas.

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/fertroya/cedears-ai-analyzer.git
cd cedears-ai-analyzer

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

## Configuración

1. **Configura tu API de IA (GRATIS recomendado)**:
   - Lee [docs/API_KEYS_SETUP.md](docs/API_KEYS_SETUP.md) para opciones gratuitas
   - **Opción rápida**: Obtén tu API key de Google Gemini en [aistudio.google.com](https://aistudio.google.com/)

2. Copia `.env.example` a `.env` y completa las variables:
   - `GEMINI_API_KEY` (recomendado - gratis) o `OPENAI_API_KEY`
   - `SENDER_EMAIL` y `SENDER_PASSWORD` (SMTP)
   - `RECIPIENT_EMAIL`

3. Edita `config/config.yaml`:
   - Configura `ai.api_provider` según tu elección (por defecto: "gemini")
   - Ajusta otros parámetros según tus preferencias

4. Revisa `config/cedears_list.yaml` para ajustar la lista de CEDEARS a analizar

## Uso

### Ejecución manual

```bash
python main.py
```

### Ejecución programada (semanal)

El scheduler ejecutará automáticamente el análisis cada lunes a las 9:00 AM.

```bash
python -m src.scheduler.weekly_job
```

## Estructura del Proyecto

```
cedears-ai-analyzer/
├── src/
│   ├── data_collector/      # Web scraping de datos
│   ├── data_processor/       # Indicadores técnicos y análisis
│   ├── ai_analyzer/          # Análisis con IA
│   ├── report_generator/     # Generación de reportes
│   ├── email_service/        # Envío de emails
│   ├── database/             # Modelos y gestión de BD
│   └── scheduler/            # Programación de tareas
├── config/                   # Archivos de configuración
├── data/                     # Base de datos local
└── main.py                   # Punto de entrada
```

## Disclaimer

⚠️ **IMPORTANTE**: Este análisis es meramente informativo y no constituye asesoramiento financiero. Las decisiones de inversión son responsabilidad del usuario. Siempre consulta con un asesor financiero profesional antes de tomar decisiones de inversión.

## Licencia

MIT License

## Autor

fertroya@gmail.com
