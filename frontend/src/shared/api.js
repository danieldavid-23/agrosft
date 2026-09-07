import { getCSRFToken } from './csrf.js'

export async function apiFetch(url, options = {}) {
  try {
    const res = await fetch(url, {
      headers: {
        'X-CSRFToken': getCSRFToken(),
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest',
        ...options.headers,
      },
      ...options,
    })

    if (!res.ok) {
      let errorMsg = `Error ${res.status}: ${res.statusText || 'Petición fallida'}`
      try {
        const errorData = await res.json()
        if (errorData && errorData.error) {
          errorMsg = errorData.error
        }
      } catch (_) {
        // La respuesta no es JSON, se conserva el errorMsg general
      }
      throw new Error(errorMsg)
    }

    const contentType = res.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      return await res.json()
    }
    return await res.text()
  } catch (error) {
    console.error('apiFetch error:', error)
    throw error
  }
}

