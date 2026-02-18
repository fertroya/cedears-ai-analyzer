"""
Motor de recomendaciones usando IA para análisis de CEDEARS.
"""

import logging
from typing import Dict, List
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Genera recomendaciones de inversión usando IA."""
    
    def __init__(self, config: Dict):
        self.config = config
        ai_config = config.get('ai', {})
        
        self.client = OllamaClient(
            base_url=ai_config.get('ollama_base_url', 'http://localhost:11434'),
            model=ai_config.get('model', 'llama3')
        )
        
        self.temperature = ai_config.get('temperature', 0.7)
        self.max_tokens = ai_config.get('max_tokens', 2000)
        self.risk_profile = config.get('risk_profile', {})
    
    def analyze_cedear(
        self,
        ticker: str,
        analysis_data: Dict,
        news: List[Dict],
        market_context: Dict
    ) -> Dict:
        """
        Analiza un CEDEAR y genera recomendación.
        
        Args:
            ticker: Símbolo del CEDEAR
            analysis_data: Datos de análisis técnico
            news: Noticias relacionadas
            market_context: Contexto de mercado
        
        Returns:
            Dict con recomendación y análisis
        """
        logger.info(f"Generando recomendación para {ticker}...")
        
        # Construir prompt para IA
        prompt = self._build_analysis_prompt(ticker, analysis_data, news, market_context)
        
        # Generar análisis con IA
        ai_response = self.client.generate(
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        if not ai_response:
            logger.warning(f"No se pudo obtener respuesta de IA para {ticker}")
            return self._default_recommendation(ticker, analysis_data)
        
        # Parsear respuesta y generar recomendación estructurada
        recommendation = self._parse_ai_response(ticker, analysis_data, ai_response)
        
        return recommendation
    
    def _build_analysis_prompt(
        self,
        ticker: str,
        analysis_data: Dict,
        news: List[Dict],
        market_context: Dict
    ) -> str:
        """Construye el prompt para análisis con IA."""
        
        # Resumir noticias
        news_summary = "\n".join([
            f"- {n.get('title', '')}: {n.get('summary', '')}"
            for n in news[:5]  # Top 5 noticias
        ]) if news else "No hay noticias recientes disponibles."
        
        prompt = f"""Eres un analista financiero experto en CEDEARS del mercado argentino. 
Analiza el siguiente CEDEAR y proporciona una recomendación de inversión para corto plazo (1-2 semanas).

CEDEAR: {ticker}
Precio actual: ${analysis_data.get('current_price', 'N/A')}

INDICADORES TÉCNICOS:
- RSI: {analysis_data.get('rsi', 'N/A')} (sobrecomprado si >70, sobrevendido si <30)
- MACD: {analysis_data.get('macd', {}).get('value', 'N/A')}
- Tendencia: {analysis_data.get('trend', {}).get('trend', 'N/A')} (fuerza: {analysis_data.get('trend', {}).get('strength', 0)})
- Momentum 7 días: {analysis_data.get('momentum', {}).get('7d', 0)}%
- Momentum 30 días: {analysis_data.get('momentum', {}).get('30d', 0)}%
- Soporte: ${analysis_data.get('support_resistance', {}).get('support', 'N/A')}
- Resistencia: ${analysis_data.get('support_resistance', {}).get('resistance', 'N/A')}
- Volumen: {analysis_data.get('volume', {}).get('trend', 'N/A')}

CONTEXTO DE MERCADO:
- Dólar MEP: ${market_context.get('dolar_mep', 'N/A')}
- Dólar CCL: ${market_context.get('dolar_ccl', 'N/A')}
- Riesgo País: {market_context.get('riesgo_pais', 'N/A')} puntos
- MERVAL: {market_context.get('merval', 'N/A')}

NOTICIAS RECIENTES:
{news_summary}

PERFIL DE INVERSOR: Moderado-Riesgoso (Argentina)
HORIZONTE: Corto plazo (1-2 semanas)

Proporciona tu análisis en el siguiente formato JSON:
{{
  "recommendation": "COMPRAR" | "VENDER" | "MANTENER",
  "confidence": 0.0-1.0,
  "reasoning": "Explicación breve de la recomendación",
  "key_factors": ["factor1", "factor2", "factor3"],
  "price_target": precio_objetivo_si_aplica,
  "risk_level": "BAJO" | "MEDIO" | "ALTO"
}}

Responde SOLO con el JSON, sin texto adicional."""

        return prompt
    
    def _parse_ai_response(self, ticker: str, analysis_data: Dict, ai_response: str) -> Dict:
        """Parsea la respuesta de IA y estructura la recomendación."""
        import json
        import re
        
        # Intentar extraer JSON de la respuesta
        try:
            # Buscar JSON en la respuesta
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                # Si no hay JSON, intentar parsear toda la respuesta
                parsed = json.loads(ai_response)
        except:
            # Si falla el parsing, generar recomendación basada en indicadores
            logger.warning(f"No se pudo parsear respuesta de IA para {ticker}, usando análisis técnico")
            return self._generate_technical_recommendation(ticker, analysis_data)
        
        # Validar y completar recomendación
        recommendation = {
            'ticker': ticker,
            'action': parsed.get('recommendation', 'MANTENER').upper(),
            'confidence': float(parsed.get('confidence', 0.5)),
            'reasoning': parsed.get('reasoning', 'Análisis técnico y de mercado'),
            'key_factors': parsed.get('key_factors', []),
            'price_target': parsed.get('price_target'),
            'risk_level': parsed.get('risk_level', 'MEDIO'),
            'current_price': analysis_data.get('current_price'),
            'ai_analysis': ai_response[:500]  # Primeros 500 caracteres
        }
        
        return recommendation
    
    def _generate_technical_recommendation(self, ticker: str, analysis_data: Dict) -> Dict:
        """Genera recomendación basada solo en análisis técnico si falla IA."""
        rsi = analysis_data.get('rsi')
        trend = analysis_data.get('trend', {}).get('trend', 'sideways')
        momentum_7d = analysis_data.get('momentum', {}).get('7d', 0)
        
        # Lógica simple basada en indicadores
        if rsi and rsi < 30 and trend == 'bullish':
            action = 'COMPRAR'
            confidence = 0.7
        elif rsi and rsi > 70 and trend == 'bearish':
            action = 'VENDER'
            confidence = 0.7
        elif momentum_7d > 5:
            action = 'COMPRAR'
            confidence = 0.6
        elif momentum_7d < -5:
            action = 'VENDER'
            confidence = 0.6
        else:
            action = 'MANTENER'
            confidence = 0.5
        
        return {
            'ticker': ticker,
            'action': action,
            'confidence': confidence,
            'reasoning': f'Basado en análisis técnico: RSI={rsi}, Tendencia={trend}, Momentum={momentum_7d}%',
            'key_factors': ['RSI', 'Tendencia', 'Momentum'],
            'price_target': None,
            'risk_level': 'MEDIO',
            'current_price': analysis_data.get('current_price')
        }
    
    def _default_recommendation(self, ticker: str, analysis_data: Dict) -> Dict:
        """Recomendación por defecto cuando falla todo."""
        return {
            'ticker': ticker,
            'action': 'MANTENER',
            'confidence': 0.3,
            'reasoning': 'Datos insuficientes para análisis',
            'key_factors': [],
            'price_target': None,
            'risk_level': 'ALTO',
            'current_price': analysis_data.get('current_price')
        }
