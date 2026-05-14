import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-900 p-4">
          <div className="bg-gray-800 border border-red-500/30 rounded-xl p-8 max-w-md text-center">
            <div className="text-5xl mb-4">⚠️</div>
            <h2 className="text-xl font-bold text-red-400 mb-2">Coś poszło nie tak</h2>
            <p className="text-gray-400 text-sm mb-4">
              Wystąpił nieoczekiwany błąd. Spróbuj odświeżyć stronę.
            </p>
            <button
              onClick={() => { this.setState({ hasError: false, error: null }) }}
              className="btn-primary"
            >
              Spróbuj ponownie
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
