import React from 'react'

const STATUS_MAP = {
  idle: { label: 'Idle', className: 'idle' },
  running: { label: 'Running', className: 'running' },
  done: { label: 'Done', className: 'done' },
  error: { label: 'Error', className: 'error' },
}

export default function StatusPill({ status }) {
  const config = STATUS_MAP[status] || STATUS_MAP.idle
  return (
    <span className={`status-pill ${config.className}`}>
      <span className="dot" />
      {config.label}
    </span>
  )
}
