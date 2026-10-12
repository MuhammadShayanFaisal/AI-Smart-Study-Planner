import React from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'

export default function FitnessCard({ result }) {
  if (!result) {
    return (
      <div className="card">
        <div className="card-title">Fitness Trend</div>
        <div className="empty-state">
          <svg className="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
          <p>Run the GA to see fitness progression</p>
        </div>
      </div>
    )
  }

  const history = result.fitness_history
  const data = history.map((f, i) => ({ generation: i + 1, fitness: f }))
  const bestGen = history.indexOf(Math.max(...history)) + 1
  const bestFitness = Math.max(...history)

  return (
    <div className="card">
      <div className="card-title">
        <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
        </svg>
        Fitness Progression
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data} margin={{ top: 5, right: 10, bottom: 5, left: -15 }}>
          <defs>
            <linearGradient id="fitnessGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--accent)" stopOpacity={0.15} />
              <stop offset="95%" stopColor="var(--accent)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="generation" stroke="var(--text-3)" fontSize={10} tickLine={false} />
          <YAxis stroke="var(--text-3)" fontSize={10} tickLine={false} axisLine={false} />
          <Tooltip
            contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '8px', fontSize: '12px' }}
            labelStyle={{ color: 'var(--text-2)', fontWeight: 600 }}
          />
          <ReferenceLine x={bestGen} stroke="var(--success)" strokeDasharray="4 4" />
          <Area type="monotone" dataKey="fitness" stroke="var(--accent)" strokeWidth={2} fill="url(#fitnessGradient)" />
        </AreaChart>
      </ResponsiveContainer>
      <p style={{ fontSize: '11px', color: 'var(--text-2)', marginTop: '4px' }}>
        Best: <strong style={{ color: 'var(--success)' }}>{bestFitness}</strong> at generation {bestGen}
      </p>
    </div>
  )
}
