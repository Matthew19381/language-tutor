import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import LoadingSpinner, { PageLoader, InlineLoader } from '../LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders without text by default', () => {
    const { container } = render(<LoadingSpinner />)
    expect(container.querySelector('.animate-spin')).toBeTruthy()
    expect(screen.queryByRole('paragraph')).toBeNull()
  })

  it('renders text when provided', () => {
    render(<LoadingSpinner text="Loading data..." />)
    expect(screen.getByText('Loading data...')).toBeInTheDocument()
  })

  it('applies md size class by default', () => {
    const { container } = render(<LoadingSpinner />)
    const spinner = container.querySelector('.animate-spin')
    expect(spinner.className).toContain('h-8')
    expect(spinner.className).toContain('w-8')
  })

  it('applies lg size class when size="lg"', () => {
    const { container } = render(<LoadingSpinner size="lg" />)
    const spinner = container.querySelector('.animate-spin')
    expect(spinner.className).toContain('h-12')
    expect(spinner.className).toContain('w-12')
  })

  it('applies sm size class when size="sm"', () => {
    const { container } = render(<LoadingSpinner size="sm" />)
    const spinner = container.querySelector('.animate-spin')
    expect(spinner.className).toContain('h-4')
    expect(spinner.className).toContain('w-4')
  })
})

describe('PageLoader', () => {
  it('renders with default text', () => {
    render(<PageLoader />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders with custom text', () => {
    render(<PageLoader text="Fetching lesson..." />)
    expect(screen.getByText('Fetching lesson...')).toBeInTheDocument()
  })

  it('renders inside a min-height container', () => {
    const { container } = render(<PageLoader />)
    const wrapper = container.firstChild
    expect(wrapper.className).toContain('min-h-')
  })
})

describe('InlineLoader', () => {
  it('renders with "Loading..." text', () => {
    render(<InlineLoader />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders a small spinner', () => {
    const { container } = render(<InlineLoader />)
    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toBeTruthy()
    expect(spinner.className).toContain('h-4')
  })
})
