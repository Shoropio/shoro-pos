# Shoro POS - Sistema Profesional de Punto de Venta

Shoro POS es una solución robusta y moderna diseñada para la gestión comercial y facturación electrónica, optimizada para el mercado de Costa Rica.

## Características Principales

- **Interfaz Moderna (UI 2026)**: Estilo VS Code con modo oscuro profundo, animaciones suaves y diseño SaaS profesional.
- **Punto de Venta (POS)**:
    - Búsqueda ultrarrápida por Nombre, SKU o Código de Barras.
    - Soporte nativo para lectores de código de barras (auto-agregar al carrito).
    - Gestión de descuentos globales y por producto.
    - Soporte para múltiples métodos de pago: Efectivo, Tarjeta, SINPE Móvil, Transferencia y Mixto.
    - Cálculo automático de cambio.
- **Gestión de Productos**:
    - CRUD completo con SKU, CAByS e Imágenes.
    - Generación automática de códigos de barras.
    - Control de inventario con alertas de stock mínimo.
- **Facturación Electrónica (Hacienda Costa Rica)**:
    - Preparado para Tiquete Electrónico, Factura Electrónica y Notas de Crédito.
    - Módulo separado para firma XML y envío.
- **Impresión Profesional**:
    - Soporte para impresoras térmicas de 58mm y 80mm.
    - Tickets en formato HTML/PDF de alta calidad.
- **Dashboard Inteligente**:
    - Gráficos de ventas recientes.
    - Indicadores de rendimiento del día y ganancias estimadas.

## Requisitos

- Python 3.10+
- Node.js 18+
- SQLite/PostgreSQL

## Instalación

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend/web
npm install
npm run dev
```

---
© 2026 Shoropio Corporation. Todos los derechos reservados.
