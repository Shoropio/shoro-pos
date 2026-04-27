# Modulo Fiscal Costa Rica

El modulo `backend/app/fiscal_cr` esta disenado para que Shoro POS pueda operar aunque Hacienda este desactivado o temporalmente no disponible. Las ventas se registran primero; si se solicita factura o tiquete electronico, se crea un documento fiscal con estado `pending`.

## Alcance preparado

- Factura electronica (`01`).
- Nota de debito electronica (`02`).
- Nota de credito electronica (`03`).
- Tiquete electronico (`04`).
- Mensaje receptor (`05`) como tipo reservado.
- Consecutivos por sucursal, terminal, tipo de documento y ambiente.
- Clave numerica Costa Rica.
- Emisor, receptor, actividad economica, condicion de venta, medio de pago.
- Lineas con CAByS, IVA, descuentos y totales.
- Moneda CRC/USD y tipo de cambio.
- Almacenamiento de XML generado, XML firmado, respuesta Hacienda, errores y bitacora.
- Ambiente sandbox/produccion mediante variables de entorno.

## Version y firma

La estructura apunta a comprobantes electronicos Costa Rica version 4.4. El archivo `signer.py` deja el punto de extension para firma XML XAdES-EPES con llave criptografica `.p12`, RSA 2048 y SHA-256. Antes de usar produccion, integre y certifique una libreria de firma compatible con la normativa vigente de Hacienda.

## Flujo recomendado

1. Registrar venta en `/sales`.
2. Crear documento fiscal si la venta requiere comprobante.
3. Generar XML con `/fiscal/documents/{id}/xml`.
4. Firmar y enviar con `/fiscal/send/{id}`.
5. Consultar estado con `/fiscal/status/{clave}`.
6. Guardar respuesta y enviar XML al cliente por correo.

## Estados

- `pending`: documento creado o integracion desactivada.
- `generated`: XML creado localmente.
- `sent`: enviado a Hacienda.
- `accepted`: reservado para respuesta aceptada.
- `rejected`: reservado para rechazo.
- `error`: error de validacion, firma, conexion o credenciales.

## Seguridad

Las credenciales OAuth2, llave `.p12`, PIN y SMTP se leen desde variables de entorno. No deben incluirse en repositorio.
