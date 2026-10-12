import React from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'

const COLORS = ['#6c63ff', '#ff6b6b', '#43d9ad', '#ffd166', '#f78c6c', '#c792ea', '#89ddff', '#ff5370']

export default function SummaryCard({ result }) {
  if (!result) {
    return (
      <div className="card full-width">
        <div className="card-title">Summary</div>
        <div className="empty-state">
          <svg className="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
          </svg>
          <p>Run the GA to see allocation summary</p>
        </div>
      </div>
    )
  }

  const { summary, schedule } = result

  const schedCounts = {}
  schedule.forEach((e) => {
    if (e.subject !== 'Break') schedCounts[e.subject] = (schedCounts[e.subject] || 0) + 1
  })
  const pieData = Object.entries(schedCounts).map(([name, value]) => ({ name, value }))
  const totalScheduled = pieData.reduce((sum, d) => sum + d.value, 0)

  return (
    <div className="card full-width">
      <div className="card-title">
        <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" />
        </svg>
        Summary — {totalScheduled} study hours scheduled
      </div>
      <div className="summary-grid">
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={50} outerRadius={75} paddingAngle={2} strokeWidth={0}>
              {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
            </Pie>
            <Tooltip contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '8px', fontSize: '12px' }} />
          </PieChart>
        </ResponsiveContainer>
        <div className="summary-legend">
          {summary.map((s, i) => (
            <div className="summary-legend-item" key={s.subject}>
              <span className="dot" style={{ background: COLORS[i % COLORS.length] }} />
              <span>{s.subject}</span>
              <span style={{ marginLeft: 'auto', color: 'var(--text-3)', fontVariant: 'tabular-nums' }}>
                {s.scheduled}/{s.allocated}h
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
