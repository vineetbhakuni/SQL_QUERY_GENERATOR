import { useEffect, useState } from 'react'
import Login from './components/Login'
import QueryHistory from './components/QueryHistory'
import QueryInput from './components/QueryInput'

export default function App() {
  const [user, setUser] = useState(null)
  const [page, setPage] = useState('query')
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('vineetsql_token')
    if (!token) { setChecking(false); return }
    fetch('/auth/me', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data) setUser({ username: data.username, accessible_tables: data.accessible_tables })
        setChecking(false)
      })
      .catch(() => setChecking(false))
  }, [])

  function handleLogin(userData) {
    setUser(userData)
    setPage('query')
  }

  function handleLogout() {
    localStorage.removeItem('vineetsql_token')
    setUser(null)
  }

  if (checking) {
    return (
      <div className="loading-screen">
        <span className="spinner" style={{ width: 24, height: 24 }} />
      </div>
    )
  }

  if (!user) return <Login onLogin={handleLogin} />

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>VINEETSQL</h1>
        <span className="user-name">
          {user.username}
        </span>

        <div className="access-panel">
          <p className="section-label">
            Table Access
          </p>
          {user.accessible_tables && user.accessible_tables.length > 0 ? (
            <div className="table-chip-list">
              {user.accessible_tables.map(t => (
                <span key={t} className="table-chip">
                  {t}
                </span>
              ))}
            </div>
          ) : (
            <span className="muted">No tables assigned</span>
          )}
        </div>

        <button
          className={`nav-btn${page === 'query' ? ' active' : ''}`}
          onClick={() => setPage('query')}
        >
          🔍 Query
        </button>
        <button
          className={`nav-btn${page === 'history' ? ' active' : ''}`}
          onClick={() => setPage('history')}
        >
          📜 History
        </button>
        <button className="logout-btn" onClick={handleLogout}>Sign out</button>
      </aside>
      <main className="main">
        {page === 'query'   && <QueryInput />}
        {page === 'history' && <QueryHistory />}
      </main>
    </div>
  )
}
