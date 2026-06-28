const BASE = ''  // same origin via Vite proxy

function getToken() {
  return localStorage.getItem('vineetsql_token')
}

async function request(path, options = {}) {
  const token = getToken()
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }
  const res = await fetch(BASE + path, { ...options, headers })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(body.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  login(username, password) {
    const form = new URLSearchParams({ username, password })
    return fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form,
    }).then(async (res) => {
      if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error(body.detail || `HTTP ${res.status}`)
      }
      return res.json()
    })
  },

  // table_access: string[] — list of table names the new user can SELECT
  register(username, email, password, table_access) {
    return request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password, table_access }),
    })
  },

  me() {
    return request('/auth/me')
  },

  generate(prompt) {
    return request('/query/generate', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    })
  },

  execute(sql) {
    return request('/query/execute', {
      method: 'POST',
      body: JSON.stringify({ sql }),
    })
  },

  getHistory(limit = 50) {
    return request(`/history/queries?limit=${limit}`)
  },

  getAuditLog(limit = 100) {
    return request(`/history/audit?limit=${limit}`)
  },
}
