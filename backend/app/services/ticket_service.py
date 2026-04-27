from jinja2 import Environment, FileSystemLoader
import os
from typing import Dict, Any
from app.models.sale import Sale
from app.models.settings import BusinessSettings

class TicketService:
    def __init__(self):
        # Asegurarse de que el directorio de templates exista
        self.template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
        
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def generate_html_ticket(self, sale: Sale, settings: BusinessSettings) -> str:
        """
        Genera el HTML de un ticket profesional.
        """
        template_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page { margin: 0; }
                body { 
                    font-family: 'Courier New', Courier, monospace; 
                    width: {{ '280px' if settings.ticket_size == '80mm' else '190px' }}; 
                    margin: 0 auto; 
                    padding: 10px;
                    font-size: 12px;
                    color: #000;
                    background: #fff;
                }
                .text-center { text-align: center; }
                .text-right { text-align: right; }
                .bold { font-weight: bold; }
                .header { margin-bottom: 15px; line-height: 1.2; }
                .divider { border-top: 1px dashed #000; margin: 10px 0; }
                .items-table { width: 100%; border-collapse: collapse; }
                .items-table th { text-align: left; border-bottom: 1px solid #000; }
                .footer { margin-top: 15px; font-size: 10px; }
                .qr-placeholder { margin: 10px 0; }
                img.logo { max-width: 80%; height: auto; margin-bottom: 10px; }
            </style>
        </head>
        <body>
            <div class="header text-center">
                {% if settings.logo_url %}
                <img src="{{ settings.logo_url }}" class="logo">
                {% endif %}
                <div class="bold" style="font-size: 16px;">{{ settings.business_name }}</div>
                <div>{{ settings.legal_name or '' }}</div>
                <div>Cédula: {{ settings.identification_number or '' }}</div>
                <div>Tel: {{ settings.phone or '' }}</div>
                <div>{{ settings.address or '' }}</div>
            </div>

            <div class="divider"></div>

            <div>
                <div>Factura: {{ sale.sale_number }}</div>
                <div>Fecha: {{ sale.created_at.strftime('%d/%m/%Y %H:%M') }}</div>
                <div>Cajero: {{ sale.user.full_name if sale.user else 'Admin' }}</div>
                {% if sale.customer %}
                <div>Cliente: {{ sale.customer.name }}</div>
                {% endif %}
            </div>

            <div class="divider"></div>

            <table class="items-table">
                <thead>
                    <tr>
                        <th>DESC</th>
                        <th class="text-right">CANT</th>
                        <th class="text-right">TOTAL</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in sale.items %}
                    <tr>
                        <td>{{ item.product_name }}</td>
                        <td class="text-right">{{ item.quantity }}</td>
                        <td class="text-right">{{ (item.line_total)|round(2) }}</td>
                    </tr>
                    {% if item.discount_amount > 0 %}
                    <tr>
                        <td colspan="2" style="font-size: 10px; padding-left: 10px;">Desc:</td>
                        <td class="text-right" style="font-size: 10px;">-{{ item.discount_amount|round(2) }}</td>
                    </tr>
                    {% endif %}
                    {% endfor %}
                </tbody>
            </table>

            <div class="divider"></div>

            <div class="text-right">
                <div>Subtotal: {{ settings.main_currency }} {{ sale.subtotal|round(2) }}</div>
                {% if sale.discount_total > 0 %}
                <div>Descuento: {{ settings.main_currency }} {{ sale.discount_total|round(2) }}</div>
                {% endif %}
                <div>IVA: {{ settings.main_currency }} {{ sale.tax_total|round(2) }}</div>
                <div class="bold" style="font-size: 14px;">TOTAL: {{ settings.main_currency }} {{ sale.total|round(2) }}</div>
            </div>

            <div class="divider"></div>

            <div>
                <div class="bold">Método de Pago:</div>
                {% for p in sale.payments %}
                <div>{{ p.method|capitalize }} {{ p.currency }}: {{ p.amount|round(2) }}</div>
                {% endfor %}
                {% if sale.change_amount_crc %}
                <div>Cambio CRC: {{ sale.change_amount_crc|round(2) }}</div>
                {% endif %}
            </div>

            <div class="divider"></div>

            <div class="footer text-center">
                <div class="bold">¡Gracias por su compra!</div>
                <div>{{ settings.ticket_footer or '' }}</div>
                <div style="margin-top: 10px;">Shoro POS &copy; 2026</div>
                {% if sale.fiscal_status == 'aceptado' %}
                <div style="font-size: 8px; margin-top: 5px;">Autorizado mediante resolución DGT-R-48-2016</div>
                {% endif %}
            </div>
        </body>
        </html>
        """
        # En una app real, guardaríamos esto en un archivo .html, pero para rapidez lo usamos directo
        template = self.env.from_string(template_content)
        return template.render(sale=sale, settings=settings)

ticket_service = TicketService()
