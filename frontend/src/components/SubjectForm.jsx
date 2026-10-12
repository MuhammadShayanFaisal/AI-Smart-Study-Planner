import React, { useState } from 'react'

const SUBJECT_COLORS = ['#6c63ff', '#ff6b6b', '#43d9ad', '#ffd166', '#f78c6c', '#c792ea', '#89ddff', '#ff5370']

function getSubjectColor(subjects, name) {
  const idx = subjects.findIndex((s) => s.name === name)
  return SUBJECT_COLORS[(idx >= 0 ? idx : name.length) % SUBJECT_COLORS.length]
}

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
  const [advancedOpen, setAdvancedOpen] = useState(false)

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
      <div className="sidebar-header">
        <h1>Study Planner</h1>
        <p>Genetic Algorithm + Constraint Satisfaction</p>
      </div>

      <div>
        <div className="section-title">Add Subject</div>
        <div className="form-group">
          <label>Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && addSubject()} placeholder="e.g. Mathematics" />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label>Hours</label>
            <input type="number" min={1} max={8} value={hours} onChange={(e) => setHours(+e.target.value)} />
          </div>
          <div className="form-group">
            <label>Difficulty</label>
            <input type="number" min={1} max={5} value={difficulty} onChange={(e) => setDifficulty(+e.target.value)} />
          </div>
        </div>
        <div className="form-group">
          <label>Preferred Time</label>
          <select value={preferred} onChange={(e) => setPreferred(e.target.value)}>
            <option>Morning</option>
            <option>Evening</option>
          </select>
        </div>
        <div className="form-group">
          <label>Priority</label>
          <div className="priority-group">
            {[1, 2, 3].map((v) => (
              <label key={v}>
                <input type="radio" name="priority" checked={priority === v} onChange={() => setPriority(v)} />
                <span>{v === 1 ? 'Low' : v === 2 ? 'Med' : 'High'}</span>
              </label>
            ))}
          </div>
        </div>
        <div className="form-row">
          <button className="btn btn-primary" onClick={addSubject} style={{ flex: 1 }}>+ Add</button>
          <button className="btn btn-ghost" onClick={clearAll}>Clear</button>
        </div>
      </div>

      <div>
        <div className="section-title">Subjects ({subjects.length})</div>
        <div className="subject-chips">
          {subjects.length === 0 && <span className="chip-empty">No subjects yet</span>}
          {subjects.map((s, i) => (
            <span className="chip" key={s.name}>
              <span className="chip-color" style={{ background: getSubjectColor(subjects, s.name) }} />
              {s.name} &middot; {s.hours}h
              <span className="chip-remove" onClick={() => removeSubject(i)}>&times;</span>
            </span>
          ))}
        </div>
      </div>

      <div>
        <button className={`advanced-toggle ${advancedOpen ? 'open' : ''}`} onClick={() => setAdvancedOpen(!advancedOpen)}>
          <span className="chevron">&#9654;</span> Advanced Settings
        </button>
        {advancedOpen && (
          <div className="advanced-content">
            <div className="form-row">
              <div className="form-group">
                <label>Population</label>
                <input type="number" min={10} max={100} value={gaSettings.population_size} onChange={(e) => setGaSettings({ ...gaSettings, population_size: +e.target.value })} />
              </div>
              <div className="form-group">
                <label>Generations</label>
                <input type="number" min={10} max={200} value={gaSettings.generations} onChange={(e) => setGaSettings({ ...gaSettings, generations: +e.target.value })} />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Break After (hrs)</label>
                <input type="number" min={1} max={5} value={gaSettings.break_interval} onChange={(e) => setGaSettings({ ...gaSettings, break_interval: +e.target.value })} />
              </div>
              <div className="form-group">
                <label>Mutation Rate</label>
                <input type="number" min={0.01} max={0.5} step={0.01} value={gaSettings.mutation_rate} onChange={(e) => setGaSettings({ ...gaSettings, mutation_rate: +e.target.value })} />
              </div>
            </div>
          </div>
        )}
      </div>

      <div style={{ marginTop: 'auto' }}>
        <button className="btn btn-primary btn-block" onClick={onGenerate} disabled={isRunning || subjects.length < 2} style={{ padding: '12px', fontSize: '14px' }}>
          {isRunning ? 'Generating...' : 'Generate Schedule'}
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
