"""Pydantic schemas for request/response validation."""
from backend.schemas.conversation import (
    StartConversationRequest,
    MessageRequest,
    AnalyzeRequest,
    QuestionRequest,
    AnalyzePastedRequest,
    TranslateRequest,
)
from backend.schemas.lesson import (
    CompleteLessonRequest,
    SaveExerciseErrorRequest,
    ExerciseErrorRequest,
    EvaluateProductionRequest,
    NextLessonRequest,
    ConceptFlashcardRequest,
)
from backend.schemas.test import (
    SubmitTestRequest,
)
from backend.schemas.flashcard import (
    AddFlashcardRequest,
    ReviewFlashcardRequest,
    AddFlashcardAIRequest,
)
from backend.schemas.pronunciation import (
    AnalyzePronunciationRequest,
)
from backend.schemas.placement import (
    StartPlacementRequest,
    SubmitPlacementRequest,
    CreateUserRequest,
    UpdateLanguageRequest,
)

__all__ = [
    "StartConversationRequest",
    "MessageRequest",
    "AnalyzeRequest",
    "QuestionRequest",
    "AnalyzePastedRequest",
    "TranslateRequest",
    "CompleteLessonRequest",
    "SaveExerciseErrorRequest",
    "ExerciseErrorRequest",
    "EvaluateProductionRequest",
    "NextLessonRequest",
    "ConceptFlashcardRequest",
    "SubmitTestRequest",
    "AddFlashcardRequest",
    "ReviewFlashcardRequest",
    "AddFlashcardAIRequest",
    "AnalyzePronunciationRequest",
    "StartPlacementRequest",
    "SubmitPlacementRequest",
    "CreateUserRequest",
    "UpdateLanguageRequest",
]
