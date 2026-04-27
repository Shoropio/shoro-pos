# Shoro POS

Shoro POS es un punto de venta moderno para pequenos y medianos negocios en Costa Rica. Incluye backend FastAPI, base de datos SQLite local, frontend React, wrapper de escritorio con PyWebView y un modulo fiscal independiente preparado para comprobantes electronicos Costa Rica v4.4.

## MVP incluido

- Login con JWT.
- CRUD inicial de productos y clientes.
- Punto de venta con busqueda, carrito, IVA, cobro y registro de venta.
- Multimoneda CRC/USD con endpoint de tipo de cambio BCCR y fallback configurable.
- Motor de promociones para reglas 3x2 y descuentos porcentuales programables.
- Fidelizacion con puntos por compra y redencion en ventas.
- Importacion masiva de productos desde Excel.
- Modo offline PWA con cola local de ventas y sincronizacion al reconectar.
- Permisos granulares por rol para descuentos, descuentos altos, importacion y acciones sensibles de caja.
- Inventario con salidas automaticas por venta y movimientos manuales.
- Dashboard con ventas del dia, ganancia estimada, productos mas vendidos e inventario bajo.
- Historial de ventas y ticket de texto basico.
- Configuracion del negocio.
- Modulo `fiscal_cr` desacoplado con clave, consecutivo, XML base, firma como punto de extension, cliente REST Hacienda y estados fiscales.

## Arranque local

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python database\\seed.py
cd backend
uvicorn app.main:app --reload
```

En otra terminal:

```powershell
cd frontend\\web
npm install
npm run dev
```

Frontend: `http://localhost:5173`  
API: `http://localhost:8000/docs`

Usuario demo:

- Correo: `admin@shoropos.local`
- Contrasena: `admin123`

## Escritorio

El wrapper esta en `desktop/main.py` y usa PyWebView. Instale dependencias de escritorio con:

```powershell
pip install -r requirements-desktop.txt
```

Nota: PyWebView puede depender de `pythonnet` en Windows. Si usa Python 3.14 y esa dependencia aun no tiene wheel compatible, use Python 3.12 o 3.13 para la variante de escritorio.

## Arquitectura

- `backend/app/models`: modelos SQLAlchemy.
- `backend/app/schemas`: validaciones Pydantic.
- `backend/app/routes`: API REST.
- `backend/app/services`: reglas de negocio.
- `backend/app/fiscal_cr`: integracion fiscal Costa Rica separada del POS.
- `frontend/web`: aplicacion React.
- `desktop`: wrapper PyWebView.
- `database/seed.py`: datos iniciales.

## Variables de entorno

No se guardan credenciales en codigo. Copie `.env.example` a `.env` y configure llaves, SMTP y credenciales de Hacienda cuando active la integracion fiscal.

Para tipo de cambio automatico BCCR configure `bccr_email` y `bccr_token` desde Ajustes. Si no estan configurados, Shoro POS usa la tasa fallback del negocio para no bloquear ventas.

SQLite es el valor por defecto para operacion local. Para PostgreSQL use `DATABASE_URL=postgresql+psycopg://usuario:clave@host:5432/db` e instale el driver correspondiente.
