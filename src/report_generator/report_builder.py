"""
Generador de reportes semanales de análisis de CEDEARS.
"""

import logging
from datetime import datetime
from typing import List, Dict
from jinja2 import Template
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportBuilder:
    """Construye reportes HTML de análisis."""
    
    def __init__(self, template_path: Path = None):
        if template_path is None:
            template_path = Path(__file__).parent / "templates" / "weekly_report.html"
        self.template_path = template_path
        self.template = self._load_template()
    
    def _load_template(self) -> Template:
        """Carga el template HTML."""
        if self.template_path.exists():
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return Template(f.read())
        else:
            # Template por defecto si no existe archivo
            return Template(self._default_template())
    
    def build_report(
        self,
        recommendations: List[Dict],
        market_context: Dict,
        date: datetime = None
    ) -> str:
        """
        Construye el reporte HTML.
        
        Args:
            recommendations: Lista de recomendaciones
            market_context: Contexto de mercado
            date: Fecha del reporte
        
        Returns:
            HTML del reporte
        """
        if date is None:
            date = datetime.now()
        
        # Separar recomendaciones por acción
        buy_recommendations = [r for r in recommendations if r.get('action') == 'COMPRAR']
        sell_recommendations = [r for r in recommendations if r.get('action') == 'VENDER']
        hold_recommendations = [r for r in recommendations if r.get('action') == 'MANTENER']
        
        # Ordenar por confianza
        buy_recommendations.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        sell_recommendations.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        context = {
            'date': date.strftime('%d/%m/%Y'),
            'buy_recommendations': buy_recommendations,
            'sell_recommendations': sell_recommendations,
            'hold_recommendations': hold_recommendations,
            'market_context': market_context,
            'total_analyzed': len(recommendations)
        }
        
        return self.template.render(**context)
    
    def _default_template(self) -> str:
        """Template HTML por defecto."""
        return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis Semanal de CEDEARS - {{ date }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            font-size: 2em;
        }
        .section {
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .recommendation {
            border-left: 4px solid #ccc;
            padding: 15px;
            margin: 15px 0;
            background: #f9f9f9;
            border-radius: 4px;
        }
        .recommendation.buy {
            border-left-color: #10b981;
        }
        .recommendation.sell {
            border-left-color: #ef4444;
        }
        .recommendation.hold {
            border-left-color: #f59e0b;
        }
        .ticker {
            font-size: 1.3em;
            font-weight: bold;
            color: #1f2937;
        }
        .action {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin: 10px 0;
        }
        .action.COMPRAR {
            background: #10b981;
            color: white;
        }
        .action.VENDER {
            background: #ef4444;
            color: white;
        }
        .action.MANTENER {
            background: #f59e0b;
            color: white;
        }
        .confidence {
            font-size: 0.9em;
            color: #6b7280;
        }
        .market-context {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .market-item {
            background: #f3f4f6;
            padding: 15px;
            border-radius: 6px;
        }
        .market-item strong {
            display: block;
            color: #667eea;
            margin-bottom: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        th {
            background: #f9fafb;
            font-weight: 600;
        }
        .footer {
            text-align: center;
            color: #6b7280;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Análisis Semanal de CEDEARS</h1>
        <p>Fecha: {{ date }}</p>
        <p>Total analizado: {{ total_analyzed }} CEDEARS</p>
    </div>

    {% if buy_recommendations %}
    <div class="section">
        <h2>🟢 CEDEARS para COMPRAR</h2>
        {% for rec in buy_recommendations %}
        <div class="recommendation buy">
            <div class="ticker">{{ rec.ticker }}</div>
            <span class="action {{ rec.action }}">{{ rec.action }}</span>
            <div class="confidence">Confianza: {{ "%.0f"|format(rec.confidence * 100) }}%</div>
            <p><strong>Razonamiento:</strong> {{ rec.reasoning }}</p>
            {% if rec.key_factors %}
            <p><strong>Factores clave:</strong> {{ rec.key_factors|join(', ') }}</p>
            {% endif %}
            {% if rec.price_target %}
            <p><strong>Precio objetivo:</strong> ${{ rec.price_target }}</p>
            {% endif %}
            <p><strong>Nivel de riesgo:</strong> {{ rec.risk_level }}</p>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if sell_recommendations %}
    <div class="section">
        <h2>🔴 CEDEARS para VENDER/RESCATAR</h2>
        {% for rec in sell_recommendations %}
        <div class="recommendation sell">
            <div class="ticker">{{ rec.ticker }}</div>
            <span class="action {{ rec.action }}">{{ rec.action }}</span>
            <div class="confidence">Confianza: {{ "%.0f"|format(rec.confidence * 100) }}%</div>
            <p><strong>Razonamiento:</strong> {{ rec.reasoning }}</p>
            {% if rec.key_factors %}
            <p><strong>Factores clave:</strong> {{ rec.key_factors|join(', ') }}</p>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if hold_recommendations %}
    <div class="section">
        <h2>🟡 CEDEARS para MANTENER</h2>
        {% for rec in hold_recommendations %}
        <div class="recommendation hold">
            <div class="ticker">{{ rec.ticker }}</div>
            <span class="action {{ rec.action }}">{{ rec.action }}</span>
            <div class="confidence">Confianza: {{ "%.0f"|format(rec.confidence * 100) }}%</div>
            <p><strong>Razonamiento:</strong> {{ rec.reasoning }}</p>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="section">
        <h2>📈 Contexto de Mercado</h2>
        <div class="market-context">
            <div class="market-item">
                <strong>Dólar MEP</strong>
                ${{ market_context.get('dolar_mep', 'N/A') }}
            </div>
            <div class="market-item">
                <strong>Dólar CCL</strong>
                ${{ market_context.get('dolar_ccl', 'N/A') }}
            </div>
            <div class="market-item">
                <strong>Riesgo País</strong>
                {{ market_context.get('riesgo_pais', 'N/A') }} pts
            </div>
            <div class="market-item">
                <strong>MERVAL</strong>
                {{ market_context.get('merval', 'N/A') }}
            </div>
        </div>
    </div>

    <div class="footer">
        <p>⚠️ <strong>Disclaimer:</strong> Este análisis es meramente informativo y no constituye asesoramiento financiero.</p>
        <p>Las decisiones de inversión son responsabilidad del usuario.</p>
        <p>Generado por CEDEARS AI Analyzer</p>
    </div>
</body>
</html>"""
