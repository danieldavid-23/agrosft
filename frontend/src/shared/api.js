import { getCSRFToken } from './csrf.js'

export async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'Content-Type': 'application/x-www-form-urlencoded',
      ...options.headers,
    },
    ...options,
  })
  return res.json()
}
