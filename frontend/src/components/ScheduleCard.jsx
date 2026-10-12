import React from 'react'

const SUBJECT_COLORS = ['#6c63ff', '#ff6b6b', '#43d9ad', '#ffd166', '#f78c6c', '#c792ea', '#89ddff', '#ff5370']

function getSubjectColor(subjects, name) {
  const idx = subjects.findIndex((s) => s.name === name)
  return SUBJECT_COLORS[(idx >= 0 ? idx : name.length) % SUBJECT_COLORS.length]
}

export default function ScheduleCard({ result, subjects }) {
  if (!result) {
    return (
      <div className="card full-width">
        <div className="card-title">Schedule</div>
        <div className="empty-state">
          <svg className="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
          </svg>
          <p>Add subjects and hit Generate to build your timetable</p>
        </div>
      </div>
    )
  }

  const { schedule, overflow } = result

  return (
    <div className="card full-width">
      <div className="card-title">
        <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
        </svg>
        Optimized Timetable
      </div>
      <div className="timetable">
        {schedule.map((entry, i) => {
          const isBreak = entry.subject === 'Break'
          const color = isBreak ? 'var(--surface-3)' : getSubjectColor(subjects, entry.subject)
          return (
            <div key={i} className={`timetable-row ${isBreak ? 'break-row' : ''}`}>
              <span className="time">{entry.time}</span>
              {!isBreak && <span className="subject-dot" style={{ background: color }} />}
              <span className="subject">{isBreak ? '☕ Break' : entry.subject}</span>
            </div>
          )
        })}
      </div>
      {overflow && overflow.length > 0 && (
        <div className="overflow-banner">
          Day full (ends 24:00). Continue next day: {overflow.join(' | ')}
        </div>
      )}
    </div>
  )
}
