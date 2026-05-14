import { Routes, Route } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import Layout from './components/Layout'
import Home from './pages/Home'
import PlacementTest from './pages/PlacementTest'
import DailyLesson from './pages/DailyLesson'
import DailyTest from './pages/DailyTest'
import Flashcards from './pages/Flashcards'
import Conversation from './pages/Conversation'
import Stats from './pages/Stats'
import QuickMode from './pages/QuickMode'
import News from './pages/News'
import PronunciationTrainer from './pages/PronunciationTrainer'
import LessonHistory from './pages/LessonHistory'
import Videos from './pages/Videos'
import ErrorReview from './pages/ErrorReview'
import TopicsPage from './pages/TopicsPage'

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="lesson" element={<DailyLesson />} />
          <Route path="lesson/history" element={<LessonHistory />} />
          <Route path="lesson/:lessonId" element={<DailyLesson />} />
          <Route path="test" element={<DailyTest />} />
          <Route path="flashcards" element={<Flashcards />} />
          <Route path="conversation" element={<Conversation />} />
          <Route path="stats" element={<Stats />} />
          <Route path="quickmode" element={<QuickMode />} />
          <Route path="news" element={<News />} />
          <Route path="pronunciation" element={<PronunciationTrainer />} />
          <Route path="videos" element={<Videos />} />
          <Route path="errors" element={<ErrorReview />} />
          <Route path="topics" element={<TopicsPage />} />
        </Route>
        <Route path="/placement" element={<PlacementTest />} />
      </Routes>
    </ErrorBoundary>
  )
}

export default App
