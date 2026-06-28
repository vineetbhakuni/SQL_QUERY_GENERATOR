import { useState } from 'react'
import { api } from '../api/client'
import CandidateCard from './CandidateCard'
import ResultsTable from './ResultsTable'

export default function QueryInput() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)      // { intent, candidates }
  const [executing, setExecuting] = useState(null) // sql being executed
  const [execResult, setExecResult] = useState(null)
  const [execError, setExecError] = useState('')

  async function handleGenerate(e) {
    e.preventDefault()
    if (!prompt.trim()) return
    setError('')
    setResult(null)
    setExecResult(null)
    setExecError('')
    setLoading(true)
    try {
      const data = await api.generate(prompt)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleExecute(sql) {
    setExecuting(sql)
    setExecResult(null)
    setExecError('')
    try {
      const data = await api.execute(sql)
      setExecResult(data)
    } catch (err) {
      setExecError(err.message)
    } finally {
      setExecuting(null)
    }
  }

  const EXAMPLES = [
    'Show all employees whose salary is greater than 70000',
    'List employees in the IT department',
    'Show students with GPA above 8.5',
    'How many employees are in each department?',
  ]

  return (
    <div>
      <h2 className="page-title">Ask a Question</h2>

      <div className="card">
        <form onSubmit={handleGenerate}>
          <label>Describe what you want in plain English</label>
          <textarea
            rows={3}
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            placeholder="e.g. Show all employees whose salary is greater than ₹50,000"
          />
          <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
            <button className="btn btn-primary" disabled={loading || !prompt.trim()}>
              {loading && <span className="spinner" />}
              Generate SQL
            </button>
            <span style={{ fontSize: '0.78rem', color: '#64748b' }}>Try:</span>
            {EXAMPLES.map(ex => (
              <button
                key={ex}
                type="button"
                className="btn btn-outline"
                style={{ fontSize: '0.75rem', padding: '4px 10px' }}
                onClick={() => setPrompt(ex)}
              >
                {ex.length > 40 ? ex.slice(0, 40) + '…' : ex}
              </button>
            ))}
          </div>
        </form>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {result && (
        <div>
          <div className="alert alert-info" style={{ marginBottom: 16 }}>
            Detected intent: <strong>{result.intent}</strong> &nbsp;·&nbsp; {result.candidates.length} candidate(s) generated
          </div>
          {result.candidates.map((c, i) => (
            <CandidateCard
              key={i}
              candidate={c}
              onExecute={handleExecute}
              isExecuting={executing === c.sql}
            />
          ))}
        </div>
      )}

      {execError && <div className="alert alert-error">{execError}</div>}
      {execResult && <ResultsTable result={execResult} />}
    </div>
  )
}
