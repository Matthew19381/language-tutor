import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import NavBar from '../NavBar'

// Mock the API client — NavBar calls getStats on mount
vi.mock('../../api/client', () => ({
  getUserId: vi.fn(() => null),
  getStats: vi.fn(() => Promise.resolve(null)),
}))

function renderNavBar(initialPath = '/') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <NavBar />
    </MemoryRouter>
  )
}

describe('NavBar', () => {
  it('renders the LinguaAI logo text', () => {
    renderNavBar()
    expect(screen.getByText('LinguaAI')).toBeInTheDocument()
  })

  it('renders all nav items', () => {
    renderNavBar()
    expect(screen.getByText('Lesson')).toBeInTheDocument()
    expect(screen.getByText('Test')).toBeInTheDocument()
    expect(screen.getByText('Flashcards')).toBeInTheDocument()
    expect(screen.getByText('Speak')).toBeInTheDocument()
    expect(screen.getByText('15 min')).toBeInTheDocument()
    expect(screen.getByText('News')).toBeInTheDocument()
    expect(screen.getByText('Pronounce')).toBeInTheDocument()
    expect(screen.getByText('Stats')).toBeInTheDocument()
  })

  it('renders "Get Started" button when no user is logged in', () => {
    renderNavBar()
    expect(screen.getByText('Get Started')).toBeInTheDocument()
  })

  it('"Get Started" links to /placement', () => {
    renderNavBar()
    const link = screen.getByText('Get Started').closest('a')
    expect(link).toHaveAttribute('href', '/placement')
  })

  it('nav links have correct href attributes', () => {
    renderNavBar()
    const lessonLink = screen.getByText('Lesson').closest('a')
    expect(lessonLink).toHaveAttribute('href', '/lesson')

    const testLink = screen.getByText('Test').closest('a')
    expect(testLink).toHaveAttribute('href', '/test')
  })

  it('renders inside a sticky nav element', () => {
    const { container } = renderNavBar()
    const nav = container.querySelector('nav')
    expect(nav).toBeTruthy()
    expect(nav.className).toContain('sticky')
  })
})

describe('NavBar with logged-in user', () => {
  beforeEach(() => {
    const { getUserId, getStats } = vi.mocked(
      // eslint-disable-next-line no-undef
      await import('../../api/client')
    )
    getUserId.mockReturnValue(1)
    getStats.mockResolvedValue({
      user: { streak_days: 5, total_xp: 100, cefr_level: 'B1' },
    })
  })

  it('does not render "Get Started" when user exists', async () => {
    const { getUserId } = await import('../../api/client')
    getUserId.mockReturnValue(42)

    renderNavBar()
    // "Get Started" should not be visible when userId is set
    // (it's rendered via !userStats && !userId, so with userId set it won't show)
    // Note: userStats is still null until the async getStats resolves
    expect(screen.queryByText('Get Started')).toBeNull()
  })
})
