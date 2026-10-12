import React, { useState } from 'react'

export default function SubjectForm({
  subjects,
  setSubjects,
  gaSettings,
  setGaSettings,
  onGenerate,
  isRunning,
  progress,
  status,
}) {
  const [name, setName] = useState('')
  const [hours, setHours] = useState(2)
  const [difficulty, setDifficulty] = useState(3)
  const [preferred, setPreferred] = useState('Morning')
  const [priority, setPriority] = useState(2)

  const addSubject = () => {
    const trimmed = name.trim()
    if (!trimmed) return
    if (subjects.some((s) => s.name === trimmed)) {
      alert(`'${trimmed}' is already added.`)
      return
    }
    setSubjects([...subjects, { name: trimmed, hours, priority, difficulty, preferred }])
    setName('')
  }

  const removeSubject = (idx) => {
    setSubjects(subjects.filter((_, i) => i !== idx))
  }

  const clearAll = () => setSubjects([])

  const pct = progress ? Math.round((progress.gen / progress.generations) * 100) : 0

  return (
    <>
      <div>
        <div className="section-title">Add Subject</div>
        <div className="form-row">
          <label>Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && addSubject()} />
        </div>
        <div className="form-row">
          <label>Study Hours</label>
          <input type="number" min={1} max={8} value={hours} onChange={(e) => setHours(+e.target.value)} />
        </div>
        <div className="form-row">
          <label>Difficulty (1-5)</label>
          <input type="number" min={1} max={5} value={difficulty} onChange={(e) => setDifficulty(+e.target.value)} />
        </div>
        <div className="form-row">
          <label>Preferred Time</label>
          <select value={preferred} onChange={(e) => setPreferred(e.target.value)}>
            <option>Morning</option>
            <option>Evening</option>
          </select>
        </div>
        <div className="form-row">
          <label>Priority</label>
          <div className="priority-group">
            {[1, 2, 3].map((v) => (
              <label key={v}>
                <input type="radio" name="priority" checked={priority === v} onChange={() => setPriority(v)} />
                {v === 1 ? 'Low' : v === 2 ? 'Med' : 'High'}
              </label>
            ))}
          </div>
        </div>
        <div className="btn-group">
          <button className="btn btn-primary" onClick={addSubject}>+ Add</button>
          <button className="btn btn-ghost" onClick={clearAll}>Clear All</button>
        </div>
      </div>

      <div>
        <div className="section-title">Subjects ({subjects.length})</div>
        <ul className="subject-list">
          {subjects.map((s, i) => (
            <li key={s.name}>
              <span>{s.name} [{s.hours}h | D:{s.difficulty} | {s.preferred}]</span>
              <span className="remove" onClick={() => removeSubject(i)}>x</span>
            </li>
          ))}
        </ul>
        <p className="count-label">{subjects.length} subject(s) added</p>
      </div>

      <div>
        <div className="section-title">GA Settings</div>
        <div className="ga-settings">
          <div className="form-row">
            <label>Population</label>
            <input type="number" min={10} max={100} value={gaSettings.population_size} onChange={(e) => setGaSettings({ ...gaSettings, population_size: +e.target.value })} />
          </div>
          <div className="form-row">
            <label>Generations</label>
            <input type="number" min={10} max={200} value={gaSettings.generations} onChange={(e) => setGaSettings({ ...gaSettings, generations: +e.target.value })} />
          </div>
          <div className="form-row">
            <label>Break After (hrs)</label>
            <input type="number" min={1} max={5} value={gaSettings.break_interval} onChange={(e) => setGaSettings({ ...gaSettings, break_interval: +e.target.value })} />
          </div>
          <div className="form-row">
            <label>Mutation Rate</label>
            <input type="number" min={0.01} max={0.5} step={0.01} value={gaSettings.mutation_rate} onChange={(e) => setGaSettings({ ...gaSettings, mutation_rate: +e.target.value })} />
          </div>
        </div>
      </div>

      <div style={{ marginTop: 'auto' }}>
        <button className="btn btn-success" onClick={onGenerate} disabled={isRunning || subjects.length < 2} style={{ width: '100%', padding: '12px', fontSize: '15px' }}>
          {isRunning ? 'Running GA...' : 'GENERATE SCHEDULE'}
        </button>
        {isRunning && (
          <div className="progress-container">
            <div className="progress-bar"><div className="progress-fill" style={{ width: `${pct}%` }} /></div>
            <div className="progress-text">{status}</div>
          </div>
        )}
      </div>
    </>
  )
}
