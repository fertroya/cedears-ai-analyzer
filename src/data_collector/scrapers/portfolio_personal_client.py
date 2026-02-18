"""
Cliente para obtener datos de CEDEARS desde Portfolio Personal API.
"""

import requests
import logging
import time
import urllib3
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd

# Deshabilitar warnings de SSL para sandbox
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class PortfolioPersonalClient:
    """Cliente para Portfolio Personal API."""
    
    def __init__(
        self,
        api_key: str,
        authorized_client: str,
        client_key: str,
        api_secret: Optional[str] = None,
        base_url: str = "https://clientapi.portfoliopersonal.com",
        api_version: str = "1.0",
        use_sandbox: bool = False
    ):
        """
        Inicializa el cliente de Portfolio Personal.
        
        Args:
            api_key: ApiKey (Public Key)
            authorized_client: AuthorizedClient (ej: "API_CLI_REST")
            client_key: ClientKey (ej: "pp19CliApp12" o "ppApiCliSB" para sandbox)
            api_secret: ApiSecret (Private Key) - Opcional, solo necesario para login completo
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
        
        # Para sandbox, deshabilitar verificación SSL si hay problemas de certificado
        if use_sandbox:
            self.session.verify = False
        
        # Headers comunes - solo incluir ApiSecret si está presente
        headers = {
            'AuthorizedClient': self.authorized_client,
            'ClientKey': self.client_key,
            'ApiKey': self.api_key
        }
        if self.api_secret:
            headers['ApiSecret'] = self.api_secret
        
        self.session.headers.update(headers)
    
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
            True si el login fue exitoso, False si falla o si no hay ApiSecret
        """
        # Si no hay ApiSecret, no podemos hacer login completo
        # Algunos endpoints pueden funcionar sin login
        if not self.api_secret:
            logger.warning("ApiSecret no configurado. Algunos endpoints pueden funcionar sin login completo.")
            return False
        
        try:
            url = f"{self.base_url}/api/{self.api_version}/Account/LoginApi"
            
            # Headers para login (necesita ApiSecret)
            login_headers = {
                'AuthorizedClient': self.authorized_client,
                'ClientKey': self.client_key,
                'ApiKey': self.api_key,
                'ApiSecret': self.api_secret
            }
            
            # Usar verificación SSL según configuración de la sesión
            verify_ssl = self.session.verify if hasattr(self.session, 'verify') else True
            response = requests.post(url, headers=login_headers, timeout=10, verify=verify_ssl)
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
        """
        Asegura que hay una sesión activa.
        Si no hay ApiSecret, retorna True ya que algunos endpoints funcionan sin login.
        """
        # Si no hay ApiSecret, no podemos hacer login pero algunos endpoints funcionan sin él
        if not self.api_secret:
            return True
        
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
        # Intentar autenticación si es posible
        self._ensure_authenticated()
        
        try:
            url = f"{self.base_url}/api/{self.api_version}/MarketData/Current"
            params = {
                'Ticker': ticker,
                'Type': 'CEDEARS',
                'Settlement': settlement
            }
            
            headers = self._get_headers()
            # Usar requests directamente en lugar de session para tener control sobre headers
            verify_ssl = self.session.verify if hasattr(self.session, 'verify') else True
            response = requests.get(url, params=params, headers=headers, timeout=10, verify=verify_ssl)
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
        # Intentar autenticación si es posible
        self._ensure_authenticated()
        
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
            verify_ssl = self.session.verify if hasattr(self.session, 'verify') else True
            response = requests.get(url, params=params, headers=headers, timeout=30, verify=verify_ssl)
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
        # Intentar autenticación si es posible
        self._ensure_authenticated()
        
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
            verify_ssl = self.session.verify if hasattr(self.session, 'verify') else True
            response = requests.get(url, params=params, headers=headers, timeout=10, verify=verify_ssl)
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
