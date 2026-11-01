import React, { useState, useEffect } from 'react';
import {
  HelpCircle,
  Plus,
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  Award,
  Sparkles,
  BookOpen,
  ArrowRight,
  RotateCcw,
  X
} from 'lucide-react';
import { api } from '../services/api';
import { Quiz, QuizResult, QuizAttemptHistory, DocumentItem, NoteItem } from '../types';

export const Quizzes: React.FC = () => {
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [history, setHistory] = useState<QuizAttemptHistory[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [notes, setNotes] = useState<NoteItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Active quiz state
  const [activeQuiz, setActiveQuiz] = useState<Quiz | null>(null);
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({});
  const [quizTimer, setQuizTimer] = useState(0);
  const [quizResult, setQuizResult] = useState<QuizResult | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Generate modal
  const [isGenerateOpen, setIsGenerateOpen] = useState(false);
  const [quizTitle, setQuizTitle] = useState('');
  const [sourceType, setSourceType] = useState('all');
  const [sourceId, setSourceId] = useState<number | undefined>(undefined);
  const [questionCount, setQuestionCount] = useState(5);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [quizzesData, historyData, docsData, notesData] = await Promise.all([
        api.getQuizzes(),
        api.getQuizHistory(),
        api.getDocuments(),
        api.getNotes(),
      ]);
      setQuizzes(quizzesData);
      setHistory(historyData);
      setDocuments(docsData);
      setNotes(notesData);
    } catch (err: any) {
      console.error('Failed to load quiz data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateQuiz = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quizTitle.trim()) return;

    setGenerating(true);
    try {
      const newQuiz = await api.generateQuiz({
        title: quizTitle.trim(),
        source_type: sourceType,
        source_id: sourceId,
        question_count: questionCount,
      });
      setQuizzes([newQuiz, ...quizzes]);
      setIsGenerateOpen(false);
      setQuizTitle('');
      startTakingQuiz(newQuiz);
    } catch (err: any) {
      alert(err.message || 'Failed to generate quiz.');
    } finally {
      setGenerating(false);
    }
  };

  const startTakingQuiz = (quiz: Quiz) => {
    setActiveQuiz(quiz);
    setUserAnswers({});
    setQuizResult(null);
    setQuizTimer(0);
  };

  const handleAnswerSelect = (questionId: number, answerText: string) => {
    setUserAnswers((prev) => ({
      ...prev,
      [questionId]: answerText,
    }));
  };

  const handleSubmitQuiz = async () => {
    if (!activeQuiz) return;
    setSubmitting(true);

    const answersList = activeQuiz.questions.map((q) => ({
      question_id: q.id,
      user_answer: userAnswers[q.id] || '',
    }));

    try {
      const result = await api.submitQuiz(activeQuiz.id, answersList, quizTimer);
      setQuizResult(result);
      const updatedHistory = await api.getQuizHistory();
      setHistory(updatedHistory);
    } catch (err: any) {
      alert(err.message || 'Failed to submit quiz.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">AI Quiz Generator</h1>
          <p className="text-sm text-slate-500">
            Generate multiple-choice quizzes directly from your study notes and documents to test comprehension.
          </p>
        </div>
        {!activeQuiz && (
          <button
            onClick={() => setIsGenerateOpen(true)}
            className="inline-flex items-center space-x-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-xl shadow-md transition-all text-sm self-start sm:self-auto"
          >
            <Sparkles className="w-4 h-4" />
            <span>Generate New Quiz</span>
          </button>
        )}
      </div>

      {/* Mode 1: Active Quiz Taking Mode */}
      {activeQuiz && !quizResult && (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-xl p-6 sm:p-8 space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                In Progress
              </span>
              <h2 className="text-xl font-bold text-slate-900 mt-1">{activeQuiz.title}</h2>
            </div>
            <button
              onClick={() => setActiveQuiz(null)}
              className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Question List */}
          <div className="space-y-6">
            {activeQuiz.questions.map((q, idx) => (
              <div key={q.id} className="p-5 bg-slate-50 rounded-2xl border border-slate-100 space-y-3">
                <div className="flex items-center space-x-2">
                  <span className="w-6 h-6 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center">
                    {idx + 1}
                  </span>
                  <h3 className="font-semibold text-slate-900 text-sm">{q.question_text}</h3>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-2">
                  {q.options?.map((opt, optIdx) => {
                    const isSelected = userAnswers[q.id] === opt;
                    return (
                      <button
                        key={optIdx}
                        type="button"
                        onClick={() => handleAnswerSelect(q.id, opt)}
                        className={`p-3 text-left rounded-xl text-xs sm:text-sm font-medium transition-all border ${
                          isSelected
                            ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                            : 'bg-white text-slate-700 border-slate-200 hover:border-emerald-300'
                        }`}
                      >
                        {opt}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end pt-4 border-t border-slate-100">
            <button
              onClick={handleSubmitQuiz}
              disabled={submitting}
              className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm rounded-xl shadow-lg shadow-emerald-950/20 transition-all flex items-center space-x-2"
            >
              {submitting ? 'Evaluating...' : 'Submit Answers & Grade'}
            </button>
          </div>
        </div>
      )}

      {/* Mode 2: Quiz Result Breakdown */}
      {quizResult && (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-xl p-6 sm:p-8 space-y-6">
          <div className="text-center max-w-md mx-auto space-y-2">
            <div className="w-16 h-16 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto mb-2">
              <Award className="w-8 h-8" />
            </div>
            <h2 className="text-2xl font-extrabold text-slate-900">{quizResult.quiz_title}</h2>
            <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-slate-100 font-bold text-slate-800 text-lg">
              <span>Score: {quizResult.score}%</span>
              <span className="text-xs text-slate-500 font-normal">
                ({quizResult.correct_count} of {quizResult.total_questions} correct)
              </span>
            </div>
          </div>

          {/* Detailed Question Review */}
          <div className="space-y-4 pt-4">
            <h3 className="font-bold text-slate-900 text-base">Detailed Question Explanations</h3>
            {quizResult.evaluations.map((ev, i) => (
              <div
                key={ev.question_id}
                className={`p-4 rounded-2xl border space-y-2 ${
                  ev.is_correct
                    ? 'bg-emerald-50/50 border-emerald-200'
                    : 'bg-rose-50/50 border-rose-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2">
                    {ev.is_correct ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                    ) : (
                      <XCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
                    )}
                    <span className="font-semibold text-slate-900 text-sm">
                      Question {i + 1}: {ev.question_text}
                    </span>
                  </div>
                  <span
                    className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                      ev.is_correct ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                    }`}
                  >
                    {ev.is_correct ? 'Correct' : 'Needs Review'}
                  </span>
                </div>

                <div className="text-xs space-y-1 pl-6">
                  <p className="text-slate-600">
                    Your answer: <span className="font-bold">{ev.user_answer || '(No answer)'}</span>
                  </p>
                  {!ev.is_correct && (
                    <p className="text-emerald-700 font-semibold">
                      Correct answer: {ev.correct_answer}
                    </p>
                  )}
                  {ev.explanation && (
                    <p className="text-slate-500 italic mt-1">{ev.explanation}</p>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-slate-100">
            <button
              onClick={() => setActiveQuiz(null)}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl"
            >
              Back to Quiz List
            </button>
            <button
              onClick={() => {
                if (activeQuiz) startTakingQuiz(activeQuiz);
              }}
              className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl flex items-center space-x-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Retry Quiz</span>
            </button>
          </div>
        </div>
      )}

      {/* Mode 3: Quizzes Library and History */}
      {!activeQuiz && (
        <div className="space-y-6">
          {/* Available Quizzes */}
          <div>
            <h3 className="font-bold text-slate-900 text-lg mb-3">Available Quizzes</h3>
            {quizzes.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {quizzes.map((quiz) => (
                  <div
                    key={quiz.id}
                    className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
                  >
                    <div className="space-y-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                        {quiz.source_type}
                      </span>
                      <h4 className="font-bold text-slate-900 text-base">{quiz.title}</h4>
                      <p className="text-xs text-slate-500">{quiz.question_count} Questions</p>
                    </div>

                    <button
                      onClick={() => startTakingQuiz(quiz)}
                      className="mt-4 w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl flex items-center justify-center space-x-1.5 transition-colors"
                    >
                      <Play className="w-3.5 h-3.5" />
                      <span>Take Quiz</span>
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white p-8 text-center rounded-2xl border border-slate-200 text-slate-400">
                <HelpCircle className="w-8 h-8 mx-auto mb-2 text-slate-300" />
                <p className="text-sm font-medium">No quizzes generated yet</p>
                <p className="text-xs mt-1">Click "Generate New Quiz" above to create one.</p>
              </div>
            )}
          </div>

          {/* Past Attempts History */}
          {history.length > 0 && (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <h3 className="font-bold text-slate-900 text-base mb-4">Past Quiz Attempts</h3>
              <div className="divide-y divide-slate-100">
                {history.map((att) => (
                  <div key={att.id} className="py-3 flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-slate-800">{att.quiz_title}</p>
                      <p className="text-xs text-slate-400">
                        {att.correct_count}/{att.total_questions} questions correct •{' '}
                        {new Date(att.completed_at).toLocaleDateString()}
                      </p>
                    </div>
                    <span
                      className={`text-xs font-bold px-3 py-1 rounded-full ${
                        att.score >= 80
                          ? 'bg-emerald-100 text-emerald-800'
                          : att.score >= 50
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {att.score}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Generate Quiz Modal */}
      {isGenerateOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-md w-full p-6 relative">
            <button
              onClick={() => setIsGenerateOpen(false)}
              className="absolute top-4 right-4 p-1.5 text-slate-400 hover:text-slate-700 rounded-lg"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-lg font-bold text-slate-900 mb-1">Generate AI Quiz</h3>
            <p className="text-xs text-slate-500 mb-4">
              Select knowledge sources to create questions strictly grounded in your materials.
            </p>

            <form onSubmit={handleCreateQuiz} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">
                  Quiz Title
                </label>
                <input
                  type="text"
                  required
                  value={quizTitle}
                  onChange={(e) => setQuizTitle(e.target.value)}
                  placeholder="e.g. Operating Systems Midterm Prep"
                  className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">
                  Source Material
                </label>
                <select
                  value={sourceType}
                  onChange={(e) => {
                    setSourceType(e.target.value);
                    setSourceId(undefined);
                  }}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="all">Entire Knowledge Library (All Documents & Notes)</option>
                  <option value="document">Specific Document</option>
                  <option value="note">Specific Study Note</option>
                </select>
              </div>

              {sourceType === 'document' && (
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">
                    Select Document
                  </label>
                  <select
                    value={sourceId || ''}
                    onChange={(e) => setSourceId(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  >
                    <option value="">Choose document...</option>
                    {documents.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.title}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {sourceType === 'note' && (
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">
                    Select Note
                  </label>
                  <select
                    value={sourceId || ''}
                    onChange={(e) => setSourceId(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  >
                    <option value="">Choose note...</option>
                    {notes.map((n) => (
                      <option key={n.id} value={n.id}>
                        {n.title}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1">
                  Number of Questions
                </label>
                <select
                  value={questionCount}
                  onChange={(e) => setQuestionCount(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value={3}>3 Questions (Quick Test)</option>
                  <option value={5}>5 Questions (Standard)</option>
                  <option value={10}>10 Questions (Comprehensive)</option>
                </select>
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsGenerateOpen(false)}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={generating}
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl shadow transition-all disabled:opacity-50 flex items-center space-x-1.5"
                >
                  {generating ? (
                    <>
                      <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Generating...</span>
                    </>
                  ) : (
                    <span>Create Quiz</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
