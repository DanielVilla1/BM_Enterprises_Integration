import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import TodoApp from './components/TodoApp'
import { checkBackend, checkDb } from './services/todoService'

function App() {
  const [count, setCount] = useState(0)
  const [backendStatus, setBackendStatus] = useState(null)
  const [dbStatus, setDbStatus] = useState(null)

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Papecon</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>

      <hr />
      <div className="p-4 max-w-lg mx-auto">
        <h3 className="text-lg font-semibold mb-2">Connections</h3>
        <div className="flex gap-2 mb-4">
          <button
            onClick={async () => {
              try {
                const res = await checkBackend()
                setBackendStatus(JSON.stringify(res))
              } catch (e) {
                setBackendStatus('error')
              }
            }}
            className="bg-green-500 text-white px-3 py-1"
          >
            Check Backend
          </button>
          <button
            onClick={async () => {
              try {
                const res = await checkDb()
                setDbStatus(JSON.stringify(res))
              } catch (e) {
                setDbStatus('error')
              }
            }}
            className="bg-yellow-500 text-black px-3 py-1"
          >
            Check DB
          </button>
        </div>
        <div className="mb-4">
          <div><strong>Backend:</strong> {backendStatus ?? 'unknown'}</div>
          <div><strong>DB:</strong> {dbStatus ?? 'unknown'}</div>
        </div>
      </div>

      <TodoApp />
    </>
  )
}

export default App
