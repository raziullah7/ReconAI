import './App.css'

const shellFacts: ReadonlyArray<{ label: string; value: string }> = [
  { label: 'Workspace', value: 'Ready' },
  { label: 'Connection', value: 'Local shell' },
  { label: 'Data', value: 'Not connected' },
]

function App() {
  return (
    <main className="app-shell">
      <header className="app-header" aria-label="ReconAI workspace">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">
            R
          </span>
          <div>
            <p className="brand-name">ReconAI</p>
            <h1>Payment reconciliation</h1>
          </div>
        </div>
      </header>

      <section className="workspace-panel" aria-labelledby="workspace-title">
        <div className="workspace-copy">
          <p className="section-label">Frontend shell</p>
          <h2 id="workspace-title">Local workspace</h2>
        </div>

        <dl className="shell-facts" aria-label="Shell status">
          {shellFacts.map((fact) => (
            <div className="fact-item" key={fact.label}>
              <dt>{fact.label}</dt>
              <dd>{fact.value}</dd>
            </div>
          ))}
        </dl>
      </section>
    </main>
  )
}

export default App
