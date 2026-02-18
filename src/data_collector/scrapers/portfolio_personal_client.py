"""
Cliente para obtener datos de CEDEARS desde Portfolio Personal API.
"""

import requests
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)


class PortfolioPersonalClient:
    """Cliente para Portfolio Personal API."""
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        authorized_client: str,
        client_key: str,
        base_url: str = "https://clientapi.portfoliopersonal.com",
        api_version: str = "1.0",
        use_sandbox: bool = False
    ):
        """
        Inicializa el cliente de Portfolio Personal.
        
        Args:
            api_key: ApiKey (Public Key)
            api_secret: ApiSecret (Private Key)
            authorized_client: AuthorizedClient (ej: "API_CLI_REST")
            client_key: ClientKey (ej: "pp19CliApp12")
            base_url: URL base de la API
            api_version: Versión de la API (default: "1.0")
            use_sandbox: Si True, usa sandbox URL
        """
        if use_sandbox:
            self.base_url = "https://clientapi_sandbox.portfoliopersonal.com"
        else:
            self.base_url = base_url.rstrip('/')
        
        self.api_version = api_version
        self.api_key = api_key
        self.api_secret = api_secret
        self.authorized_client = authorized_client
        self.client_key = client_key
        
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        # Headers comunes
        self.session.headers.update({
            'AuthorizedClient': self.authorized_client,
            'ClientKey': self.client_key,
            'ApiKey': self.api_key,
            'ApiSecret': self.api_secret
        })
    
    def _get_headers(self) -> Dict[str, str]:
        """Obtiene headers para requests autenticados."""
        headers = {
            'AuthorizedClient': self.authorized_client,
            'ClientKey': self.client_key
        }
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        return headers
    
    def login(self) -> bool:
        """
        Inicia sesión y obtiene token de acceso.
        
        Returns:
            True si el login fue exitoso
        """
        try:
            url = f"{self.base_url}/api/{self.api_version}/Account/LoginApi"
            
            response = self.session.post(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                token_data = data[0]
            else:
                token_data = data
            
            self.access_token = token_data.get('accessToken')
            self.refresh_token = token_data.get('refreshToken')
            
            # Calcular expiración (asumir 1 hora si no se especifica)
            expires_in = token_data.get('expires', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info("Login exitoso en Portfolio Personal API")
            return True
            
        except Exception as e:
            logger.error(f"Error en login de Portfolio Personal: {e}")
            return False
    
    def _ensure_authenticated(self) -> bool:
        """Asegura que hay una sesión activa."""
        if not self.access_token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
            return self.login()
        return True
    
    def get_cedear_price(self, ticker: str, settlement: str = "INMEDIATA") -> Optional[Dict]:
        """
        Obtiene el precio actual de un CEDEAR.
        
        Args:
            ticker: Símbolo del CEDEAR (ej: "AAPL")
            settlement: Tipo de liquidación (default: "INMEDIATA")
        
        Returns:
            Dict con datos del precio o None si falla
        """
        if not self._ensure_authenticated():
            logger.error("No se pudo autenticar en Portfolio Personal")
            return None
        
        try:
            url = f"{self.base_url}/api/{self.api_version}/MarketData/Current"
            params = {
                'Ticker': ticker,
                'Type': 'CEDEARS',
                'Settlement': settlement
            }
            
            headers = self._get_headers()
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'ticker': ticker,
                'price': data.get('price', 0),
                'opening_price': data.get('openingPrice', 0),
                'high': data.get('max', 0),
                'low': data.get('min', 0),
                'volume': data.get('volume', 0),
                'date': data.get('date'),
                'timestamp': datetime.now().isoformat(),
                'source': 'portfolio_personal'
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo precio de {ticker} desde Portfolio Personal: {e}")
            return None
    
    def get_cedear_history(
        self,
        ticker: str,
        days: int = 60,
        settlement: str = "INMEDIATA"
    ) -> pd.DataFrame:
        """
        Obtiene historial de precios de un CEDEAR.
        
        Args:
            ticker: Símbolo del CEDEAR
            days: Número de días hacia atrás
            settlement: Tipo de liquidación
        
        Returns:
            DataFrame con historial de precios
        """
        if not self._ensure_authenticated():
            logger.error("No se pudo autenticar en Portfolio Personal")
            return pd.DataFrame()
        
        try:
            date_to = datetime.now()
            date_from = date_to - timedelta(days=days)
            
            url = f"{self.base_url}/api/{self.api_version}/MarketData/Search"
            params = {
                'Ticker': ticker,
                'Type': 'CEDEARS',
                'DateFrom': date_from.isoformat(),
                'DateTo': date_to.isoformat(),
                'Settlement': settlement
            }
            
            headers = self._get_headers()
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data or len(data) == 0:
                logger.warning(f"No se encontraron datos históricos para {ticker}")
                return pd.DataFrame()
            
            # Convertir a DataFrame
            records = []
            for item in data:
                records.append({
                    'date': pd.to_datetime(item.get('date')),
                    'ticker': ticker,
                    'open': item.get('openingPrice', 0),
                    'high': item.get('max', 0),
                    'low': item.get('min', 0),
                    'close': item.get('price', 0),
                    'volume': item.get('volume', 0)
                })
            
            df = pd.DataFrame(records)
            df = df.sort_values('date')
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error obteniendo historial de {ticker} desde Portfolio Personal: {e}")
            return pd.DataFrame()
    
    def search_instruments(
        self,
        ticker: str = None,
        name: str = None,
        market: str = None,
        instrument_type: str = "CEDEARS"
    ) -> List[Dict]:
        """
        Busca instrumentos en Portfolio Personal.
        
        Args:
            ticker: Símbolo del instrumento
            name: Nombre o descripción
            market: Mercado (ej: "BYMA")
            instrument_type: Tipo de instrumento (default: "CEDEARS")
        
        Returns:
            Lista de instrumentos encontrados
        """
        if not self._ensure_authenticated():
            logger.error("No se pudo autenticar en Portfolio Personal")
            return []
        
        try:
            url = f"{self.base_url}/api/{self.api_version}/MarketData/SearchInstrument"
            params = {}
            
            if ticker:
                params['Ticker'] = ticker
            if name:
                params['Name'] = name
            if market:
                params['Market'] = market
            if instrument_type:
                params['Type'] = instrument_type
            
            headers = self._get_headers()
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error buscando instrumentos en Portfolio Personal: {e}")
            return []
    
    def get_multiple_cedears(self, tickers: List[str], settlement: str = "INMEDIATA") -> Dict[str, Dict]:
        """Obtiene precios de múltiples CEDEARS."""
        results = {}
        for ticker in tickers:
            try:
                results[ticker] = self.get_cedear_price(ticker, settlement)
                time.sleep(0.5)  # Pequeño delay entre requests
            except Exception as e:
                logger.error(f"Error obteniendo precio de {ticker}: {e}")
                results[ticker] = None
        return results
