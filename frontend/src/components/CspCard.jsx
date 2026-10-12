import React from 'react'

export default function CspCard({ result }) {
  if (!result) {
    return (
      <div className="card">
        <div className="card-title">Constraint Check</div>
        <div className="empty-state">
          <svg className="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          <p>Run the GA to validate constraints</p>
        </div>
      </div>
    )
  }

  const { violations } = result
  const isValid = violations.length === 0

  return (
    <div className="card">
      <div className="card-title">
        <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" />
        </svg>
        Constraint Check
      </div>
      <div className={`csp-status ${isValid ? 'valid' : 'invalid'}`}>
        <svg className="csp-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          {isValid ? (
            <><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></>
          ) : (
            <><circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" /></>
          )}
        </svg>
        {isValid ? 'All constraints satisfied' : `${violations.length} violation(s) found`}
      </div>
      {!isValid && (
        <ul className="violations-list">
          {violations.map((v, i) => <li key={i}>{v}</li>)}
        </ul>
      )}
    </div>
  )
}
