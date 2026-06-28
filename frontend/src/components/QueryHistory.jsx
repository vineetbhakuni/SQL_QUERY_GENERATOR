import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function QueryHistory() {
  const [tab, setTab] = useState('queries')
  const [queries, setQueries] = useState([])
  const [audit, setAudit] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [expanded, setExpanded] = useState(null)

  useEffect(() => {
    loadData()
  }, [tab])

  async function loadData() {
    setLoading(true)
    setError('')
    try {
      if (tab === 'queries') {
        setQueries(await api.getHistory())
      } else {
        setAudit(await api.getAuditLog())
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function fmt(iso) {
    return new Date(iso).toLocaleString()
  }

  return (
    <div>
      <h2 className="page-title">History & Audit Log</h2>

      <div className="tab-row" style={{ maxWidth: 300, marginBottom: 20 }}>
        <button className={`tab-btn${tab === 'queries' ? ' active' : ''}`} onClick={() => setTab('queries')}>Query History</button>
        <button className={`tab-btn${tab === 'audit' ? ' active' : ''}`} onClick={() => setTab('audit')}>Audit Log</button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {loading && <div className="alert alert-info">Loading…</div>}

      {tab === 'queries' && !loading && (
        queries.length === 0
          ? <p style={{ color: '#64748b' }}>No query history yet.</p>
          : queries.map(q => (
              <div
                key={q.id}
                className="history-item"
                onClick={() => setExpanded(expanded === q.id ? null : q.id)}
              >
                <div className="prompt">{q.natural_language_prompt}</div>
                <div className="meta">{fmt(q.executed_at)} · {q.rows_returned ?? '?'} row(s)</div>
                {expanded === q.id && (
                  <pre className="sql-code" style={{ marginTop: 10 }}>{q.sql_query}</pre>
                )}
              </div>
            ))
      )}

      {tab === 'audit' && !loading && (
        audit.length === 0
          ? <p style={{ color: '#64748b' }}>No audit entries yet.</p>
          : audit.map(a => (
              <div
                key={a.id}
                className={`history-item ${a.was_allowed ? '' : 'blocked'}`}
                onClick={() => setExpanded(expanded === a.id ? null : a.id)}
              >
                <div className="candidate-header" style={{ marginBottom: 4 }}>
                  <span className={`badge ${a.was_allowed ? 'badge-allowed' : 'badge-blocked'}`}>
                    {a.was_allowed ? '✓ Allowed' : '✗ Blocked'}
                  </span>
                  {a.operation_type && <span className="badge badge-op">{a.operation_type}</span>}
                  {a.tables_involved?.map(t => <span key={t} className="tag">{t}</span>)}
                </div>
                <div className="meta">{fmt(a.executed_at)}</div>
                {!a.was_allowed && a.block_reason && (
                  <div style={{ fontSize: '0.78rem', color: '#fca5a5', marginTop: 4 }}>{a.block_reason}</div>
                )}
                {expanded === a.id && (
                  <pre className="sql-code" style={{ marginTop: 10 }}>{a.query_text}</pre>
                )}
              </div>
            ))
      )}
    </div>
  )
}
