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
- **Ollama** (instalación automática incluida) - 100% gratis, corre localmente
- Credenciales SMTP para envío de emails

### 🤖 IA con Ollama (Por Defecto)

Este proyecto usa **Ollama** por defecto, que es:
- ✅ **100% gratis** - Sin límites ni costos
- ✅ **Privacidad total** - Corre completamente local
- ✅ **Instalación automática** - El proyecto se encarga de instalarlo
- ✅ **Sin API keys** - No necesitas credenciales externas

Ollama se instalará automáticamente la primera vez que ejecutes el proyecto.

### 🔄 Otras Opciones de IA

También puedes usar otros proveedores editando `config/config.yaml`:
- **Google Gemini** - Gratis, sin tarjeta de crédito
- **Hugging Face** - Gratis con límites
- **OpenAI** - Pago

Ver [docs/API_KEYS_SETUP.md](docs/API_KEYS_SETUP.md) para instrucciones detalladas.

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/fertroya/cedears-ai-analyzer.git
cd cedears-ai-analyzer

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias Python
pip install -r requirements.txt

# Instalar y configurar Ollama (automático)
bash scripts/setup_ollama.sh

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de email (SMTP)
```

### Instalación Rápida de Ollama

Si prefieres instalar Ollama manualmente:

**macOS:**
```bash
brew install ollama
ollama serve  # Iniciar servicio
ollama pull llama3  # Descargar modelo por defecto
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve  # Iniciar servicio
ollama pull llama3  # Descargar modelo por defecto
```

**Windows:**
Descarga desde [ollama.com/download](https://ollama.com/download) e instala manualmente.

## Configuración

1. **Ollama está configurado por defecto** - No necesitas API keys
   - El proyecto verificará e instalará Ollama automáticamente al ejecutar
   - Si prefieres otro proveedor, edita `config/config.yaml` y cambia `ai.api_provider`

2. Copia `.env.example` a `.env` y completa las variables:
   - `SENDER_EMAIL` y `SENDER_PASSWORD` (SMTP para envío de reportes)
   - `RECIPIENT_EMAIL` (donde recibirás los reportes)
   - Solo necesitas API keys si cambias el proveedor de IA

3. Edita `config/config.yaml` (opcional):
   - `ai.model`: Cambia el modelo de Ollama si lo deseas (por defecto: "llama3")
   - Otros parámetros de análisis según tus preferencias

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
