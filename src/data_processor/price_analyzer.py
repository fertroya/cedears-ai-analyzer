"""
Análisis de precios y tendencias de CEDEARS.
"""

import pandas as pd
import logging
from typing import Dict
from .technical_indicators import TechnicalIndicators

logger = logging.getLogger(__name__)


class PriceAnalyzer:
    """Analiza precios y genera insights técnicos."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.indicators = TechnicalIndicators()
    
    def analyze(self, ticker: str, price_data: pd.DataFrame) -> Dict:
        """
        Realiza análisis completo de un CEDEAR.
        
        Args:
            ticker: Símbolo del CEDEAR
            price_data: DataFrame con datos históricos de precios
        
        Returns:
            Dict con análisis completo
        """
        if price_data.empty or len(price_data) < 20:
            logger.warning(f"Datos insuficientes para {ticker}")
            return self._empty_analysis(ticker)
        
        prices = price_data['close']
        
        # Calcular indicadores
        rsi_period = self.config.get('rsi_period', 14)
        rsi = self.indicators.calculate_rsi(prices, rsi_period)
        
        macd_config = self.config.get('macd', {})
        macd = self.indicators.calculate_macd(
            prices,
            fast=macd_config.get('fast', 12),
            slow=macd_config.get('slow', 26),
            signal=macd_config.get('signal', 9)
        )
        
        ma_periods = self.config.get('moving_averages', [20, 50, 200])
        moving_averages = self.indicators.calculate_moving_averages(prices, ma_periods)
        
        trend = self.indicators.analyze_trend(prices)
        support_resistance = self.indicators.identify_support_resistance(prices)
        
        # Calcular momentum
        momentum_1d = self._calculate_momentum(prices, 1)
        momentum_7d = self._calculate_momentum(prices, 7)
        momentum_30d = self._calculate_momentum(prices, 30)
        
        # Análisis de volumen
        volume_analysis = self._analyze_volume(price_data)
        
        return {
            'ticker': ticker,
            'current_price': round(prices.iloc[-1], 2),
            'rsi': round(rsi.iloc[-1], 2) if not rsi.empty else None,
            'macd': {
                'value': round(macd['macd'].iloc[-1], 2) if not macd['macd'].empty else None,
                'signal': round(macd['signal'].iloc[-1], 2) if not macd['signal'].empty else None,
                'histogram': round(macd['histogram'].iloc[-1], 2) if not macd['histogram'].empty else None
            },
            'moving_averages': {
                k: round(v.iloc[-1], 2) if not v.empty else None
                for k, v in moving_averages.items()
            },
            'trend': trend,
            'support_resistance': support_resistance,
            'momentum': {
                '1d': momentum_1d,
                '7d': momentum_7d,
                '30d': momentum_30d
            },
            'volume': volume_analysis,
            'timestamp': pd.Timestamp.now().isoformat()
        }
    
    def _calculate_momentum(self, prices: pd.Series, days: int) -> float:
        """Calcula momentum para un período específico."""
        if len(prices) < days + 1:
            return 0.0
        return round(((prices.iloc[-1] - prices.iloc[-days-1]) / prices.iloc[-days-1]) * 100, 2)
    
    def _analyze_volume(self, price_data: pd.DataFrame) -> Dict:
        """Analiza volumen de negociación."""
        if 'volume' not in price_data.columns:
            return {'average': None, 'trend': 'unknown'}
        
        volumes = price_data['volume']
        avg_volume = volumes.mean()
        recent_volume = volumes.tail(5).mean()
        
        volume_trend = 'increasing' if recent_volume > avg_volume else 'decreasing'
        
        return {
            'average': round(avg_volume, 0),
            'recent_average': round(recent_volume, 0),
            'trend': volume_trend
        }
    
    def _empty_analysis(self, ticker: str) -> Dict:
        """Retorna análisis vacío cuando no hay datos suficientes."""
        return {
            'ticker': ticker,
            'current_price': None,
            'rsi': None,
            'macd': {'value': None, 'signal': None, 'histogram': None},
            'moving_averages': {},
            'trend': {'trend': 'insufficient_data', 'strength': 0},
            'support_resistance': {'support': None, 'resistance': None},
            'momentum': {'1d': 0, '7d': 0, '30d': 0},
            'volume': {'average': None, 'trend': 'unknown'},
            'timestamp': pd.Timestamp.now().isoformat()
        }
