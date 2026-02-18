"""
Cálculo de indicadores técnicos para análisis de CEDEARS.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calcula indicadores técnicos para análisis de precios."""
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calcula el RSI (Relative Strength Index).
        
        Args:
            prices: Serie de precios de cierre
            period: Período para cálculo (default: 14)
        
        Returns:
            Serie con valores de RSI
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_macd(
        prices: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Dict[str, pd.Series]:
        """
        Calcula MACD (Moving Average Convergence Divergence).
        
        Args:
            prices: Serie de precios de cierre
            fast: Período rápido (default: 12)
            slow: Período lento (default: 26)
            signal: Período de señal (default: 9)
        
        Returns:
            Dict con 'macd', 'signal', 'histogram'
        """
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        return {
            'macd': macd,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def calculate_moving_averages(
        prices: pd.Series,
        periods: list = [20, 50, 200]
    ) -> Dict[str, pd.Series]:
        """
        Calcula medias móviles simples.
        
        Args:
            prices: Serie de precios
            periods: Lista de períodos para calcular
        
        Returns:
            Dict con medias móviles por período
        """
        ma_dict = {}
        for period in periods:
            if len(prices) >= period:
                ma_dict[f'MA{period}'] = prices.rolling(window=period).mean()
            else:
                ma_dict[f'MA{period}'] = pd.Series(dtype=float)
        return ma_dict
    
    @staticmethod
    def calculate_bollinger_bands(
        prices: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, pd.Series]:
        """
        Calcula Bandas de Bollinger.
        
        Args:
            prices: Serie de precios
            period: Período para cálculo
            std_dev: Desviación estándar (default: 2.0)
        
        Returns:
            Dict con 'upper', 'middle', 'lower'
        """
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }
    
    @staticmethod
    def analyze_trend(prices: pd.Series) -> Dict:
        """
        Analiza la tendencia del precio.
        
        Args:
            prices: Serie de precios
        
        Returns:
            Dict con análisis de tendencia
        """
        if len(prices) < 20:
            return {'trend': 'insufficient_data', 'strength': 0}
        
        # Calcular pendiente de regresión lineal
        x = np.arange(len(prices))
        slope = np.polyfit(x, prices.values, 1)[0]
        
        # Calcular fuerza de la tendencia (R²)
        correlation = np.corrcoef(x, prices.values)[0, 1]
        strength = abs(correlation)
        
        # Determinar dirección
        if slope > 0.1:
            trend = 'bullish'
        elif slope < -0.1:
            trend = 'bearish'
        else:
            trend = 'sideways'
        
        return {
            'trend': trend,
            'strength': round(strength, 3),
            'slope': round(slope, 4)
        }
    
    @staticmethod
    def identify_support_resistance(prices: pd.Series) -> Dict:
        """
        Identifica niveles de soporte y resistencia.
        
        Args:
            prices: Serie de precios
        
        Returns:
            Dict con niveles de soporte y resistencia
        """
        if len(prices) < 20:
            return {'support': None, 'resistance': None}
        
        # Método simple: usar mínimos y máximos locales
        window = min(10, len(prices) // 4)
        
        support = prices.rolling(window=window).min().min()
        resistance = prices.rolling(window=window).max().max()
        
        return {
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'current_price': round(prices.iloc[-1], 2)
        }
