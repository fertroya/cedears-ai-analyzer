#!/usr/bin/env python3
"""
Main entry point for CEDEARS AI Analyzer.
Executes the weekly analysis workflow.
"""

import logging
import sys
import yaml
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from src.utils.ollama_setup import ensure_ollama_ready

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cedears_analyzer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def load_config():
    """Carga la configuración desde config.yaml."""
    config_path = Path(__file__).parent / "config" / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("CEDEARS AI Analyzer - Weekly Analysis")
    logger.info(f"Execution started at: {datetime.now()}")
    logger.info("=" * 60)
    
    try:
        # Cargar configuración
        config = load_config()
        ai_config = config.get('ai', {})
        api_provider = ai_config.get('api_provider', 'ollama')
        
        # Verificar Ollama si es el proveedor seleccionado
        if api_provider == 'ollama':
            logger.info("Verificando configuración de Ollama...")
            model = ai_config.get('model', 'llama3')
            base_url = ai_config.get('ollama_base_url', 'http://localhost:11434')
            auto_install = ai_config.get('ollama_auto_install', True)
            auto_download = ai_config.get('ollama_auto_download_model', True)
            
            if not ensure_ollama_ready(
                model=model,
                base_url=base_url,
                auto_install=auto_install,
                auto_download_model=auto_download
            ):
                logger.error("Ollama no está listo. Por favor, ejecuta:")
                logger.error("  bash scripts/setup_ollama.sh")
                logger.error("O instala Ollama manualmente desde https://ollama.com")
                sys.exit(1)
        
        # TODO: Implement main workflow
        # 1. Collect data
        # 2. Process data
        # 3. AI analysis
        # 4. Generate report
        # 5. Send email
        
        logger.info("Analysis workflow will be implemented in next steps")
        logger.info("=" * 60)
        logger.info("Execution completed successfully")
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
