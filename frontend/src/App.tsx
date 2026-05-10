import { useState } from 'react'
import { ScanForm } from './components/ScanForm'
import { ScanResults } from './components/ScanResults'
import type { ScanResponse } from './types'
import './style.css'
import './App.css'

function App() {
  const [results, setResults] = useState<ScanResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [scanNotice, setScanNotice] = useState<string | null>(null)

  const handleScanComplete = (data: ScanResponse) => {
    setResults(data)
    setError(null)
    setScanNotice(data.message?.trim() ? data.message : null)
  }

  const handleError = (msg: string) => {
    setError(msg)
    setResults(null)
    setScanNotice(null)
  }

  const handleLoading = (loading: boolean) => {
    setLoading(loading)
    if (loading) {
      setScanNotice(null)
      setError(null)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <svg className="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          </svg>
          <h1>Lume</h1>
        </div>
        <p className="header-subtitle">Análise profissional de segurança web — comportamental e de infraestrutura</p>
      </header>

      <main className="main">
        <ScanForm
          onResult={handleScanComplete}
          onError={handleError}
          onLoading={handleLoading}
          disabled={loading}
        />

        {error && (
          <div className="alert alert-error">
            <span className="alert-icon">⚠</span>
            {error}
          </div>
        )}

        {scanNotice && !error && (
          <div className="alert alert-warn" role="status">
            <span className="alert-icon">ℹ</span>
            {scanNotice}
          </div>
        )}

        {loading && (
          <div className="loading-state">
            <div className="spinner" />
            <p>Estamos analisando o site; isso pode levar alguns segundos dependendo da complexidade.</p>
          </div>
        )}

        {results && !loading && (
          <ScanResults data={results} />
        )}
      </main>

      <footer className="footer">
        <p>⚠️ Use apenas em sistemas com autorização explícita para testes de segurança.</p>
        <a
          href="https://github.com/Bypaulohx"
          target="_blank"
          rel="noopener noreferrer"
          className="footer-logo"
          aria-label="Six Coders - GitHub Paulo Henrique"
        >
          <img src="/Logo Six Coders.svg" alt="Six Coders" />
        </a>
      </footer>
    </div>
  )
}

export default App
