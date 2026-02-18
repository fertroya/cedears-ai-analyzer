"""
Utilidades para verificar e instalar Ollama automáticamente.
"""

import subprocess
import sys
import platform
import time
import requests
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def check_ollama_installed() -> bool:
    """Verifica si Ollama está instalado en el sistema."""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_ollama_running(base_url: str = "http://localhost:11434") -> bool:
    """Verifica si el servicio Ollama está corriendo."""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=2)
        return response.status_code == 200
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        return False


def start_ollama_service() -> bool:
    """Intenta iniciar el servicio Ollama."""
    logger.info("Intentando iniciar servicio Ollama...")
    
    try:
        # Iniciar Ollama en background
        if platform.system() == "Windows":
            subprocess.Popen(
                ["ollama", "serve"],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        # Esperar a que el servicio inicie
        for _ in range(10):
            time.sleep(1)
            if check_ollama_running():
                logger.info("✓ Ollama iniciado exitosamente")
                return True
        
        logger.warning("Ollama no respondió después de 10 segundos")
        return False
        
    except Exception as e:
        logger.error(f"Error al iniciar Ollama: {e}")
        return False


def check_model_available(model: str, base_url: str = "http://localhost:11434") -> bool:
    """Verifica si un modelo está disponible en Ollama."""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return any(m.get("name", "").startswith(model) for m in models)
        return False
    except Exception:
        return False


def download_model(model: str, base_url: str = "http://localhost:11434") -> bool:
    """Descarga un modelo de Ollama."""
    logger.info(f"Descargando modelo: {model}")
    
    try:
        response = requests.post(
            f"{base_url}/api/pull",
            json={"name": model},
            stream=True,
            timeout=300
        )
        
        if response.status_code == 200:
            # Leer el stream para mostrar progreso
            for line in response.iter_lines():
                if line:
                    try:
                        import json
                        data = json.loads(line)
                        if "status" in data:
                            logger.info(f"  {data['status']}")
                    except:
                        pass
            
            logger.info(f"✓ Modelo {model} descargado exitosamente")
            return True
        else:
            logger.error(f"Error al descargar modelo: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error al descargar modelo {model}: {e}")
        return False


def install_ollama() -> bool:
    """Intenta instalar Ollama usando el script de setup."""
    logger.info("Intentando instalar Ollama...")
    
    script_path = Path(__file__).parent.parent.parent / "scripts" / "setup_ollama.sh"
    
    if not script_path.exists():
        logger.error(f"Script de instalación no encontrado: {script_path}")
        return False
    
    try:
        if platform.system() == "Windows":
            logger.error("Instalación automática no soportada en Windows")
            logger.info("Por favor, descarga Ollama desde: https://ollama.com/download")
            return False
        else:
            # Hacer el script ejecutable
            subprocess.run(["chmod", "+x", str(script_path)], check=True)
            
            # Ejecutar script de instalación
            result = subprocess.run(
                ["bash", str(script_path)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✓ Ollama instalado exitosamente")
                return True
            else:
                logger.error(f"Error en instalación: {result.stderr}")
                return False
                
    except Exception as e:
        logger.error(f"Error al ejecutar script de instalación: {e}")
        return False


def ensure_ollama_ready(
    model: str = "llama3",
    base_url: str = "http://localhost:11434",
    auto_install: bool = True,
    auto_download_model: bool = True
) -> bool:
    """
    Asegura que Ollama esté instalado, corriendo y con el modelo disponible.
    
    Args:
        model: Nombre del modelo a verificar/descargar
        base_url: URL base de Ollama
        auto_install: Si True, intenta instalar Ollama si no está presente
        auto_download_model: Si True, descarga el modelo si no está disponible
    
    Returns:
        True si Ollama está listo para usar, False en caso contrario
    """
    # Verificar instalación
    if not check_ollama_installed():
        logger.warning("Ollama no está instalado")
        if auto_install:
            if not install_ollama():
                logger.error("No se pudo instalar Ollama automáticamente")
                logger.info("Por favor, instala Ollama manualmente:")
                logger.info("  macOS: brew install ollama")
                logger.info("  Linux: curl -fsSL https://ollama.com/install.sh | sh")
                logger.info("  Windows: https://ollama.com/download")
                return False
        else:
            logger.error("Ollama no está instalado y auto_install está deshabilitado")
            return False
    
    # Verificar que esté corriendo
    if not check_ollama_running(base_url):
        logger.warning("Ollama no está corriendo. Intentando iniciar...")
        if not start_ollama_service():
            logger.error("No se pudo iniciar Ollama")
            logger.info("Intenta iniciarlo manualmente con: ollama serve")
            return False
    
    # Verificar modelo
    if not check_model_available(model, base_url):
        logger.warning(f"Modelo {model} no está disponible")
        if auto_download_model:
            if not download_model(model, base_url):
                logger.error(f"No se pudo descargar modelo {model}")
                logger.info(f"Intenta descargarlo manualmente con: ollama pull {model}")
                return False
        else:
            logger.error(f"Modelo {model} no está disponible y auto_download_model está deshabilitado")
            return False
    
    logger.info("✓ Ollama está listo para usar")
    return True


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Verificar y configurar Ollama
    success = ensure_ollama_ready()
    sys.exit(0 if success else 1)
