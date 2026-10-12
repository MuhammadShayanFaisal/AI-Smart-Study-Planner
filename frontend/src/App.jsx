import React, { useState, useCallback } from 'react'
import { createSchedule, pollJob } from './api.js'
import SubjectForm from './components/SubjectForm.jsx'
import ScheduleCard from './components/ScheduleCard.jsx'
import FitnessCard from './components/FitnessCard.jsx'
import CspCard from './components/CspCard.jsx'
import SummaryCard from './components/SummaryCard.jsx'
import StatusPill from './components/StatusPill.jsx'
import ErrorBanner from './components/ErrorBanner.jsx'

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
  const [result, setResult] = useState(null)
  const [progress, setProgress] = useState(null)
  const [status, setStatus] = useState('idle')
  const [statusMessage, setStatusMessage] = useState('Ready')
  const [error, setError] = useState(null)
  const [isRunning, setIsRunning] = useState(false)

  const handleGenerate = useCallback(async () => {
    if (subjects.length < 2) {
      alert('Please add at least 2 subjects.')
      return
    }
    setIsRunning(true)
    setResult(null)
    setProgress(null)
    setError(null)
    setStatus('running')
    setStatusMessage('Starting...')
    try {
      const payload = { subjects, ...gaSettings }
      const { job_id } = await createSchedule(payload)
      const res = await pollJob(job_id, (p) => {
        setProgress(p)
        setStatusMessage(`Generation ${p.gen}/${p.generations} · Best: ${p.best_fitness}`)
      })
      setResult(res)
      setStatus('done')
      setStatusMessage(`Done · Fitness ${res.fitness} · ${res.schedule.length} slots`)
    } catch (err) {
      setStatus('error')
      setError(err.message)
      setStatusMessage('Failed')
    } finally {
      setIsRunning(false)
    }
  }, [subjects, gaSettings])

  return (
    <div className="app">
      <aside className="sidebar">
        <SubjectForm
          subjects={subjects}
          setSubjects={setSubjects}
          gaSettings={gaSettings}
          setGaSettings={setGaSettings}
          onGenerate={handleGenerate}
          isRunning={isRunning}
          progress={progress}
          status={statusMessage}
        />
      </aside>
      <main className="main">
        <div className="header">
          <span className="header-title">Your Study Plan</span>
          <StatusPill status={status} />
        </div>
        <div className="content">
          <ErrorBanner message={error} onDismiss={() => setError(null)} />
          <div className="dashboard">
            <ScheduleCard result={result} subjects={subjects} />
            <FitnessCard result={result} />
            <CspCard result={result} />
            <SummaryCard result={result} />
          </div>
        </div>
      </main>
    </div>
  )
}
