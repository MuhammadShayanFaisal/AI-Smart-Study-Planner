import React, { useState, useCallback } from 'react'
import { createSchedule, pollJob } from './api.js'
import SubjectForm from './components/SubjectForm.jsx'
import ScheduleTab from './components/ScheduleTab.jsx'
import FitnessTab from './components/FitnessTab.jsx'
import CspTab from './components/CspTab.jsx'
import SummaryTab from './components/SummaryTab.jsx'

const DEMO_SUBJECTS = [
  { name: 'AI', hours: 2, priority: 3, difficulty: 5, preferred: 'Morning' },
  { name: 'OS', hours: 2, priority: 2, difficulty: 3, preferred: 'Morning' },
  { name: 'Database', hours: 2, priority: 2, difficulty: 4, preferred: 'Evening' },
  { name: 'Networks', hours: 1, priority: 1, difficulty: 2, preferred: 'Evening' },
  { name: 'Math', hours: 1, priority: 3, difficulty: 4, preferred: 'Morning' },
]

export default function App() {
  const [subjects, setSubjects] = useState(DEMO_SUBJECTS)
  const [gaSettings, setGaSettings] = useState({
    population_size: 30,
    generations: 50,
    break_interval: 2,
    mutation_rate: 0.1,
  })
  const [activeTab, setActiveTab] = useState('schedule')
  const [result, setResult] = useState(null)
  const [progress, setProgress] = useState(null)
  const [status, setStatus] = useState('Ready')
  const [isRunning, setIsRunning] = useState(false)

  const handleGenerate = useCallback(async () => {
    if (subjects.length < 2) {
      alert('Please add at least 2 subjects.')
      return
    }
    setIsRunning(true)
    setResult(null)
    setProgress(null)
    setStatus('Starting...')
    try {
      const payload = { subjects, ...gaSettings }
      const { job_id } = await createSchedule(payload)
      const res = await pollJob(job_id, (p) => {
        setProgress(p)
        setStatus(`Generation ${p.gen}/${p.generations} | Best: ${p.best_fitness}`)
      })
      setResult(res)
      setStatus(`Done! Fitness: ${res.fitness} | ${res.schedule.length} slots`)
    } catch (err) {
      setStatus(`Error: ${err.message}`)
    } finally {
      setIsRunning(false)
    }
  }, [subjects, gaSettings])

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>AI Smart Study Planner</h2>
        <p className="subtitle">Genetic Algorithm x Constraint Satisfaction</p>
        <SubjectForm
          subjects={subjects}
          setSubjects={setSubjects}
          gaSettings={gaSettings}
          setGaSettings={setGaSettings}
          onGenerate={handleGenerate}
          isRunning={isRunning}
          progress={progress}
          status={status}
        />
      </aside>
      <main className="main">
        <div className="header">
          <h1>Optimized Schedule</h1>
          <span className="status">{status}</span>
        </div>
        <div className="tabs">
          {['schedule', 'fitness', 'csp', 'summary'].map((t) => (
            <button
              key={t}
              className={`tab ${activeTab === t ? 'active' : ''}`}
              onClick={() => setActiveTab(t)}
            >
              {t === 'schedule' ? 'Schedule' : t === 'fitness' ? 'Fitness Graph' : t === 'csp' ? 'CSP Visualizer' : 'Summary'}
            </button>
          ))}
        </div>
        <div className="content">
          <div className="tab-content">
            {activeTab === 'schedule' && <ScheduleTab result={result} />}
            {activeTab === 'fitness' && <FitnessTab result={result} />}
            {activeTab === 'csp' && <CspTab result={result} />}
            {activeTab === 'summary' && <SummaryTab result={result} />}
          </div>
        </div>
      </main>
    </div>
  )
}
