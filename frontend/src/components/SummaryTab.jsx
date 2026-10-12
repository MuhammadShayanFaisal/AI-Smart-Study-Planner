import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#6c63ff', '#ff6b6b', '#43d9ad', '#ffd166', '#f78c6c', '#c792ea', '#89ddff', '#ff5370']

export default function SummaryTab({ result }) {
  if (!result) return <div className="placeholder">Run GA first</div>

  const { summary, schedule } = result

  const barData = summary.map((s) => ({
    subject: s.subject,
    Allocated: s.allocated,
    Scheduled: s.scheduled,
  }))

  const schedCounts = {}
  schedule.forEach((e) => {
    if (e.subject !== 'Break') schedCounts[e.subject] = (schedCounts[e.subject] || 0) + 1
  })
  const pieData = Object.entries(schedCounts).map(([name, value]) => ({ name, value }))

  return (
    <>
      <h3>Summary</h3>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        <div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={barData} margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2a45" />
              <XAxis dataKey="subject" stroke="#888899" fontSize={10} />
              <YAxis stroke="#888899" fontSize={10} />
              <Tooltip contentStyle={{ background: '#1e1e38', border: '1px solid #2a2a45', borderRadius: '4px' }} />
              <Legend wrapperStyle={{ fontSize: '11px' }} />
              <Bar dataKey="Allocated" fill="#6c63ff" radius={[3, 3, 0, 0]} />
              <Bar dataKey="Scheduled" fill="#43d9ad" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`} labelLine={false} fontSize={10}>
                {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#1e1e38', border: '1px solid #2a2a45', borderRadius: '4px' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  )
}
