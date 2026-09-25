// ===== AI GENERATED: TodoApp =====
// Purpose: Simple UI to list/create/delete Todos
// Inputs: uses `todoService` for API calls
// Returns: React component rendering basic Todo functionality
// Flow:
// 1. Load todos on mount
// 2. Allow creating and toggling completion

import { useEffect, useState } from 'react'
import { listTodos, createTodo, updateTodo, deleteTodo } from '../services/todoService'

export default function TodoApp() {
  const [todos, setTodos] = useState([])
  const [title, setTitle] = useState('')

  useEffect(() => {
    fetchTodos()
  }, [])

  async function fetchTodos() {
    const data = await listTodos()
    setTodos(data)
  }

  async function handleCreate(e) {
    e.preventDefault()
    if (!title.trim()) return
    await createTodo({ title })
    setTitle('')
    fetchTodos()
  }

  async function toggleCompleted(todo) {
    await updateTodo(todo.id, { completed: !todo.completed })
    fetchTodos()
  }

  async function handleDelete(id) {
    await deleteTodo(id)
    fetchTodos()
  }

  return (
    <div className="p-4 max-w-lg mx-auto">
      <h2 className="text-xl font-bold mb-2">Todos</h2>
      <form onSubmit={handleCreate} className="mb-4">
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="New todo" className="border p-2 mr-2" />
        <button className="bg-blue-500 text-white px-3 py-1">Add</button>
      </form>
      <ul>
        {todos.map((t) => (
          <li key={t.id} className="flex items-center justify-between mb-2">
            <div>
              <label>
                <input type="checkbox" checked={t.completed} onChange={() => toggleCompleted(t)} />
                <span className="ml-2">{t.title}</span>
              </label>
            </div>
            <button onClick={() => handleDelete(t.id)} className="text-red-500">Delete</button>
          </li>
        ))}
      </ul>
    </div>
  )
}
