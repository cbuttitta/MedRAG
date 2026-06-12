import { useState, useRef } from 'react'
import axios from 'axios'

const EXAMPLE = `Patient: 54-year-old male.
Labs: HbA1c 7.9%, LDL 142 mg/dL, HDL 38 mg/dL,
      fasting glucose 168 mg/dL, BMI 31.2
Visit notes: Patient reports fatigue and increased thirst.
No current medications. Family history of T2D on paternal side.`

function parseCSVLine(line) {
  const result = []
  let current = ''
  let inQuotes = false
  for (let i = 0; i < line.length; i++) {
    if (line[i] === '"') {
      inQuotes = !inQuotes
    } else if (line[i] === ',' && !inQuotes) {
      result.push(current.trim())
      current = ''
    } else {
      current += line[i]
    }
  }
  result.push(current.trim())
  return result
}

function csvToText(csvContent) {
  const lines = csvContent.split('\n').filter(l => l.trim())
  if (lines.length < 2) return csvContent
  const headers = parseCSVLine(lines[0])
  return lines.slice(1).map((line, i) => {
    const values = parseCSVLine(line)
    const pairs = headers
      .map((h, j) => `  ${h}: ${values[j] || 'N/A'}`)
      .join('\n')
    return `Patient ${i + 1}:\n${pairs}`
  }).join('\n\n')
}

export default function PatientForm({ onResults, onLoading, onError }) {
  const [text, setText] = useState(EXAMPLE)
  const [tab, setTab] = useState('text')
  const [csvFile, setCsvFile] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const fileRef = useRef()

  function handleFile(file) {
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.csv')) {
      onError('Please upload a .csv file.')
      return
    }
    onError(null)
    setCsvFile(file)
    const reader = new FileReader()
    reader.onload = e => {
      const parsed = csvToText(e.target.result)
      setText(parsed)
      setTab('text')
    }
    reader.readAsText(file)
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  async function handleSubmit() {
    if (!text.trim()) return
    onLoading(true)
    onError(null)
    onResults(null)
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/recommend`,
        { raw_text: text },
        { headers: { 'X-API-Key': import.meta.env.VITE_API_KEY } }
      )
      onResults(response.data)
    } catch (err) {
      const msg = err.response?.data?.error || 'An unexpected error occurred.'
      onError(msg)
    } finally {
      onLoading(false)
    }
  }

  return (
    <div className='patient-form'>
      <div className='form-toolbar'>
        <p className='form-label'>
          Patient data &mdash; paste lab values and visit notes, or upload a CSV
        </p>
        <div className='tab-pills'>
          <button
            className={`tab-btn ${tab === 'text' ? 'active' : ''}`}
            onClick={() => setTab('text')}
          >
            <svg className='tab-icon' viewBox='0 0 20 20' fill='currentColor'>
              <path fillRule='evenodd' d='M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z' clipRule='evenodd' />
            </svg>
            Manual Entry
          </button>
          <button
            className={`tab-btn ${tab === 'csv' ? 'active' : ''}`}
            onClick={() => setTab('csv')}
          >
            <svg className='tab-icon' viewBox='0 0 20 20' fill='currentColor'>
              <path fillRule='evenodd' d='M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z' clipRule='evenodd' />
            </svg>
            Upload CSV
          </button>
        </div>
      </div>

      {tab === 'text' && (
        <>
          <textarea
            id='patient-input'
            className='patient-textarea'
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder='Paste patient lab values and visit notes here...'
            spellCheck={false}
          />
          <div className='char-count'>{text.length.toLocaleString()} characters</div>
        </>
      )}

      {tab === 'csv' && (
        <div
          className={`drop-zone${dragOver ? ' drag-active' : ''}${csvFile ? ' has-file' : ''}`}
          onDragOver={e => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileRef.current.click()}
          role='button'
          tabIndex={0}
          onKeyDown={e => e.key === 'Enter' && fileRef.current.click()}
        >
          <input
            ref={fileRef}
            type='file'
            accept='.csv'
            className='file-input-hidden'
            onChange={e => handleFile(e.target.files[0])}
          />
          <svg className='drop-icon' viewBox='0 0 24 24' fill='none' stroke='currentColor'>
            <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={1.5} d='M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' />
          </svg>
          {csvFile ? (
            <>
              <p className='drop-title'>{csvFile.name}</p>
              <p className='drop-hint'>Loaded — switch to Manual Entry to review or edit</p>
            </>
          ) : (
            <>
              <p className='drop-title'>Drop a CSV file here</p>
              <p className='drop-hint'>or click to browse &mdash; column headers become patient fields</p>
            </>
          )}
        </div>
      )}

      <button
        className='submit-btn'
        onClick={handleSubmit}
        disabled={!text.trim()}
      >
        Generate Recommendations
        <svg className='btn-icon' viewBox='0 0 20 20' fill='currentColor'>
          <path fillRule='evenodd' d='M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z' clipRule='evenodd' />
        </svg>
      </button>
    </div>
  )
}
