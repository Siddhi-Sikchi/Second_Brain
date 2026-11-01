import React, { useState, useEffect } from 'react';
import {
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Calendar,
  Sparkles,
  ArrowRight,
  Flame,
  ThumbsUp,
  Smile,
  Frown,
  Eye
} from 'lucide-react';
import { api } from '../services/api';
import { RevisionItem } from '../types';

export const Revision: React.FC = () => {
  const [dueItems, setDueItems] = useState<RevisionItem[]>([]);
  const [allItems, setAllItems] = useState<RevisionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeItemIndex, setActiveItemIndex] = useState(0);
  const [isRevealed, setIsRevealed] = useState(false);
  const [reviewing, setReviewing] = useState(false);

  useEffect(() => {
    loadRevisions();
  }, []);

  const loadRevisions = async () => {
    try {
      setLoading(true);
      const [due, all] = await Promise.all([
        api.getDueRevisions(),
        api.getAllRevisions(),
      ]);
      setDueItems(due);
      setAllItems(all);
    } catch (err: any) {
      console.error('Failed to load revision items', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRating = async (rating: 'again' | 'hard' | 'good' | 'easy') => {
    if (dueItems.length === 0) return;
    const current = dueItems[activeItemIndex];

    setReviewing(true);
    try {
      await api.reviewRevisionItem(current.id, rating);
      // Remove from due items
      const updatedDue = dueItems.filter((_, idx) => idx !== activeItemIndex);
      setDueItems(updatedDue);
      setIsRevealed(false);
      if (activeItemIndex >= updatedDue.length) {
        setActiveItemIndex(0);
      }
    } catch (err: any) {
      alert(err.message || 'Failed to submit review.');
    } finally {
      setReviewing(false);
    }
  };

  const currentItem = dueItems[activeItemIndex];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center max-w-xl mx-auto space-y-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 bg-emerald-50 text-emerald-800 rounded-full text-xs font-semibold border border-emerald-200">
          <RotateCcw className="w-3.5 h-3.5 text-emerald-600" />
          <span>SuperMemo SM-2 Spaced Repetition</span>
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Daily Revision Queue</h1>
        <p className="text-sm text-slate-500">
          Review critical notes and questions you missed during quizzes right before you forget them.
        </p>
      </div>

      {/* Main Flashcard Card */}
      {loading ? (
        <div className="h-64 flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : currentItem ? (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-xl p-8 sm:p-10 space-y-8 flex flex-col justify-between min-h-[420px]">
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs text-slate-400 pb-3 border-b border-slate-100">
              <span className="font-semibold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full">
                Item {activeItemIndex + 1} of {dueItems.length} Due Today
              </span>
              <span>Repetition Level: {currentItem.repetition_level}</span>
            </div>

            <div>
              <h3 className="text-xl sm:text-2xl font-bold text-slate-900 leading-snug">
                {currentItem.title}
              </h3>
            </div>

            {/* Revealed Answer Content */}
            {isRevealed ? (
              <div className="p-6 bg-slate-50 border border-slate-200 rounded-2xl space-y-2 animate-fadeIn">
                <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Answer / Explanation:</p>
                <p className="text-sm sm:text-base text-slate-800 leading-relaxed whitespace-pre-line font-sans">
                  {currentItem.content_preview || 'No additional explanation available.'}
                </p>
              </div>
            ) : (
              <div className="py-12 flex flex-col items-center justify-center text-slate-400">
                <button
                  type="button"
                  onClick={() => setIsRevealed(true)}
                  className="px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm rounded-2xl flex items-center space-x-2 transition-all shadow-sm"
                >
                  <Eye className="w-4 h-4" />
                  <span>Reveal Answer</span>
                </button>
              </div>
            )}
          </div>

          {/* SM-2 Feedback Buttons */}
          {isRevealed && (
            <div className="pt-6 border-t border-slate-100 space-y-3">
              <p className="text-center text-xs font-semibold text-slate-400 uppercase tracking-wider">
                How well did you recall this concept?
              </p>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <button
                  onClick={() => handleRating('again')}
                  disabled={reviewing}
                  className="p-3 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 font-bold text-xs rounded-xl flex flex-col items-center space-y-1 transition-all"
                >
                  <span>Again</span>
                  <span className="text-[10px] font-normal text-rose-500">&lt; 1 Day</span>
                </button>

                <button
                  onClick={() => handleRating('hard')}
                  disabled={reviewing}
                  className="p-3 bg-amber-50 hover:bg-amber-100 text-amber-700 border border-amber-200 font-bold text-xs rounded-xl flex flex-col items-center space-y-1 transition-all"
                >
                  <span>Hard</span>
                  <span className="text-[10px] font-normal text-amber-500">~2 Days</span>
                </button>

                <button
                  onClick={() => handleRating('good')}
                  disabled={reviewing}
                  className="p-3 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 font-bold text-xs rounded-xl flex flex-col items-center space-y-1 transition-all"
                >
                  <span>Good</span>
                  <span className="text-[10px] font-normal text-blue-500">~4 Days</span>
                </button>

                <button
                  onClick={() => handleRating('easy')}
                  disabled={reviewing}
                  className="p-3 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 font-bold text-xs rounded-xl flex flex-col items-center space-y-1 transition-all"
                >
                  <span>Easy</span>
                  <span className="text-[10px] font-normal text-emerald-500">&gt; 7 Days</span>
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200 p-12 text-center max-w-md mx-auto space-y-3">
          <div className="w-14 h-14 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-2">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <h3 className="font-bold text-slate-900 text-lg">All caught up for today!</h3>
          <p className="text-xs text-slate-500 leading-relaxed">
            You have reviewed all due cards. Take quizzes or create new notes to schedule future spaced repetition intervals.
          </p>
        </div>
      )}

      {/* Revision Queue Overview */}
      {allItems.length > 0 && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <h3 className="font-bold text-slate-900 text-base">All Scheduled Items ({allItems.length})</h3>
          <div className="divide-y divide-slate-100 max-h-60 overflow-y-auto">
            {allItems.map((item) => (
              <div key={item.id} className="py-2.5 flex items-center justify-between text-xs">
                <span className="font-medium text-slate-800 line-clamp-1">{item.title}</span>
                <span className="text-slate-400 whitespace-nowrap ml-4">
                  Next review: {new Date(item.next_review_date).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
