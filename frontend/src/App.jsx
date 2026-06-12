import { useState } from 'react'
import PatientForm from './components/PatientForm'
import ResultsView from './components/ResultsView'
import './App.css'

export default function App() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  return (
    <div className='app-wrapper'>
      <header className='app-header'>
        <div className='header-content'>
          <div className='header-brand'>
            <svg className='header-icon' viewBox='0 0 24 24' fill='none' xmlns='http://www.w3.org/2000/svg'>
              <circle cx='12' cy='12' r='10' fill='currentColor' opacity='0.25' />
              <path d='M13 6h-2v5H6v2h5v5h2v-5h5v-2h-5V6z' fill='currentColor' />
            </svg>
            <div>
              <h1 className='header-title'>MedRAG</h1>
              <p className='header-subtitle'>AI-Powered Clinical Decision Support</p>
            </div>
          </div>
        </div>
      </header>

      <main className='app-main'>
        <PatientForm
          onResults={setResults}
          onLoading={setLoading}
          onError={setError}
        />

        {loading && (
          <div className='status-card loading-card'>
            <div className='loading-spinner' />
            <span>Analyzing patient data — this may take a moment...</span>
          </div>
        )}

        {error && (
          <div className='status-card error-card'>
            <svg className='status-icon' viewBox='0 0 20 20' fill='currentColor'>
              <path fillRule='evenodd' d='M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z' clipRule='evenodd' />
            </svg>
            {error}
          </div>
        )}

        {results && <ResultsView data={results} />}
      </main>

      <footer className='app-footer'>
        <p>MedRAG — For research and educational use only. Not a substitute for professional medical advice.</p>
      </footer>
    </div>
  )
}
