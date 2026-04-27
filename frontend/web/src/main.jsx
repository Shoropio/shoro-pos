import React, { useEffect, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { BarChart3, Boxes, CreditCard, LayoutDashboard, LogOut, Receipt, Search, Settings, ShoppingCart, UserRound } from 'lucide-react'
import { api, setToken } from './services/api'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'
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
      setError('Credenciales incorrectas')
    }
  }
  return (
    <main className="login-shell">
      <section className="login-card">
        <div style={{ textAlign: 'center' }}>
          <span className="brand-mark" style={{ margin: '0 auto 16px', width: '48px', height: '48px', fontSize: '1.5rem' }}>S</span>
          <h1 style={{ margin: 0, fontSize: '1.75rem', color: 'var(--text-bright)' }}>Shoro POS</h1>
          <p style={{ color: 'var(--text-muted)', marginTop: '8px' }}>Sistema Profesional de Punto de Venta</p>
        </div>
        <form onSubmit={submit} className="form-stack">
          <label>Correo Electrónico<input placeholder="admin@shoropos.local" value={email} onChange={(e) => setEmail(e.target.value)} /></label>
          <label>Contraseña<input type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} /></label>
          {error && <p className="text-red" style={{ fontSize: '0.875rem', textAlign: 'center' }}>{error}</p>}
          <button className="btn btn-primary btn-large">Iniciar Sesión</button>
        </form>
      </section>
    </main>
  )
}

function Shell({ children, page, setPage, onLogout }) {
  const nav = [
    ['dashboard', LayoutDashboard, 'Dashboard'],
    ['pos', ShoppingCart, 'Punto de Venta'],
    ['products', Boxes, 'Productos'],
    ['customers', UserRound, 'Clientes'],
    ['sales', Receipt, 'Ventas'],
    ['inventory', Boxes, 'Inventario'],
    ['reports', BarChart3, 'Reportes'],
    ['settings', Settings, 'Configuración']
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
        <div style={{ marginTop: 'auto', display: 'grid', gap: '8px' }}>
          <button className="btn-ghost" onClick={onLogout}><LogOut size={18} />Cerrar Sesión</button>
          <div className="footer">
            © 2026 Shoropio Corporation.<br/>Todos los derechos reservados.
          </div>
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
  const [receivedAmount, setReceivedAmount] = useState('')
  const [globalDiscount, setGlobalDiscount] = useState(0)
  const [message, setMessage] = useState('')
  const searchRef = React.useRef(null)

  useEffect(() => { 
    refresh()
    searchRef.current?.focus()
  }, [])

  async function refresh() {
    setProducts(await api('/products'))
    setCustomers(await api('/customers'))
  }

  const filtered = products.filter((p) => 
    [p.name, p.internal_code, p.sku, p.barcode].join(' ').toLowerCase().includes(search.toLowerCase())
  )

  const totals = useMemo(() => {
    const sub = cart.reduce((acc, item) => acc + (Number(item.sale_price) * item.qty), 0)
    const disc = cart.reduce((acc, item) => acc + (Number(item.discount || 0) * item.qty), 0) + Number(globalDiscount)
    const afterDisc = sub - disc
    const tax = cart.reduce((acc, item) => {
      const itemSub = Number(item.sale_price) * item.qty
      const itemDisc = (Number(item.discount || 0) * item.qty) + (afterDisc > 0 ? (itemSub / sub * globalDiscount) : 0)
      return acc + ((itemSub - itemDisc) * Number(item.tax_rate) / 100)
    }, 0)
    return { subtotal: sub, discount: disc, tax: tax, total: Math.max(0, afterDisc + tax) }
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

  function handleSearchKeyDown(e) {
    if (e.key === 'Enter') {
      if (filtered.length === 1) {
        add(filtered[0])
      }
    }
  }

  async function charge(fiscalType = null) {
    if (cart.length === 0) return
    try {
      const sale = await api('/sales', {
        method: 'POST',
        body: {
          customer_id: customerId ? Number(customerId) : null,
          items: cart.map((item) => ({ 
            product_id: item.id, 
            quantity: item.qty, 
            discount: Number(item.discount || 0) + (Number(globalDiscount) / cart.length)
          })),
          payments: [{ method, amount: totals.total }],
          fiscal_document_type: fiscalType
        }
      })
      setCart([])
      setGlobalDiscount(0)
      setReceivedAmount('')
      setMessage(`Venta ${sale.sale_number} exitosa: ${money(sale.total)}`)
      refresh()
    } catch (err) {
      setMessage('Error al procesar la venta')
    }
  }

  const change = Number(receivedAmount) > totals.total ? Number(receivedAmount) - totals.total : 0

  return (
    <>
      <Header title="Punto de Venta" subtitle="Escanea productos o busca manualmente para facturar." />
      <section className="pos-grid">
        <div className="catalog">
          <div className="search-section">
            <div className="search-input-wrapper">
              <Search className="search-icon" size={20} />
              <input 
                ref={searchRef}
                placeholder="Escanea código de barras o busca por nombre/SKU..." 
                value={search} 
                onChange={(e) => setSearch(e.target.value)} 
                onKeyDown={handleSearchKeyDown}
              />
            </div>
            <button className="btn btn-secondary" onClick={() => { setCart([]); setGlobalDiscount(0); setReceivedAmount(''); setMessage(''); }}>Limpiar</button>
          </div>
          {message && <div className="notice" style={{ marginBottom: '20px' }}>{message}</div>}
          <div className="product-grid">
            {filtered.slice(0, 15).map((product) => (
              <button key={product.id} className="product-tile" onClick={() => add(product)}>
                <div className="product-tile-img">{product.name[0]}</div>
                <div className="product-tile-info">
                  <h3>{product.name}</h3>
                  <div className="price">{money(product.sale_price)}</div>
                  <small>Stock: {product.stock}</small>
                </div>
              </button>
            ))}
          </div>
        </div>
        <aside className="cart">
          <h2 style={{ color: 'var(--text-bright)' }}>Carrito</h2>
          <label>Cliente
            <select value={customerId} onChange={(e) => setCustomerId(e.target.value)}>
              <option value="">Venta Rápida</option>
              {customers.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </label>
          <div className="cart-items">
            {cart.map((item) => (
              <div className="cart-item" key={item.id}>
                <div><strong>{item.name}</strong><br/><small>{money(item.sale_price)}</small></div>
                <input type="number" min="1" value={item.qty} onChange={(e) => setCart(cart.map((x) => x.id === item.id ? { ...x, qty: Number(e.target.value) } : x))} />
                <button className="btn-ghost text-red" onClick={() => setCart(cart.filter(x => x.id !== item.id))}>×</button>
              </div>
            ))}
          </div>
          <div className="cart-totals">
            <div className="total-row"><span>Subtotal</span><span>{money(totals.subtotal)}</span></div>
            <div className="total-row"><span>IVA</span><span>{money(totals.tax)}</span></div>
            <div className="total-row grand-total"><span>TOTAL</span><span>{money(totals.total)}</span></div>
          </div>
          <select value={method} onChange={(e) => setMethod(e.target.value)}>
            <option value="cash">Efectivo</option><option value="card">Tarjeta</option><option value="sinpe">SINPE</option>
          </select>
          <button className="btn btn-primary btn-large" onClick={() => charge()}>COBRAR</button>
        </aside>
      </section>
    </>
  )
}

function Dashboard() {
  const [data, setData] = useState(null)
  useEffect(() => { api('/reports/dashboard').then(setData) }, [])
  if (!data) return <div className="loading">Cargando Dashboard...</div>

  const chartData = data.recent_sales.map(s => ({
    name: s.sale_number.slice(-5),
    total: Number(s.total)
  })).reverse()

  return (
    <>
      <Header title="Panel de Control" subtitle="Resumen de operaciones y métricas clave en tiempo real." />
      
      <section className="metric-grid">
        <Metric label="Ventas del Día" value={data.sales_count} />
        <Metric label="Total Facturado" value={money(data.total_billed)} />
        <Metric label="Ganancia Estimada" value={money(data.estimated_profit)} />
        <Metric label="Bajo Stock" value={data.low_stock.length} />
      </section>

      <div className="split">
        <Panel title="Tendencia de Ventas (Recientes)">
          <div style={{ height: '300px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                <XAxis dataKey="name" stroke="#8b949e" />
                <YAxis stroke="#8b949e" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#161b22', borderColor: '#30363d', color: '#c9d1d9' }}
                  itemStyle={{ color: '#58a6ff' }}
                />
                <Bar dataKey="total" fill="#1f6feb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Inventario Crítico">
          {data.low_stock.length === 0 ? <Empty /> : (
            <div style={{ display: 'grid', gap: '8px' }}>
              {data.low_stock.map((p) => (
                <Row key={p.id} left={p.name} middle={`Mín: ${p.min_stock}`} right={p.stock} />
              ))}
            </div>
          )}
        </Panel>
      </div>

      <Panel title="Últimas Transacciones">
        <div style={{ display: 'grid', gap: '4px' }}>
          {data.recent_sales.map((s) => (
            <Row 
              key={s.id} 
              left={s.sale_number} 
              middle={<span style={{ 
                padding: '2px 8px', 
                borderRadius: '12px', 
                fontSize: '0.7rem', 
                backgroundColor: s.fiscal_status === 'aceptado' ? 'rgba(35, 134, 54, 0.2)' : 'rgba(139, 148, 158, 0.1)',
                color: s.fiscal_status === 'aceptado' ? '#3fb950' : '#8b949e'
              }}>{s.fiscal_status.toUpperCase()}</span>} 
              right={money(s.total)} 
            />
          ))}
        </div>
      </Panel>
    </>
  )
}

function Products() {
  const empty = { internal_code: '', barcode: '', name: '', sale_price: 0, purchase_price: 0, tax_rate: 13, stock: 0, min_stock: 0, unit: 'Unid', cabys_code: '' }
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

  return (
    <CrudPage 
      title="Productos" 
      items={items} 
      form={form} 
      setForm={setForm} 
      save={save} 
      fields={['internal_code', 'barcode', 'name', 'cabys_code', 'sale_price', 'purchase_price', 'tax_rate', 'stock', 'min_stock']} 
      render={(p) => (
        <div className="row">
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontWeight: 600 }}>{p.name}</span>
            <small style={{ color: 'var(--text-muted)' }}>{p.barcode || p.internal_code}</small>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontWeight: 700, color: 'var(--accent-green-hover)' }}>{money(p.sale_price)}</div>
            <small>Stock: {p.stock}</small>
          </div>
        </div>
      )} 
    />
  )
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
  return <CrudPage title="Clientes" items={items} form={form} setForm={setForm} save={save} fields={['name', 'identification_type', 'identification_number', 'email', 'phone', 'address']} render={(c) => <Row left={c.name} middle={c.identification_number || 'Sin identificación'} right={c.email || ''} />} />
}

function Sales() {
  const [items, setItems] = useState([])
  useEffect(() => { api('/sales').then(setItems) }, [])
  return (
    <>
      <Header title="Historial de Ventas" subtitle="Consulta facturas, tiquetes y sus estados fiscales." />
      <Panel title="Ventas Recientes">
        <div style={{ display: 'grid', gap: '8px' }}>
          {items.map((s) => (
            <div key={s.id} className="row">
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontWeight: 600 }}>{s.sale_number}</span>
                <small style={{ color: 'var(--text-muted)' }}>{new Date(s.created_at).toLocaleString()}</small>
              </div>
              <div style={{ textAlign: 'center' }}>
                <span style={{ fontSize: '0.8rem', color: s.payment_status === 'pagada' ? 'var(--accent-green-hover)' : 'var(--accent-red)' }}>{s.payment_status.toUpperCase()}</span>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontWeight: 700 }}>{money(s.total)}</div>
                <small>{s.fiscal_status}</small>
              </div>
            </div>
          ))}
        </div>
      </Panel>
    </>
  )
}

function Inventory() {
  const [items, setItems] = useState([])
  useEffect(() => { api('/inventory/low-stock').then(setItems) }, [])
  return <><Header title="Inventario" subtitle="Control de existencias y alertas de stock mínimo." /><Panel title="Productos con bajo stock">{items.length === 0 ? <Empty /> : items.map((p) => <Row key={p.id} left={p.name} middle="Stock Mínimo" right={`${p.stock} / ${p.min_stock}`} />)}</Panel></>
}

function Reports() {
  return <><Header title="Reportes" subtitle="Análisis de ventas, impuestos y rendimiento." /><Dashboard /></>
}

function SettingsPage() {
  const [settings, setSettings] = useState(null)
  useEffect(() => { api('/settings').then(setSettings) }, [])
  async function save(event) {
    event.preventDefault()
    setSettings(await api('/settings', { method: 'PUT', body: settings }))
  }
  if (!settings) return <div className="loading">Cargando configuración...</div>
  return (
    <>
      <Header title="Configuración" subtitle="Datos del negocio, preferencias de impresión y ambiente fiscal." />
      <form className="settings-form" onSubmit={save}>
        <div className="card" style={{ gridColumn: '1 / -1', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <h3 style={{ gridColumn: '1 / -1', margin: '0 0 10px' }}>Información del Negocio</h3>
          {['business_name', 'legal_name', 'identification_type', 'identification_number', 'economic_activity', 'phone', 'email', 'address'].map((field) => (
            <label key={field}>{field}<input value={settings[field] || ''} onChange={(e) => setSettings({ ...settings, [field]: e.target.value })} /></label>
          ))}
        </div>

        <div className="card" style={{ gridColumn: '1 / -1', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
          <h3 style={{ gridColumn: '1 / -1', margin: '0 0 10px' }}>Preferencias de Impresión y Tema</h3>
          <label>Impresora Predeterminada<input value={settings.printer_name || ''} onChange={(e) => setSettings({ ...settings, printer_name: e.target.value })} /></label>
          <label>Tamaño de Ticket
            <select value={settings.ticket_size || '80mm'} onChange={(e) => setSettings({ ...settings, ticket_size: e.target.value })}>
              <option value="80mm">80mm (Estándar)</option>
              <option value="58mm">58mm (Pequeña)</option>
            </select>
          </label>
          <label>Moneda Principal<input value={settings.main_currency || 'CRC'} onChange={(e) => setSettings({ ...settings, main_currency: e.target.value })} /></label>
          <label>Impuesto Predeterminado (%)<input type="number" value={settings.default_tax_rate || 13} onChange={(e) => setSettings({ ...settings, default_tax_rate: e.target.value })} /></label>
        </div>

        <div className="card" style={{ gridColumn: '1 / -1', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
          <h3 style={{ gridColumn: '1 / -1', margin: '0 0 10px' }}>Configuración Fiscal (Costa Rica)</h3>
          <label>Ambiente de Hacienda
            <select value={settings.fiscal_environment || 'sandbox'} onChange={(e) => setSettings({ ...settings, fiscal_environment: e.target.value })}>
              <option value="sandbox">Sandbox (Pruebas)</option>
              <option value="production">Producción (Real)</option>
            </select>
          </label>
          <label className="check" style={{ marginTop: '24px' }}>
            <input type="checkbox" checked={settings.fiscal_enabled} onChange={(e) => setSettings({ ...settings, fiscal_enabled: e.target.checked })} /> 
            Habilitar Facturación Electrónica
          </label>
        </div>

        <button className="btn btn-primary btn-large" style={{ gridColumn: '1 / -1', marginTop: '20px' }}>Guardar Cambios</button>
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
