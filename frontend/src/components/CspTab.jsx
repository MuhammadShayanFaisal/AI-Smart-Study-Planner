import React from 'react'

export default function CspTab({ result }) {
  if (!result) return <div className="placeholder">CSP constraint analysis will appear here</div>

  const { schedule, violations } = result
  const isValid = violations.length === 0

  return (
    <>
      <h3 style={{ color: isValid ? '#43d9ad' : '#ff6b6b' }}>
        {isValid ? 'All CSP Constraints Satisfied' : `${violations.length} Violation(s) Found`}
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
        {schedule.map((entry, i) => {
          const isConsecutive = i > 0 && schedule[i - 1].subject === entry.subject && entry.subject !== 'Break'
          const color = entry.subject === 'Break' ? '#2a2a45' : isConsecutive ? '#ff6b6b' : '#6c63ff'
          return (
            <div
              key={i}
              style={{
                display: 'flex',
                alignItems: 'center',
                background: color,
                borderRadius: '4px',
                padding: '6px 12px',
                color: '#fff',
                fontSize: '13px',
                fontWeight: 600,
              }}
            >
              <span style={{ width: '70px', opacity: 0.9 }}>{entry.time}</span>
              <span>{entry.subject === 'Break' ? '☕ Break' : entry.subject}</span>
            </div>
          )
        })}
      </div>
      {!isValid && (
        <div className="violations-list">
          {violations.map((v, i) => <div key={i}>{v}</div>)}
        </div>
      )}
    </>
  )
}
