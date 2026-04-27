import React, { useEffect, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { BarChart3, Boxes, CreditCard, LayoutDashboard, LogOut, Receipt, Search, Settings, ShoppingCart, UserRound } from 'lucide-react'
import { api, setToken } from './services/api'
import './styles/app.css'

const money = (value) => new Intl.NumberFormat('es-CR', { style: 'currency', currency: 'CRC' }).format(Number(value || 0))

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
      setToken(data.access_token)
      onLogin()
    } catch {
      setError('No se pudo iniciar sesion')
    }
  }
  return (
    <main className="login-shell">
      <section className="login-panel">
        <div>
          <span className="brand-mark">S</span>
          <h1>Shoro POS</h1>
          <p>Punto de venta moderno para Costa Rica.</p>
        </div>
        <form onSubmit={submit} className="form-stack">
          <label>Correo<input value={email} onChange={(e) => setEmail(e.target.value)} /></label>
          <label>Contrasena<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
          {error && <p className="error">{error}</p>}
          <button className="primary">Entrar</button>
        </form>
      </section>
    </main>
  )
}

function Shell({ children, page, setPage, onLogout }) {
  const nav = [
    ['dashboard', LayoutDashboard, 'Dashboard'],
    ['pos', ShoppingCart, 'Punto de venta'],
    ['products', Boxes, 'Productos'],
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
        <nav>
          {nav.map(([id, Icon, label]) => (
            <button key={id} className={page === id ? 'active' : ''} onClick={() => setPage(id)}><Icon size={18} />{label}</button>
          ))}
        </nav>
        <button className="ghost" onClick={onLogout}><LogOut size={18} />Salir</button>
      </aside>
      <main className="content">{children}</main>
    </div>
  )
}

function Dashboard() {
  const [data, setData] = useState(null)
  useEffect(() => { api('/reports/dashboard').then(setData) }, [])
  if (!data) return <div className="loading">Cargando dashboard...</div>
  return (
    <>
      <Header title="Dashboard" subtitle="Operacion del dia y alertas principales" />
      <section className="metric-grid">
        <Metric label="Ventas del dia" value={data.sales_count} />
        <Metric label="Total facturado" value={money(data.total_billed)} />
        <Metric label="Ganancia estimada" value={money(data.estimated_profit)} />
      </section>
      <section className="split">
        <Panel title="Productos mas vendidos">
          {data.top_products.length === 0 ? <Empty /> : data.top_products.map((p) => <Row key={p.name} left={p.name} right={p.quantity} />)}
        </Panel>
        <Panel title="Inventario bajo">
          {data.low_stock.length === 0 ? <Empty /> : data.low_stock.map((p) => <Row key={p.id} left={p.name} right={p.stock} />)}
        </Panel>
      </section>
      <Panel title="Ventas recientes">
        {data.recent_sales.map((s) => <Row key={s.id} left={s.sale_number} middle={s.fiscal_status} right={money(s.total)} />)}
      </Panel>
    </>
  )
}

function POS() {
  const [products, setProducts] = useState([])
  const [customers, setCustomers] = useState([])
  const [search, setSearch] = useState('')
  const [cart, setCart] = useState([])
  const [customerId, setCustomerId] = useState('')
  const [method, setMethod] = useState('cash')
  const [message, setMessage] = useState('')
  useEffect(() => { refresh() }, [])
  async function refresh() {
    setProducts(await api('/products'))
    setCustomers(await api('/customers'))
  }
  const filtered = products.filter((p) => [p.name, p.internal_code, p.sku, p.barcode].join(' ').toLowerCase().includes(search.toLowerCase()))
  const totals = useMemo(() => cart.reduce((acc, item) => {
    const sub = Number(item.sale_price) * item.qty
    const tax = sub * Number(item.tax_rate) / 100
    return { subtotal: acc.subtotal + sub, tax: acc.tax + tax, total: acc.total + sub + tax }
  }, { subtotal: 0, tax: 0, total: 0 }), [cart])
  function add(product) {
    setCart((current) => {
      const found = current.find((item) => item.id === product.id)
      if (found) return current.map((item) => item.id === product.id ? { ...item, qty: item.qty + 1 } : item)
      return [...current, { ...product, qty: 1 }]
    })
  }
  async function charge(fiscalType = null) {
    if (cart.length === 0) return
    const sale = await api('/sales', {
      method: 'POST',
      body: {
        customer_id: customerId ? Number(customerId) : null,
        items: cart.map((item) => ({ product_id: item.id, quantity: item.qty, discount: 0 })),
        payments: [{ method, amount: totals.total }],
        fiscal_document_type: fiscalType
      }
    })
    setCart([])
    setMessage(`Venta ${sale.sale_number} registrada por ${money(sale.total)}`)
    await refresh()
  }
  return (
    <>
      <Header title="Punto de venta" subtitle="Busqueda rapida, carrito, cobro y comprobante fiscal pendiente" />
      {message && <div className="notice">{message}</div>}
      <section className="pos-grid">
        <div className="catalog">
          <div className="searchbox"><Search size={18} /><input placeholder="Buscar por nombre, SKU o codigo" value={search} onChange={(e) => setSearch(e.target.value)} /></div>
          <div className="product-grid">
            {filtered.map((product) => <button key={product.id} className="product-tile" onClick={() => add(product)}><strong>{product.name}</strong><span>{money(product.sale_price)}</span><small>Stock {product.stock}</small></button>)}
          </div>
        </div>
        <aside className="cart">
          <h2>Carrito</h2>
          <select value={customerId} onChange={(e) => setCustomerId(e.target.value)}><option value="">Venta rapida</option>{customers.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</select>
          <div className="cart-lines">
            {cart.map((item) => <div className="cart-line" key={item.id}><span>{item.name}</span><input type="number" min="1" value={item.qty} onChange={(e) => setCart(cart.map((x) => x.id === item.id ? { ...x, qty: Number(e.target.value) } : x))} /><strong>{money(Number(item.sale_price) * item.qty)}</strong></div>)}
          </div>
          <Row left="Subtotal" right={money(totals.subtotal)} />
          <Row left="IVA" right={money(totals.tax)} />
          <Row left="Total" right={money(totals.total)} strong />
          <select value={method} onChange={(e) => setMethod(e.target.value)}><option value="cash">Efectivo</option><option value="card">Tarjeta</option><option value="sinpe">SINPE Movil</option><option value="transfer">Transferencia</option></select>
          <button className="primary large" onClick={() => charge(null)}><CreditCard size={18} />Cobrar</button>
          <button className="secondary" onClick={() => charge('04')}>Cobrar con tiquete electronico</button>
          <button className="secondary" onClick={() => charge('01')}>Cobrar con factura electronica</button>
        </aside>
      </section>
    </>
  )
}

function Products() {
  const empty = { internal_code: '', name: '', sale_price: 0, purchase_price: 0, tax_rate: 13, stock: 0, min_stock: 0, unit: 'Unid', cabys_code: '' }
  const [items, setItems] = useState([])
  const [form, setForm] = useState(empty)
  useEffect(() => { load() }, [])
  const load = () => api('/products').then(setItems)
  async function save(event) {
    event.preventDefault()
    await api('/products', { method: 'POST', body: form })
    setForm(empty)
    load()
  }
  return <CrudPage title="Productos" items={items} form={form} setForm={setForm} save={save} fields={['internal_code', 'name', 'cabys_code', 'sale_price', 'purchase_price', 'tax_rate', 'stock', 'min_stock']} render={(p) => <Row left={p.name} middle={p.internal_code} right={money(p.sale_price)} />} />
}

function Customers() {
  const empty = { name: '', identification_type: 'fisica', identification_number: '', email: '', phone: '', address: '' }
  const [items, setItems] = useState([])
  const [form, setForm] = useState(empty)
  useEffect(() => { load() }, [])
  const load = () => api('/customers').then(setItems)
  async function save(event) {
    event.preventDefault()
    await api('/customers', { method: 'POST', body: form })
    setForm(empty)
    load()
  }
  return <CrudPage title="Clientes" items={items} form={form} setForm={setForm} save={save} fields={['name', 'identification_type', 'identification_number', 'email', 'phone', 'address']} render={(c) => <Row left={c.name} middle={c.identification_number || 'Sin identificacion'} right={c.email || ''} />} />
}

function Sales() {
  const [items, setItems] = useState([])
  useEffect(() => { api('/sales').then(setItems) }, [])
  return <><Header title="Ventas" subtitle="Historial, estado de pago y estado fiscal" /><Panel title="Historial">{items.map((s) => <Row key={s.id} left={s.sale_number} middle={`${s.payment_status} / ${s.fiscal_status}`} right={money(s.total)} />)}</Panel></>
}

function Inventory() {
  const [items, setItems] = useState([])
  useEffect(() => { api('/inventory/low-stock').then(setItems) }, [])
  return <><Header title="Inventario" subtitle="Entradas, salidas, ajustes y productos bajo minimo" /><Panel title="Bajo inventario">{items.length === 0 ? <Empty /> : items.map((p) => <Row key={p.id} left={p.name} middle="Stock minimo" right={`${p.stock} / ${p.min_stock}`} />)}</Panel></>
}

function Reports() {
  return <><Header title="Reportes" subtitle="Ventas, impuestos, productos y metodos de pago" /><Dashboard /></>
}

function SettingsPage() {
  const [settings, setSettings] = useState(null)
  useEffect(() => { api('/settings').then(setSettings) }, [])
  async function save(event) {
    event.preventDefault()
    setSettings(await api('/settings', { method: 'PUT', body: settings }))
  }
  if (!settings) return <div className="loading">Cargando configuracion...</div>
  return (
    <>
      <Header title="Configuracion" subtitle="Negocio, moneda, ticket y ambiente fiscal Costa Rica" />
      <form className="settings-form" onSubmit={save}>
        {['business_name', 'legal_name', 'identification_type', 'identification_number', 'economic_activity', 'phone', 'email', 'address', 'main_currency', 'default_tax_rate', 'ticket_footer', 'theme', 'fiscal_environment'].map((field) => (
          <label key={field}>{field}<input value={settings[field] || ''} onChange={(e) => setSettings({ ...settings, [field]: e.target.value })} /></label>
        ))}
        <label className="check"><input type="checkbox" checked={settings.fiscal_enabled} onChange={(e) => setSettings({ ...settings, fiscal_enabled: e.target.checked })} /> Facturacion electronica activa</label>
        <button className="primary">Guardar</button>
      </form>
    </>
  )
}

function CrudPage({ title, items, form, setForm, save, fields, render }) {
  return (
    <>
      <Header title={title} subtitle="Crear, consultar y preparar datos para venta y facturacion" />
      <section className="split">
        <Panel title={`Nuevo ${title.toLowerCase()}`}>
          <form onSubmit={save} className="form-grid">
            {fields.map((field) => <label key={field}>{field}<input value={form[field] ?? ''} onChange={(e) => setForm({ ...form, [field]: e.target.value })} /></label>)}
            <button className="primary">Guardar</button>
          </form>
        </Panel>
        <Panel title="Registros">{items.map((item) => <div key={item.id}>{render(item)}</div>)}</Panel>
      </section>
    </>
  )
}

function Header({ title, subtitle }) { return <header className="page-header"><div><h1>{title}</h1><p>{subtitle}</p></div></header> }
function Metric({ label, value }) { return <article className="metric"><span>{label}</span><strong>{value}</strong></article> }
function Panel({ title, children }) { return <section className="panel"><h2>{title}</h2>{children}</section> }
function Row({ left, middle, right, strong }) { return <div className={strong ? 'row strong' : 'row'}><span>{left}</span>{middle && <small>{middle}</small>}<b>{right}</b></div> }
function Empty() { return <p className="muted">Sin datos todavia.</p> }

function App() {
  const [tokenReady, setTokenReady] = useState(Boolean(localStorage.getItem('token')))
  const [page, setPage] = useState('dashboard')
  useEffect(() => setToken(localStorage.getItem('token')), [])
  if (!tokenReady) return <Login onLogin={() => setTokenReady(true)} />
  const pages = { dashboard: <Dashboard />, pos: <POS />, products: <Products />, customers: <Customers />, sales: <Sales />, inventory: <Inventory />, reports: <Reports />, settings: <SettingsPage /> }
  return <Shell page={page} setPage={setPage} onLogout={() => { localStorage.removeItem('token'); setTokenReady(false) }}>{pages[page]}</Shell>
}

createRoot(document.getElementById('root')).render(<App />)
