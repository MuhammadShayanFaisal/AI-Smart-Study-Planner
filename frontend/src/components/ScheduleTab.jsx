import React from 'react'

const COLORS = ['#6c63ff', '#ff6b6b', '#43d9ad', '#ffd166', '#f78c6c', '#c792ea', '#89ddff', '#ff5370']

export default function ScheduleTab({ result }) {
  if (!result) return <div className="placeholder">Run GA to see your optimized schedule here</div>

  const { schedule, overflow } = result
  const unique = [...new Set(schedule.map((e) => e.subject))].filter((s) => s !== 'Break')
  const colorMap = { Break: '#2a2a45' }
  unique.forEach((s, i) => { colorMap[s] = COLORS[i % COLORS.length] })

  return (
    <>
      <h3>Optimized Study Timetable</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
        {schedule.map((entry, i) => (
          <div
            key={i}
            style={{
              display: 'flex',
              alignItems: 'center',
              background: colorMap[entry.subject],
              borderRadius: '4px',
              padding: '6px 12px',
              color: '#fff',
              fontSize: '13px',
              fontWeight: 600,
            }}
          >
            <span style={{ width: '70px', opacity: 0.9 }}>{entry.time}</span>
            <span>{entry.subject === 'Break' ? '☕ Break' : `📖 ${entry.subject}`}</span>
          </div>
        ))}
      </div>
      {overflow && overflow.length > 0 && (
        <div className="overflow-label">Day full (ends 24:00). Continue next day: {overflow.join(' | ')}</div>
      )}
    </>
  )
}
