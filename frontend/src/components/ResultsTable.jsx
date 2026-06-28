export default function ResultsTable({ result }) {
  const { columns, rows, rows_returned, message } = result

  return (
    <div className="card" style={{ marginTop: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>Results</span>
        <span style={{ fontSize: '0.8rem', color: '#64748b' }}>{rows_returned} row(s) · {message}</span>
      </div>

      {rows.length === 0 ? (
        <p style={{ color: '#64748b', fontSize: '0.88rem' }}>No rows returned.</p>
      ) : (
        <div className="results-wrapper">
          <table>
            <thead>
              <tr>{columns.map(c => <th key={c}>{c}</th>)}</tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={i}>
                  {row.map((cell, j) => (
                    <td key={j}>{cell === null ? <span style={{ color: '#4a5568' }}>NULL</span> : String(cell)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
