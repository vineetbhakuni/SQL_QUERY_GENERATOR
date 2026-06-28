import { useState } from 'react'
import { api } from '../api/client'

const ALL_TABLES = [
  { name: 'employees',   label: 'Employees' },
  { name: 'departments', label: 'Departments' },
  { name: 'jobs',        label: 'Jobs' },
  { name: 'locations',   label: 'Locations' },
  { name: 'countries',   label: 'Countries' },
  { name: 'regions',     label: 'Regions' },
  { name: 'dependents',  label: 'Dependents' },
]

export default function Login({ onLogin }) {
  const [tab, setTab] = useState('login')
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [selectedTables, setSelectedTables] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }))

  function toggleTable(name) {
    setSelectedTables(prev =>
      prev.includes(name) ? prev.filter(t => t !== name) : [...prev, name]
    )
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (tab === 'register' && selectedTables.length === 0) {
      setError('Select at least one table to access')
      return
    }

    setLoading(true)
    try {
      if (tab === 'login') {
        const data = await api.login(form.username, form.password)
        localStorage.setItem('vineetsql_token', data.access_token)
        onLogin({ username: data.username, accessible_tables: data.accessible_tables })
      } else {
        await api.register(form.username, form.email, form.password, selectedTables)
        const data = await api.login(form.username, form.password)
        localStorage.setItem('vineetsql_token', data.access_token)
        onLogin({ username: data.username, accessible_tables: data.accessible_tables })
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-wrapper">
      <div className="login-box">
        <h1>VINEETSQL</h1>
        <p>Colorful SQL help with smart access control</p>

        <div className="tab-row">
          <button className={`tab-btn${tab === 'login' ? ' active' : ''}`} onClick={() => setTab('login')}>Sign In</button>
          <button className={`tab-btn${tab === 'register' ? ' active' : ''}`} onClick={() => setTab('register')}>Register</button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input value={form.username} onChange={e => update('username', e.target.value)} required autoFocus />
          </div>

          {tab === 'register' && (
            <div className="form-group">
              <label>Email</label>
              <input type="email" value={form.email} onChange={e => update('email', e.target.value)} required />
            </div>
          )}

          <div className="form-group">
            <label>Password</label>
            <input type="password" value={form.password} onChange={e => update('password', e.target.value)} required />
          </div>

          {tab === 'register' && (
            <div className="form-group">
              <label>Table Access <span className="label-note">(select tables you need)</span></label>
              <div className="table-picker">
                {ALL_TABLES.map(t => (
                  <label
                    key={t.name}
                    className={`table-option${selectedTables.includes(t.name) ? ' selected' : ''}`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedTables.includes(t.name)}
                      onChange={() => toggleTable(t.name)}
                    />
                    {t.label}
                  </label>
                ))}
              </div>
              {selectedTables.length === 0 && (
                <p className="helper-text">
                  You must select at least one table.
                </p>
              )}
            </div>
          )}

          <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }} disabled={loading}>
            {loading && <span className="spinner" />}
            {tab === 'login' ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <p className="demo-users">
          Demo users: <strong>viewer_user</strong> / viewer123 &nbsp;|&nbsp;
          <strong>analyst_user</strong> / analyst123 &nbsp;|&nbsp;
          <strong>admin_user</strong> / admin123
        </p>
      </div>
    </div>
  )
}
