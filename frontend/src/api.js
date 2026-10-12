const API_BASE = '/api'

export async function createSchedule(payload) {
  const res = await fetch(`${API_BASE}/schedule`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error(`Failed to create job: ${res.status}`)
  return res.json()
}

export async function getJob(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`)
  if (!res.ok) throw new Error(`Failed to get job: ${res.status}`)
  return res.json()
}

export async function pollJob(jobId, onProgress, intervalMs = 400) {
  return new Promise((resolve, reject) => {
    const tick = async () => {
      try {
        const job = await getJob(jobId)
        if (job.progress) onProgress(job.progress)
        if (job.status === 'done') return resolve(job.result)
        if (job.status === 'failed') return reject(new Error(job.error || 'Job failed'))
        setTimeout(tick, intervalMs)
      } catch (err) {
        reject(err)
      }
    }
    tick()
  })
}
