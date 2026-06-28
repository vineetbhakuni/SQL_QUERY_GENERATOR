export default function CandidateCard({ candidate, onExecute, isExecuting }) {
  const { authorization, validation, impact } = candidate
  const allowed = authorization?.allowed
  const valid = validation?.valid

  // Blocked candidates: show a clean "no access" card without exposing the SQL
  if (!allowed) {
    return (
      <div className="candidate blocked" style={{ padding: '16px 20px' }}>
        <div className="candidate-header">
          <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{candidate.label}</span>
          <span className="badge badge-blocked">Access Denied</span>
          <span className="badge badge-op">{candidate.operation_type}</span>
        </div>

        <div style={{
          marginTop: 12,
          padding: '12px 16px',
          background: 'rgba(239,68,68,0.08)',
          border: '1px solid rgba(239,68,68,0.25)',
          borderRadius: 8,
        }}>
          <p style={{ margin: 0, fontWeight: 600, color: '#f87171', fontSize: '0.88rem' }}>
            You don't have access to this query
          </p>
          <p style={{ margin: '4px 0 0', color: '#94a3b8', fontSize: '0.8rem' }}>
            {authorization.reason}
          </p>
        </div>

        <div className="detail-row" style={{ marginTop: 10 }}>
          {candidate.tables_involved.map(t => (
            <span key={t} className="tag">📋 {t}</span>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="candidate allowed">
      <div className="candidate-header">
        <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{candidate.label}</span>
        <span className="badge badge-allowed">✓ Authorized</span>
        <span className="badge badge-op">{candidate.operation_type}</span>
        {candidate.is_risky && <span className="badge badge-risky">⚠ Risky</span>}
        {!valid && <span className="badge badge-blocked">Invalid SQL</span>}
      </div>

      <pre className="sql-code">{candidate.sql}</pre>

      <p style={{ fontSize: '0.85rem', color: '#94a3b8', margin: '10px 0 6px' }}>
        {candidate.explanation}
      </p>

      {impact && (
        <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: 8 }}>
          {impact.estimated_rows != null
            ? `Estimated rows: ${impact.estimated_rows}`
            : 'Row estimate unavailable'}
          {impact.risk_reason && (
            <span style={{ color: '#fb923c', marginLeft: 8 }}> ⚠ {impact.risk_reason}</span>
          )}
        </div>
      )}

      {validation?.suggestions?.length > 0 && (
        <div className="alert alert-warning" style={{ marginBottom: 8 }}>
          {validation.suggestions.join(' · ')}
        </div>
      )}

      <div className="detail-row">
        {candidate.tables_involved.map(t => (
          <span key={t} className="tag">📋 {t}</span>
        ))}
        {candidate.columns_involved.slice(0, 6).map(c => (
          <span key={c} className="tag">{c}</span>
        ))}
        {candidate.columns_involved.length > 6 && (
          <span className="tag">+{candidate.columns_involved.length - 6} more</span>
        )}
      </div>

      {valid && (
        <div style={{ marginTop: 14 }}>
          {candidate.is_risky && (
            <div className="alert alert-warning" style={{ marginBottom: 10 }}>
              This operation is flagged as risky. Please review the SQL carefully before executing.
            </div>
          )}
          <button
            className="btn btn-success"
            onClick={() => onExecute(candidate.sql)}
            disabled={isExecuting}
          >
            {isExecuting && <span className="spinner" />}
            Run Query
          </button>
        </div>
      )}
    </div>
  )
}
