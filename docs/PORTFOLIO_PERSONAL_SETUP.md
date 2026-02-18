# Configuración de Portfolio Personal API

Este proyecto soporta obtener datos reales de CEDEARS desde la API oficial de Portfolio Personal.

## Credenciales Requeridas

Para usar Portfolio Personal como fuente de datos, necesitas las siguientes credenciales:

### Producción
1. **ApiKey (Public Key)**: `dE1pb1RHeWZDdkVtUEVaM3FHS2Y=`
2. **ApiSecret (Private Key)**: Se obtiene desde tu cuenta de Portfolio Personal (opcional pero recomendado)
3. **AuthorizedClient**: `API_CLI_REST`
4. **ClientKey**: `pp19CliApp12`

### Sandbox (Para Testing)
1. **ApiKey**: `MlBQNllVQmgyMzBzWWZyZGNnblM=`
2. **ApiSecret**: `OTZjZmMzZGQtODFiNy00MTkzLThiM2ItNDM1M2YyNDVlZmM4`
3. **AuthorizedClient**: `API_CLI_REST`
4. **ClientKey**: `ppApiCliSB`

**Nota**: 
- `ApiSecret` es **opcional** - algunos endpoints funcionan sin él
- Las credenciales de Sandbox están incluidas en `.env.example` para facilitar el testing

## Configuración

### 1. Configurar variables de entorno

El archivo `.env.example` ya incluye las credenciales de **sandbox** listas para usar. Simplemente copia el archivo:

```bash
cp .env.example .env
```

Las credenciales de sandbox están pre-configuradas:
```bash
# SANDBOX (ya configurado)
PORTFOLIO_PERSONAL_API_KEY=MlBQNllVQmgyMzBzWWZyZGNnblM=
PORTFOLIO_PERSONAL_API_SECRET=OTZjZmMzZGQtODFiNy00MTkzLThiM2ItNDM1M2YyNDVlZmM4
PORTFOLIO_PERSONAL_AUTHORIZED_CLIENT=API_CLI_REST
PORTFOLIO_PERSONAL_CLIENT_KEY=ppApiCliSB
```

Para producción, descomenta y actualiza las credenciales de producción en `.env`.

### 2. Configurar en config.yaml

El archivo `config/config.yaml` ya está configurado para usar Portfolio Personal con **sandbox por defecto**:

```yaml
scraping:
  data_source: "portfolio_personal"  # Cambiar a "investing" para usar datos simulados
  portfolio_personal:
    base_url: "https://clientapi.portfoliopersonal.com"
    use_sandbox: true  # Cambiar a false para producción
    api_version: "1.0"
    settlement: "INMEDIATA"  # INMEDIATA, A-24HS, A-48HS, A-72HS
```

**Para producción**: Cambia `use_sandbox: false` y actualiza las credenciales en `.env`.

### 3. ApiSecret (Opcional)

**ApiSecret es opcional** - algunos endpoints funcionan sin él usando solo los headers básicos. Sin embargo, para login completo y acceso a todos los endpoints, se recomienda configurarlo.

Si necesitas obtener tu ApiSecret de producción:

1. Inicia sesión en [portfoliopersonal.com](https://portfoliopersonal.com)
2. Ve a la sección de API
3. Si olvidaste tu Private Key, contacta a `api@portfoliopersonal.com`

**Para sandbox**: El ApiSecret ya está incluido en `.env.example`.

## Uso

Una vez configurado, el sistema automáticamente:

1. Se autenticará en Portfolio Personal API al iniciar
2. Obtendrá datos reales de precios de CEDEARS
3. Obtendrá historial de precios para análisis técnico
4. Usará estos datos para generar recomendaciones

## Endpoints Utilizados

El cliente utiliza los siguientes endpoints de la API:

- **Login**: `/api/1.0/Account/LoginApi` - Autenticación
- **Current Market Data**: `/api/1.0/MarketData/Current` - Precios actuales
- **Historical Market Data**: `/api/1.0/MarketData/Search` - Historial de precios
- **Search Instruments**: `/api/1.0/MarketData/SearchInstrument` - Búsqueda de instrumentos

## Sandbox vs Producción

- **Producción**: Usa `https://clientapi.portfoliopersonal.com` (datos reales)
- **Sandbox**: Usa `https://clientapi_sandbox.portfoliopersonal.com` (datos de prueba)

Para usar sandbox, configura:
```yaml
portfolio_personal:
  use_sandbox: true
```

Y usa las credenciales de sandbox que recibiste por email.

## Troubleshooting

### Error de autenticación

Si recibes errores de autenticación:

1. Verifica que todas las credenciales estén correctas en `.env`
2. Asegúrate de que el ApiSecret sea el correcto (Private Key)
3. Verifica que estés usando las credenciales correctas (producción vs sandbox)

### Sin datos históricos

Si no se obtienen datos históricos:

1. Verifica que el ticker exista en Portfolio Personal
2. Ajusta el número de días hacia atrás en `config.yaml` (`analysis.lookback_days`)
3. Verifica que el tipo de liquidación (`settlement`) sea correcto

## Documentación Oficial

- [API REST Documentation](https://itatppi.github.io/ppi-official-api-docs/api/documentacionRest/)
- [Swagger Sandbox](https://clientapi_sandbox.portfoliopersonal.com/swagger/index.html)
