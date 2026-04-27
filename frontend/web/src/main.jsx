import React, { useEffect, useMemo, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { BarChart3, Boxes, CreditCard, LayoutDashboard, LogOut, Receipt, Search, Settings, ShoppingCart, Tags, Upload, UserRound, WifiOff, X } from 'lucide-react'
import { api, API_URL, setToken } from './services/api'
import './styles/app.css'

const pendingKey = 'shoro_pending_sales'
const money = (value, currency = 'CRC') => new Intl.NumberFormat('es-CR', { style: 'currency', currency }).format(Number(value || 0))
const permissions = () => JSON.parse(localStorage.getItem('permissions') || '{}')
const can = (permission) => Boolean(permissions().all || permissions()[permission])

function queueOfflineSale(payload) {
  const current = JSON.parse(localStorage.getItem(pendingKey) || '[]')
  current.push({ client_uuid: crypto.randomUUID(), payload, created_at: new Date().toISOString() })
  localStorage.setItem(pendingKey, JSON.stringify(current))
}

async function syncOfflineSales() {
  const pending = JSON.parse(localStorage.getItem(pendingKey) || '[]')
  if (!pending.length || !navigator.onLine) return
  const data = await api('/sync/sales', { method: 'POST', body: pending.map(({ client_uuid, payload }) => ({ client_uuid, payload })) })
  const failed = pending.filter((item) => data.results.some((result) => result.client_uuid === item.client_uuid && result.status === 'error'))
  localStorage.setItem(pendingKey, JSON.stringify(failed))
}

function Login({ onLogin }) {
  const [email, setEmail] = useState('admin@shoropos.local')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  async function submit(event) {
    event.preventDefault()
    setError('')
    try {
      const data = await api('/auth/login', { method: 'POST', body: { email, password }, auth: false })
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('role', data.role || 'administrador')
      localStorage.setItem('permissions', JSON.stringify(data.permissions || { all: true }))
      setToken(data.access_token)
      onLogin()
    } catch {
      setError('Credenciales incorrectas')
    }
  }
  return (
    <main className="login-shell">
      <section className="login-card">
        <div className="center">
          <span className="brand-mark hero-mark">S</span>
          <h1>Shoro POS</h1>
          <p>Sistema profesional de punto de venta</p>
        </div>
        <form onSubmit={submit} className="form-stack">
          <label>Correo<input value={email} onChange={(e) => setEmail(e.target.value)} /></label>
          <label>Contrasena<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
          {error && <p className="text-red center">{error}</p>}
          <button className="btn btn-primary btn-large">Iniciar sesion</button>
        </form>
      </section>
    </main>
  )
}

function Shell({ children, page, setPage, onLogout }) {
  const nav = [
    ['dashboard', LayoutDashboard, 'Dashboard'],
    ['pos', ShoppingCart, 'Punto de Venta'],
    ['arqueo', CreditCard, 'Arqueo de Caja'],
    ['products', Boxes, 'Productos'],
    ['promotions', Tags, 'Promociones'],
    ['customers', UserRound, 'Clientes'],
    ['sales', Receipt, 'Ventas'],
    ['inventory', Boxes, 'Inventario'],
    ['reports', BarChart3, 'Reportes'],
    ['settings', Settings, 'Configuracion']
  ]
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">S</span><strong>Shoro POS</strong></div>
        <nav>{nav.map(([id, Icon, label]) => <button key={id} className={page === id ? 'active' : ''} onClick={() => setPage(id)}><Icon size={18} />{label}</button>)}</nav>
        <div className="sidebar-bottom">
          <button className="btn-ghost sidebar-exit" onClick={onLogout}><LogOut size={18} />Cerrar sesion</button>
          <div className="footer">© 2026 Shoropio Corporation.<br />Todos los derechos reservados.</div>
        </div>
      </aside>
      <main className="content">{children}</main>
    </div>
  )
}

function POS() {
  const [products, setProducts] = useState([])
  const [customers, setCustomers] = useState([])
  const [search, setSearch] = useState('')
  const [cart, setCart] = useState([])
  const [customerId, setCustomerId] = useState('')
  const [method, setMethod] = useState('cash')
  const [paymentCurrency, setPaymentCurrency] = useState('CRC')
  const [exchangeRate, setExchangeRate] = useState(520)
  const [receivedAmount, setReceivedAmount] = useState('')
  const [globalDiscount, setGlobalDiscount] = useState(0)
  const [message, setMessage] = useState('')
  const [offlineCount, setOfflineCount] = useState(JSON.parse(localStorage.getItem(pendingKey) || '[]').length)
  const searchRef = useRef(null)
  const mayDiscount = can('pos.apply_discount')
  const mayRemove = can('pos.remove_cart_item')

  useEffect(() => {
    refresh()
    searchRef.current?.focus()
    const online = async () => {
      await syncOfflineSales()
      setOfflineCount(JSON.parse(localStorage.getItem(pendingKey) || '[]').length)
      refresh()
    }
    window.addEventListener('online', online)
    return () => window.removeEventListener('online', online)
  }, [])

  async function refresh() {
    const [productData, customerData] = await Promise.all([api('/products'), api('/customers')])
    setProducts(productData)
    setCustomers(customerData)
    try {
      const fx = await api('/exchange/usd-crc')
      setExchangeRate(Number(fx.sell_rate || fx.buy_rate || 520))
    } catch {
      setExchangeRate(520)
    }
  }

  const filtered = products.filter((p) => [p.name, p.internal_code, p.sku, p.barcode].join(' ').toLowerCase().includes(search.toLowerCase()))
  const totals = useMemo(() => {
    const subtotal = cart.reduce((acc, item) => acc + Number(item.sale_price) * item.qty, 0)
    const lineDiscount = cart.reduce((acc, item) => acc + Number(item.discount || 0), 0)
    const discount = Math.min(subtotal, lineDiscount + Number(globalDiscount || 0))
    const tax = cart.reduce((acc, item) => {
      const lineBase = Number(item.sale_price) * item.qty
      const share = subtotal > 0 ? lineBase / subtotal : 0
      const lineDiscountTotal = Number(item.discount || 0) + Number(globalDiscount || 0) * share
      return Math.max(0, lineBase - lineDiscountTotal) * Number(item.tax_rate) / 100
    }, 0)
    return { subtotal, discount, tax, total: Math.max(0, subtotal - discount + tax) }
  }, [cart, globalDiscount])

  function add(product) {
    setCart((current) => {
      const found = current.find((item) => item.id === product.id)
      if (found) return current.map((item) => item.id === product.id ? { ...item, qty: item.qty + 1 } : item)
      return [...current, { ...product, qty: 1, discount: 0 }]
    })
    setSearch('')
    searchRef.current?.focus()
  }

  function handleSearchKeyDown(event) {
    if (event.key !== 'Enter') return
    const exact = products.find((p) => [p.barcode, p.internal_code, p.sku].some((code) => code && code.toLowerCase() === search.toLowerCase()))
    if (exact) add(exact)
    else if (filtered.length) add(filtered[0])
  }

  async function charge(fiscalType = null) {
    if (!cart.length) return
    const paid = Number(receivedAmount || (paymentCurrency === 'USD' ? totals.total / exchangeRate : totals.total))
    const payload = {
      customer_id: customerId ? Number(customerId) : null,
      currency: 'CRC',
      exchange_rate: 1,
      global_discount: Number(globalDiscount || 0),
      items: cart.map((item) => ({ product_id: item.id, quantity: item.qty, discount: Number(item.discount || 0) })),
      payments: [{ method, amount: paid, currency: paymentCurrency, exchange_rate: paymentCurrency === 'USD' ? exchangeRate : 1 }],
      fiscal_document_type: fiscalType
    }
    try {
      const sale = await api('/sales', { method: 'POST', body: payload })
      setCart([])
      setGlobalDiscount(0)
      setReceivedAmount('')
      setMessage(`Venta ${sale.sale_number} registrada. Cambio: ${money(sale.change_amount_crc)}`)
      refresh()
    } catch {
      if (!navigator.onLine) {
        queueOfflineSale(payload)
        setOfflineCount(JSON.parse(localStorage.getItem(pendingKey) || '[]').length)
        setCart([])
        setMessage('Venta guardada offline. Se sincronizara al volver la conexion.')
      } else {
        setMessage('No se pudo procesar la venta. Revise permisos, stock o pago.')
      }
    }
  }

  const paidCRC = paymentCurrency === 'USD' ? Number(receivedAmount || 0) * exchangeRate : Number(receivedAmount || 0)
  const change = Math.max(0, paidCRC - totals.total)

  return (
    <>
      <Header title="Punto de Venta" subtitle="Caja rapida con lector de barras, multimoneda, promociones, puntos y modo offline." />
      {offlineCount > 0 && <div className="notice warning"><WifiOff size={16} /> {offlineCount} venta(s) offline pendientes.</div>}
      {message && <div className="notice">{message}</div>}
      <section className="pos-grid">
        <div className="catalog">
          <div className="search-section">
            <div className="search-input-wrapper">
              <Search className="search-icon" size={20} />
              <input ref={searchRef} placeholder="Escanea codigo de barras o busca por nombre, SKU o codigo interno" value={search} onChange={(e) => setSearch(e.target.value)} onKeyDown={handleSearchKeyDown} />
            </div>
            <button className="btn btn-secondary" onClick={() => { setCart([]); setGlobalDiscount(0); setReceivedAmount('') }}>Limpiar</button>
          </div>
          <div className="product-grid">
            {filtered.slice(0, 20).map((product) => (
              <button key={product.id} className="product-tile" onClick={() => add(product)}>
                <div className="product-tile-img">{product.image_url ? <img src={product.image_url} alt={product.name} /> : product.name[0]}</div>
                <div className="product-tile-info">
                  <h3>{product.name}</h3>
                  <div className="price">{money(product.sale_price)}</div>
                  <small>{product.barcode || product.internal_code} · Stock {product.stock}</small>
                </div>
              </button>
            ))}
          </div>
        </div>
        <aside className="cart">
          <h2>Carrito</h2>
          <label>Cliente<select value={customerId} onChange={(e) => setCustomerId(e.target.value)}><option value="">Venta rapida</option>{customers.map((c) => <option key={c.id} value={c.id}>{c.name} · {c.points_balance || 0} pts</option>)}</select></label>
          <div className="cart-items">
            {cart.map((item) => (
              <div className="cart-item pro" key={item.id}>
                <div><strong>{item.name}</strong><small>{money(item.sale_price)}</small></div>
                <input type="number" min="1" value={item.qty} onChange={(e) => setCart(cart.map((x) => x.id === item.id ? { ...x, qty: Number(e.target.value) } : x))} />
                <input type="number" min="0" disabled={!mayDiscount} value={item.discount || 0} title="Descuento por linea" onChange={(e) => setCart(cart.map((x) => x.id === item.id ? { ...x, discount: Number(e.target.value) } : x))} />
                <button className="btn-ghost text-red" disabled={!mayRemove} title={mayRemove ? 'Eliminar' : 'Sin permiso'} onClick={() => setCart(cart.filter((x) => x.id !== item.id))}><X size={16} /></button>
              </div>
            ))}
          </div>
          <div className="cart-totals">
            <div className="total-row"><span>Subtotal</span><span>{money(totals.subtotal)}</span></div>
            <div className="total-row"><span>Descuentos</span><span>{money(totals.discount)}</span></div>
            <div className="total-row"><span>IVA</span><span>{money(totals.tax)}</span></div>
            <div className="total-row grand-total"><span>Total</span><span>{money(totals.total)}</span></div>
          </div>
          <label>Descuento global<input type="number" disabled={!mayDiscount} value={globalDiscount} onChange={(e) => setGlobalDiscount(Number(e.target.value || 0))} /></label>
          <div className="payment-grid">
            <label>Metodo<select value={method} onChange={(e) => setMethod(e.target.value)}><option value="cash">Efectivo</option><option value="card">Tarjeta</option><option value="sinpe">SINPE Movil</option><option value="transfer">Transferencia</option><option value="mixed">Mixto</option></select></label>
            <label>Moneda<select value={paymentCurrency} onChange={(e) => setPaymentCurrency(e.target.value)}><option value="CRC">CRC</option><option value="USD">USD</option></select></label>
          </div>
          <div className="payment-grid">
            <label>Tipo cambio<input type="number" value={exchangeRate} onChange={(e) => setExchangeRate(Number(e.target.value || 1))} /></label>
            <label>Monto recibido<input type="number" value={receivedAmount} onChange={(e) => setReceivedAmount(e.target.value)} placeholder={paymentCurrency === 'USD' ? money(totals.total / exchangeRate, 'USD') : money(totals.total)} /></label>
          </div>
          <div className="total-row"><span>Cambio</span><strong>{money(change)}</strong></div>
          <button className="btn btn-primary btn-large" onClick={() => charge()}>Cobrar</button>
          <div className="payment-grid">
            <button className="btn btn-secondary" onClick={() => window.print()}>Imprimir</button>
            <button className="btn btn-secondary" onClick={() => charge('tiquete_electronico')}>Tiquete</button>
            <button className="btn btn-secondary" onClick={() => charge('factura_electronica')}>Factura</button>
          </div>
        </aside>
      </section>
    </>
  )
}

function Dashboard() {
  const [data, setData] = useState(null)
  useEffect(() => { api('/reports/dashboard').then(setData) }, [])
  if (!data) return <div className="loading">Cargando dashboard...</div>
  const chartData = data.recent_sales.map((s) => ({ name: s.sale_number.slice(-5), total: Number(s.total) })).reverse()
  return (
    <>
      <Header title="Panel de Control" subtitle="Indicadores operativos en tiempo real." />
      <section className="metric-grid">
        <Metric label="Ventas del dia" value={data.sales_count} />
        <Metric label="Total facturado" value={money(data.total_billed)} />
        <Metric label="Ganancia estimada" value={money(data.estimated_profit)} />
        <Metric label="Stock bajo" value={data.low_stock.length} />
      </section>
      <div className="split">
        <Panel title="Ventas recientes"><div className="chart"><ResponsiveContainer><BarChart data={chartData}><CartesianGrid strokeDasharray="3 3" stroke="#30363d" /><XAxis dataKey="name" stroke="#8b949e" /><YAxis stroke="#8b949e" /><Tooltip contentStyle={{ background: '#161b22', borderColor: '#30363d' }} /><Bar dataKey="total" fill="#1f6feb" radius={[5, 5, 0, 0]} /></BarChart></ResponsiveContainer></div></Panel>
        <Panel title="Inventario critico">{data.low_stock.length ? data.low_stock.map((p) => <Row key={p.id} left={p.name} middle={`Min ${p.min_stock || 0}`} right={p.stock} />) : <Empty />}</Panel>
      </div>
      <Panel title="Ultimas ventas">{data.recent_sales.map((s) => <Row key={s.id} left={s.sale_number} middle={s.fiscal_status} right={money(s.total)} />)}</Panel>
    </>
  )
}

function Products() {
  const empty = { internal_code: '', barcode: '', name: '', sale_price: 0, purchase_price: 0, tax_rate: 13, stock: 0, min_stock: 0, unit: 'Unid', cabys_code: '', image_url: '' }
  const [items, setItems] = useState([])
  const [form, setForm] = useState(empty)
  const [importResult, setImportResult] = useState(null)
  useEffect(() => { load() }, [])
  const load = () => api('/products').then(setItems)
  async function save(event) {
    event.preventDefault()
    await api('/products', { method: 'POST', body: form })
    setForm(empty)
    load()
  }
  async function importExcel(event) {
    const file = event.target.files?.[0]
    if (!file) return
    const body = new FormData()
    body.append('file', file)
    const response = await fetch(`${API_URL}/products/import`, { method: 'POST', headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }, body })
    setImportResult(await response.json())
    load()
  }
  const labels = { internal_code: 'Codigo interno', barcode: 'Codigo de barras', name: 'Producto', cabys_code: 'CAByS', sale_price: 'Precio venta', purchase_price: 'Precio compra', tax_rate: 'IVA %', stock: 'Stock', min_stock: 'Stock minimo', image_url: 'Imagen URL' }
  return (
    <>
      <CrudPage title="Productos" items={items} form={form} setForm={setForm} save={save} fields={Object.keys(labels)} labels={labels} render={(p) => (
        <div className="row"><span><strong>{p.name}</strong><small>{p.barcode || p.internal_code}</small></span><small>{p.cabys_code || 'Sin CAByS'}</small><b>{money(p.sale_price)}</b><button className="btn btn-secondary" onClick={() => window.open(`${API_URL}/products/${p.id}/barcode`, '_blank')}>Etiqueta</button></div>
      )} />
      {can('products.import') && <Panel title="Importacion masiva"><label className="file-drop"><Upload size={18} /> Subir Excel de productos<input type="file" accept=".xlsx,.xlsm" onChange={importExcel} /></label>{importResult && <pre className="import-result">{JSON.stringify(importResult, null, 2)}</pre>}</Panel>}
    </>
  )
}

function Promotions() {
  const [items, setItems] = useState([])
  const [products, setProducts] = useState([])
  const [form, setForm] = useState({ name: '', rule_type: 'buy_x_pay_y', product_ids: [], buy_quantity: 3, pay_quantity: 2, discount_percent: 0, is_active: true })
  useEffect(() => { Promise.all([api('/promotions'), api('/products')]).then(([promos, prods]) => { setItems(promos); setProducts(prods) }) }, [])
  async function save(event) {
    event.preventDefault()
    await api('/promotions', { method: 'POST', body: form })
    setItems(await api('/promotions'))
  }
  return (
    <>
      <Header title="Promociones" subtitle="Reglas automaticas 3x2 y descuentos tipo happy hour." />
      <section className="split">
        <Panel title="Nueva promocion"><form className="form-stack" onSubmit={save}>
          <label>Nombre<input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
          <label>Tipo<select value={form.rule_type} onChange={(e) => setForm({ ...form, rule_type: e.target.value })}><option value="buy_x_pay_y">Lleva X paga Y</option><option value="percent_discount">Descuento porcentual</option></select></label>
          <div className="payment-grid"><label>Lleva<input type="number" value={form.buy_quantity} onChange={(e) => setForm({ ...form, buy_quantity: Number(e.target.value) })} /></label><label>Paga<input type="number" value={form.pay_quantity} onChange={(e) => setForm({ ...form, pay_quantity: Number(e.target.value) })} /></label></div>
          <label>Descuento %<input type="number" value={form.discount_percent} onChange={(e) => setForm({ ...form, discount_percent: Number(e.target.value) })} /></label>
          <label>Producto<select onChange={(e) => setForm({ ...form, product_ids: e.target.value ? [Number(e.target.value)] : [] })}><option value="">Todos</option>{products.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}</select></label>
          <button className="btn btn-primary">Guardar</button>
        </form></Panel>
        <Panel title="Reglas activas">{items.length ? items.map((p) => <Row key={p.id} left={p.name} middle={p.rule_type} right={p.is_active ? 'Activa' : 'Inactiva'} />) : <Empty />}</Panel>
      </section>
    </>
  )
}

function Customers() {
  const empty = { name: '', identification_type: 'fisica', identification_number: '', email: '', phone: '', address: '' }
  const [items, setItems] = useState([])
  const [form, setForm] = useState(empty)
  useEffect(() => { load() }, [])
  const load = () => api('/customers').then(setItems)
  async function save(event) { event.preventDefault(); await api('/customers', { method: 'POST', body: form }); setForm(empty); load() }
  const labels = { name: 'Nombre', identification_type: 'Tipo ID', identification_number: 'Identificacion', email: 'Correo', phone: 'Telefono', address: 'Direccion' }
  return <CrudPage title="Clientes" items={items} form={form} setForm={setForm} save={save} fields={Object.keys(labels)} labels={labels} render={(c) => <Row left={c.name} middle={`${c.points_balance || 0} puntos`} right={c.email || ''} />} />
}

function Sales() {
  const [items, setItems] = useState([])
  useEffect(() => { api('/sales').then(setItems) }, [])
  return <><Header title="Ventas" subtitle="Historial, reimpresion y estados." /><Panel title="Historial">{items.map((s) => <Row key={s.id} left={s.sale_number} middle={`${s.payment_status} · ${s.fiscal_status} · ${s.points_earned || 0} pts`} right={money(s.total)} />)}</Panel></>
}

function Inventory() {
  const [products, setProducts] = useState([])
  const [movements, setMovements] = useState([])
  const [form, setForm] = useState({ product_id: '', movement_type: 'entrada', quantity: 1, reason: '' })
  useEffect(() => { Promise.all([api('/products'), api('/inventory/movements')]).then(([p, m]) => { setProducts(p); setMovements(m) }) }, [])
  async function save(event) {
    event.preventDefault()
    await api('/inventory/movements', { method: 'POST', body: { ...form, product_id: Number(form.product_id), quantity: Number(form.quantity) } })
    setMovements(await api('/inventory/movements'))
    setProducts(await api('/products'))
  }
  return <><Header title="Inventario" subtitle="Entradas, salidas y ajustes." /><section className="split"><Panel title="Movimiento"><form className="form-stack" onSubmit={save}><label>Producto<select value={form.product_id} onChange={(e) => setForm({ ...form, product_id: e.target.value })}><option value="">Seleccione...</option>{products.map((p) => <option key={p.id} value={p.id}>{p.name} · {p.stock}</option>)}</select></label><label>Tipo<select value={form.movement_type} onChange={(e) => setForm({ ...form, movement_type: e.target.value })}><option value="entrada">Entrada</option><option value="salida">Salida</option><option value="ajuste_positivo">Ajuste +</option><option value="ajuste_negativo">Ajuste -</option></select></label><label>Cantidad<input type="number" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} /></label><label>Motivo<input value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} /></label><button className="btn btn-primary">Registrar</button></form></Panel><Panel title="Historial">{movements.map((m) => <Row key={m.id} left={m.reason} middle={m.movement_type} right={m.quantity} />)}</Panel></section></>
}

function Arqueo() { return <><Header title="Arqueo de Caja" subtitle="Apertura, cierre y control de efectivo." /><Panel title="Caja">Modulo preparado para cierres e impresion de cierre.</Panel></> }
function Reports() { return <Dashboard /> }

function SettingsPage() {
  const [settings, setSettings] = useState(null)
  useEffect(() => { api('/settings').then(setSettings) }, [])
  async function save(event) { event.preventDefault(); setSettings(await api('/settings', { method: 'PUT', body: settings })) }
  if (!settings) return <div className="loading">Cargando configuracion...</div>
  const fields = ['business_name', 'legal_name', 'identification_number', 'economic_activity', 'phone', 'email', 'address', 'main_currency', 'default_tax_rate', 'printer_name', 'ticket_size', 'bccr_email', 'bccr_token', 'fallback_usd_crc_rate', 'loyalty_crc_per_point']
  return <><Header title="Configuracion" subtitle="Negocio, BCCR, impresoras, impuestos y puntos." /><form className="settings-form" onSubmit={save}>{fields.map((field) => <label key={field}>{field.replaceAll('_', ' ')}<input value={settings[field] || ''} onChange={(e) => setSettings({ ...settings, [field]: e.target.value })} /></label>)}<label className="check"><input type="checkbox" checked={settings.fiscal_enabled} onChange={(e) => setSettings({ ...settings, fiscal_enabled: e.target.checked })} /> Facturacion electronica activa</label><button className="btn btn-primary btn-large">Guardar</button></form></>
}

function CrudPage({ title, items, form, setForm, save, fields, labels, render }) {
  return <><Header title={title} subtitle="Gestion profesional de registros." /><section className="split"><Panel title={`Nuevo ${title.toLowerCase()}`}><form onSubmit={save} className="form-grid">{fields.map((field) => <label key={field}>{labels[field] || field}<input type={field.includes('price') || field.includes('stock') || field.includes('rate') ? 'number' : 'text'} value={form[field] ?? ''} onChange={(e) => setForm({ ...form, [field]: e.target.value })} /></label>)}<button className="btn btn-primary">Guardar</button></form></Panel><Panel title="Registros">{items.map((item) => <div key={item.id}>{render(item)}</div>)}</Panel></section></>
}
function Header({ title, subtitle }) { return <header className="page-header"><div><h1>{title}</h1><p>{subtitle}</p></div></header> }
function Metric({ label, value }) { return <article className="metric"><span>{label}</span><strong>{value}</strong></article> }
function Panel({ title, children }) { return <section className="panel"><h2>{title}</h2>{children}</section> }
function Row({ left, middle, right }) { return <div className="row"><span>{left}</span>{middle && <small>{middle}</small>}<b>{right}</b></div> }
function Empty() { return <p className="muted">Sin datos todavia.</p> }

function App() {
  const [tokenReady, setTokenReady] = useState(Boolean(localStorage.getItem('token')))
  const [page, setPage] = useState('dashboard')
  useEffect(() => {
    setToken(localStorage.getItem('token'))
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(() => {})
    window.addEventListener('online', syncOfflineSales)
    return () => window.removeEventListener('online', syncOfflineSales)
  }, [])
  if (!tokenReady) return <Login onLogin={() => setTokenReady(true)} />
  const pages = { dashboard: <Dashboard />, pos: <POS />, arqueo: <Arqueo />, products: <Products />, promotions: <Promotions />, customers: <Customers />, sales: <Sales />, inventory: <Inventory />, reports: <Reports />, settings: <SettingsPage /> }
  return <Shell page={page} setPage={setPage} onLogout={() => { localStorage.removeItem('token'); localStorage.removeItem('permissions'); setTokenReady(false) }}>{pages[page]}</Shell>
}

createRoot(document.getElementById('root')).render(<App />)
