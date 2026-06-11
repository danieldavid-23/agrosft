export function getCSRFToken() {
  return document.cookie.split('; ')
    .find(r => r.startsWith('csrftoken='))
    ?.split('=')[1]
}
