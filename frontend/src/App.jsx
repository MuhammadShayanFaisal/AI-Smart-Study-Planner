import React, { useState, useCallback, useEffect } from 'react'
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
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('theme') === 'dark')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light')
    localStorage.setItem('theme', darkMode ? 'dark' : 'light')
  }, [darkMode])

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
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button
              className="theme-toggle"
              onClick={() => setDarkMode(!darkMode)}
              aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {darkMode ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="5" /><line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" /><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" /><line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" /><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                </svg>
              )}
            </button>
            <StatusPill status={status} />
          </div>
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
