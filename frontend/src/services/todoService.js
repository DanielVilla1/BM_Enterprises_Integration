// ===== AI GENERATED: todoService =====
// Purpose: Axios wrapper for Todo CRUD
// Inputs: uses VITE_API_BASE_URL
// Returns: functions: listTodos, getTodo, createTodo, updateTodo, deleteTodo
// Flow:
// 1. Create axios instance
// 2. Export CRUD helpers

import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const api = axios.create({ baseURL })

export async function listTodos() {
  const res = await api.get('/todos/')
  return res.data
}

export async function getTodo(id) {
  const res = await api.get(`/todos/${id}`)
  return res.data
}

export async function createTodo(payload) {
  const res = await api.post('/todos/', payload)
  return res.data
}

export async function updateTodo(id, payload) {
  const res = await api.put(`/todos/${id}`, payload)
  return res.data
}

export async function deleteTodo(id) {
  const res = await api.delete(`/todos/${id}`)
  return res.data
}

export async function checkBackend() {
  const res = await api.get('/health')
  return res.data
}

export async function checkDb() {
  const res = await api.get('/health/db')
  return res.data
}
