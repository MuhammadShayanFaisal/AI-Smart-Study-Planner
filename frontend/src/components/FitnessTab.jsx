import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'

export default function FitnessTab({ result }) {
  if (!result) return <div className="placeholder">Fitness history will appear after running GA</div>

  const history = result.fitness_history
  const data = history.map((f, i) => ({ generation: i + 1, fitness: f }))
  const bestGen = history.indexOf(Math.max(...history)) + 1
  const bestFitness = Math.max(...history)

  return (
    <>
      <h3>GA Fitness Progression Over Generations</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a45" />
          <XAxis dataKey="generation" stroke="#888899" fontSize={11} />
          <YAxis stroke="#888899" fontSize={11} />
          <Tooltip contentStyle={{ background: '#1e1e38', border: '1px solid #2a2a45', borderRadius: '4px' }} labelStyle={{ color: '#e8e8f0' }} />
          <ReferenceLine x={bestGen} stroke="#43d9ad" strokeDasharray="4 4" />
          <Line type="monotone" dataKey="fitness" stroke="#6c63ff" strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} />
        </LineChart>
      </ResponsiveContainer>
      <p style={{ fontSize: '12px', color: '#43d9ad', marginTop: '8px' }}>Best: {bestFitness} at generation {bestGen}</p>
    </>
  )
}
