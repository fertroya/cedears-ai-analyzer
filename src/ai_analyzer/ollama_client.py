"""
Cliente para interactuar con Ollama API.
"""

import requests
import logging
import json
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class OllamaClient:
    """Cliente para Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url.rstrip('/')
        self.model = model
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        """
        Genera texto usando Ollama.
        
        Args:
            prompt: Prompt para el modelo
            temperature: Temperatura para generación (0.0-1.0)
            max_tokens: Máximo de tokens a generar
        
        Returns:
            Texto generado o None si hay error
        """
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en llamada a Ollama: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en Ollama: {e}")
            return None
    
    def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        """
        Genera respuesta usando formato de chat.
        
        Args:
            messages: Lista de mensajes en formato [{"role": "user", "content": "..."}]
            temperature: Temperatura para generación
            max_tokens: Máximo de tokens
        
        Returns:
            Respuesta del modelo o None si hay error
        """
        try:
            url = f"{self.base_url}/api/chat"
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get('message', {}).get('content', '')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en chat de Ollama: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado en chat de Ollama: {e}")
            return None
