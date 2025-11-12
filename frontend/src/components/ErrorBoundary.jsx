import React from 'react'

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }
  componentDidCatch(error, info) {
    // eslint-disable-next-line no-console
    console.error('ErrorBoundary caught', error, info)
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="max-w-xl mx-auto p-4">
          <div className="rounded border bg-[#FFF6F6] text-[#8B0000] p-4">
            <div className="font-bold mb-1">Something went wrong</div>
            <div className="text-sm">Please try again or refresh the page.</div>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}