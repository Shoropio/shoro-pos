const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
let token = localStorage.getItem('token')

export function setToken(value) {
  token = value
}

export async function api(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
  if (options.auth !== false && token) headers.Authorization = `Bearer ${token}`
  const response = await fetch(`${API_URL}${path}`, {
    method: options.method || 'GET',
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined
  })
  if (!response.ok) throw new Error(await response.text())
  return response.json()
}
