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
        
        # Cargar lista de CEDEARS
        logger.info("Cargando lista de CEDEARS...")
        cedears_list_path = Path(__file__).parent / "config" / "cedears_list.yaml"
        with open(cedears_list_path, 'r') as f:
            cedears_config = yaml.safe_load(f)
        
        cedears = [c['ticker'] for c in cedears_config.get('cedears', []) if c.get('priority') in ['high', 'medium']]
        logger.info(f"Analizando {len(cedears)} CEDEARS: {', '.join(cedears[:10])}...")
        
        # 1. Recolectar datos
        logger.info("\n" + "="*60)
        logger.info("PASO 1: Recolectando datos de mercado...")
        logger.info("="*60)
        
        from src.data_collector.scrapers.investing_scraper import InvestingScraper
        from src.data_collector.scrapers.portfolio_personal_client import PortfolioPersonalClient
        from src.data_collector.scrapers.news_scraper import NewsScraper
        
        # Seleccionar fuente de datos según configuración
        scraping_config = config.get('scraping', {})
        data_source = scraping_config.get('data_source', 'investing')
        
        if data_source == 'portfolio_personal':
            logger.info("Usando Portfolio Personal API como fuente de datos")
            import os
            pp_config = scraping_config.get('portfolio_personal', {})
            
            api_key = os.getenv('PORTFOLIO_PERSONAL_API_KEY')
            api_secret = os.getenv('PORTFOLIO_PERSONAL_API_SECRET')  # Opcional
            authorized_client = os.getenv('PORTFOLIO_PERSONAL_AUTHORIZED_CLIENT', 'API_CLI_REST')
            client_key = os.getenv('PORTFOLIO_PERSONAL_CLIENT_KEY', 'pp19CliApp12')
            
            if not api_key:
                logger.error("Credenciales de Portfolio Personal no configuradas en .env")
                logger.error("Configura PORTFOLIO_PERSONAL_API_KEY (requerido)")
                logger.error("PORTFOLIO_PERSONAL_API_SECRET es opcional pero recomendado para login completo")
                sys.exit(1)
            
            use_sandbox = pp_config.get('use_sandbox', False)
            if use_sandbox:
                logger.info("Usando entorno SANDBOX de Portfolio Personal")
                # Valores por defecto para sandbox si no están configurados
                if not authorized_client or authorized_client == 'API_CLI_REST':
                    authorized_client = os.getenv('PORTFOLIO_PERSONAL_AUTHORIZED_CLIENT', 'API_CLI_REST')
                if not client_key or client_key == 'pp19CliApp12':
                    client_key = os.getenv('PORTFOLIO_PERSONAL_CLIENT_KEY', 'ppApiCliSB')
            
            scraper = PortfolioPersonalClient(
                api_key=api_key,
                authorized_client=authorized_client,
                client_key=client_key,
                api_secret=api_secret,  # Opcional
                base_url=pp_config.get('base_url', 'https://clientapi.portfoliopersonal.com'),
                api_version=pp_config.get('api_version', '1.0'),
                use_sandbox=use_sandbox
            )
            
            # Intentar login solo si hay ApiSecret
            if api_secret:
                if not scraper.login():
                    logger.warning("No se pudo autenticar en Portfolio Personal API, pero continuando...")
                    logger.warning("Algunos endpoints pueden funcionar sin login completo")
            else:
                logger.info("ApiSecret no configurado. Usando endpoints que no requieren autenticación completa.")
        else:
            logger.info("Usando Investing.com como fuente de datos (simulado)")
            scraper = InvestingScraper(
                delay=scraping_config.get('delay_between_requests', 2)
            )
        
        news_scraper = NewsScraper()
        
        # Obtener contexto de mercado
        market_context = news_scraper.get_market_context()
        logger.info(f"Contexto de mercado obtenido: Dólar MEP=${market_context.get('dolar_mep')}, Riesgo País={market_context.get('riesgo_pais')}")
        
        # 2. Procesar datos y generar análisis técnico
        logger.info("\n" + "="*60)
        logger.info("PASO 2: Procesando datos y calculando indicadores técnicos...")
        logger.info("="*60)
        
        from src.data_processor.price_analyzer import PriceAnalyzer
        
        analyzer = PriceAnalyzer(config.get('analysis', {}))
        all_analyses = []
        all_news = {}
        
        for ticker in cedears:
            try:
                logger.info(f"Analizando {ticker}...")
                # Obtener datos históricos
                settlement = scraping_config.get('portfolio_personal', {}).get('settlement', 'INMEDIATA') if data_source == 'portfolio_personal' else None
                
                if data_source == 'portfolio_personal' and hasattr(scraper, 'get_cedear_history'):
                    price_data = scraper.get_cedear_history(
                        ticker,
                        days=config.get('analysis', {}).get('lookback_days', 60),
                        settlement=settlement
                    )
                else:
                    price_data = scraper.get_cedear_history(ticker, days=config.get('analysis', {}).get('lookback_days', 60))
                
                # Analizar
                analysis = analyzer.analyze(ticker, price_data)
                all_analyses.append(analysis)
                
                # Obtener noticias
                news = news_scraper.get_cedear_news(ticker)
                all_news[ticker] = news
                
            except Exception as e:
                logger.error(f"Error analizando {ticker}: {e}")
                continue
        
        logger.info(f"Análisis completado para {len(all_analyses)} CEDEARS")
        
        # 3. Generar recomendaciones con IA
        logger.info("\n" + "="*60)
        logger.info("PASO 3: Generando recomendaciones con IA...")
        logger.info("="*60)
        
        from src.ai_analyzer.recommendation_engine import RecommendationEngine
        
        recommendation_engine = RecommendationEngine(config)
        recommendations = []
        
        for analysis in all_analyses:
            ticker = analysis['ticker']
            try:
                logger.info(f"Generando recomendación para {ticker}...")
                recommendation = recommendation_engine.analyze_cedear(
                    ticker=ticker,
                    analysis_data=analysis,
                    news=all_news.get(ticker, []),
                    market_context=market_context
                )
                recommendations.append(recommendation)
                logger.info(f"  → {ticker}: {recommendation.get('action')} (confianza: {recommendation.get('confidence', 0):.0%})")
            except Exception as e:
                logger.error(f"Error generando recomendación para {ticker}: {e}")
                continue
        
        logger.info(f"Recomendaciones generadas: {len(recommendations)}")
        
        # 4. Generar reporte
        logger.info("\n" + "="*60)
        logger.info("PASO 4: Generando reporte...")
        logger.info("="*60)
        
        from src.report_generator.report_builder import ReportBuilder
        
        report_builder = ReportBuilder()
        html_report = report_builder.build_report(
            recommendations=recommendations,
            market_context=market_context,
            date=datetime.now()
        )
        
        # Guardar reporte HTML
        reports_dir = Path(__file__).parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        report_file = reports_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        logger.info(f"Reporte guardado en: {report_file}")
        
        # 5. Enviar email (si está configurado)
        logger.info("\n" + "="*60)
        logger.info("PASO 5: Enviando reporte por email...")
        logger.info("="*60)
        
        from src.email_service.email_sender import EmailSender
        
        email_sender = EmailSender(config)
        email_config = config.get('email', {})
        subject = email_config.get('subject_template', 'Análisis Semanal de CEDEARS - {date}').format(
            date=datetime.now().strftime('%d/%m/%Y')
        )
        
        email_sent = email_sender.send_report(
            html_content=html_report,
            subject=subject
        )
        
        if email_sent:
            logger.info("✓ Email enviado exitosamente")
        else:
            logger.warning("⚠ Email no enviado (verificar configuración SMTP)")
        
        # Resumen final
        logger.info("\n" + "="*60)
        logger.info("RESUMEN DEL ANÁLISIS")
        logger.info("="*60)
        buy_count = len([r for r in recommendations if r.get('action') == 'COMPRAR'])
        sell_count = len([r for r in recommendations if r.get('action') == 'VENDER'])
        hold_count = len([r for r in recommendations if r.get('action') == 'MANTENER'])
        
        logger.info(f"Total analizado: {len(recommendations)} CEDEARS")
        logger.info(f"  🟢 COMPRAR: {buy_count}")
        logger.info(f"  🔴 VENDER: {sell_count}")
        logger.info(f"  🟡 MANTENER: {hold_count}")
        logger.info(f"Reporte guardado en: {report_file}")
        logger.info("="*60)
        logger.info("Execution completed successfully")
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
