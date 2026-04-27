# ShoroPOS - Sistema Profesional de Punto de Venta

ShoroPOS es una solución robusta y moderna diseñada para la gestión comercial y facturación electrónica, optimizada para el mercado de Costa Rica.

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

### Acceso al Sistema
- **URL Frontend**: [http://127.0.0.1:5173/](http://127.0.0.1:5173/)
- **Credenciales Admin**: 
    - **Usuario**: `admin@shoropos.local`
    - **Contraseña**: `admin123`
- **Credenciales Cajero (Sugerido)**: 
    - **Usuario**: `cajero@shoropos.local`
    - **Contraseña**: `cajero123`

## Documentación de la API

El sistema cuenta con una documentación interactiva completa basada en Swagger UI.

- **URL de Documentación**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Produccion

- Health check: `GET /health`
- Readiness check: `GET /ready`
- Migraciones: `alembic upgrade head`
- Tests backend: `pytest -q`
- Build frontend: `npm run build`
- Backup SQLite: `.\scripts\backup_sqlite.ps1`
- Docker local: `docker compose up --build`

## Funcionalidades Avanzadas (Enterprise)

- **Gestión de Turnos**: Apertura y cierre de caja con arqueo detallado.
- **Facturación Electrónica Pro**: Integración directa con Hacienda CR y visualización de estados XML.
- **Reportes Inteligentes**: Análisis de IVA, utilidad por producto y exportación de datos.
- **Control de Roles**: Permisos granulares para cajeros, supervisores y administradores.
- **Soporte Multimedia**: Catálogo con imágenes de productos para una venta más visual.

---
© 2026 Shoropio Corporation. Todos los derechos reservados.
