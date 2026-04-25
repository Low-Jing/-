export function createPageState() {
  return {
    loading: false,
    empty: false,
    error: ''
  }
}

export function startLoading(state) {
  state.loading = true
  state.empty = false
  state.error = ''
}

export function finishLoading(state, list) {
  state.loading = false
  state.error = ''
  if (Array.isArray(list)) {
    state.empty = list.length === 0
  } else {
    state.empty = !list
  }
}

export function failLoading(state, message) {
  state.loading = false
  state.error = message || '加载失败'
  state.empty = false
}