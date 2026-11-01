import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import {
  Search as SearchIcon,
  Sparkles,
  BookOpen,
  FileText,
  StickyNote,
  ExternalLink,
  ShieldCheck,
  AlertCircle,
  HelpCircle,
  ArrowRight,
  Filter,
  CheckCircle2
} from 'lucide-react';
import { api } from '../services/api';
import { SearchResultItem, RagResponse } from '../types';

export const Search: React.FC = () => {
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';

  const [query, setQuery] = useState(initialQuery);
  const [mode, setMode] = useState<'rag' | 'search'>('rag');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // RAG answer state
  const [ragResult, setRagResult] = useState<RagResponse | null>(null);

  // Hybrid search state
  const [searchResults, setSearchResults] = useState<SearchResultItem[]>([]);

  useEffect(() => {
    if (initialQuery) {
      executeSearch(initialQuery);
    }
  }, [initialQuery]);

  const executeSearch = async (queryString: string) => {
    if (!queryString.trim()) return;

    setLoading(true);
    setError(null);

    try {
      if (mode === 'rag') {
        const res = await api.askRag(queryString);
        setRagResult(res);
      } else {
        const res = await api.search(queryString);
        setSearchResults(res);
      }
    } catch (err: any) {
      setError(err.message || 'Search execution failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeSearch(query);
  };

  const sampleQuestions = [
    'What are the core concepts covered in my notes?',
    'Explain the primary algorithms and their applications.',
    'Summarize key principles of computer systems and architecture.',
  ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto space-y-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-xs font-semibold border border-emerald-200">
          <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
          <span>Retrieval-Augmented Generation (RAG)</span>
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">AI Search & Q&A Engine</h1>
        <p className="text-sm text-slate-500">
          Ask questions in natural language. Answers are strictly grounded in your personal documents and notes with verified source citations.
        </p>
      </div>

      {/* Search Mode Toggle & Input */}
      <div className="bg-white p-4 sm:p-6 rounded-3xl border border-slate-200 shadow-lg space-y-4">
        <div className="flex items-center justify-center space-x-2">
          <button
            type="button"
            onClick={() => setMode('rag')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 ${
              mode === 'rag'
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-950/20'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Q&A Assistant</span>
          </button>
          <button
            type="button"
            onClick={() => setMode('search')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 ${
              mode === 'search'
                ? 'bg-slate-900 text-white shadow-md'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            <SearchIcon className="w-3.5 h-3.5" />
            <span>Keyword & Semantic Search</span>
          </button>
        </div>

        <form onSubmit={handleFormSubmit} className="relative">
          <input
            type="text"
            required
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={
              mode === 'rag'
                ? 'Ask anything about your notes or study documents...'
                : 'Search terms, concepts, algorithms, definitions...'
            }
            className="w-full pl-5 pr-28 py-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition-all shadow-inner"
          />
          <button
            type="submit"
            disabled={loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl shadow transition-all disabled:opacity-50 flex items-center space-x-1.5"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <span>{mode === 'rag' ? 'Ask AI' : 'Search'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </form>

        {/* Suggested Prompts */}
        <div className="flex flex-wrap items-center gap-2 pt-1 text-xs text-slate-500">
          <span className="font-semibold text-slate-400">Try asking:</span>
          {sampleQuestions.map((q, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                setQuery(q);
                executeSearch(q);
              }}
              className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition-colors text-left"
            >
              "{q}"
            </button>
          ))}
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-rose-700 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Mode 1: RAG Response Display */}
      {mode === 'rag' && ragResult && (
        <div className="space-y-6">
          <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-5">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div className="flex items-center space-x-2 text-emerald-700 font-bold text-sm">
                <Sparkles className="w-4 h-4" />
                <span>Grounded Answer</span>
              </div>

              <div className="flex items-center space-x-2">
                {ragResult.is_grounded ? (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                    <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                    Confidence: {(ragResult.confidence_score * 100).toFixed(0)}%
                  </span>
                ) : (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800">
                    <AlertCircle className="w-3.5 h-3.5 mr-1" />
                    Insufficient Knowledge
                  </span>
                )}
              </div>
            </div>

            <div className="text-slate-800 text-sm sm:text-base leading-relaxed whitespace-pre-line font-sans">
              {ragResult.answer}
            </div>

            {/* Citations Box */}
            {ragResult.citations && ragResult.citations.length > 0 && (
              <div className="pt-6 border-t border-slate-100 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Source Citations & Relevant Excerpts ({ragResult.citations.length})
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {ragResult.citations.map((cite, i) => (
                    <div
                      key={i}
                      className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          {cite.source_type === 'document' ? (
                            <FileText className="w-3.5 h-3.5 text-blue-600" />
                          ) : (
                            <StickyNote className="w-3.5 h-3.5 text-purple-600" />
                          )}
                          <span className="text-xs font-bold text-slate-900 line-clamp-1">
                            {cite.source_title}
                          </span>
                        </div>
                        <span className="text-[10px] text-slate-400 font-mono">
                          Relevance {(cite.relevance * 100).toFixed(0)}%
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 line-clamp-3 italic leading-relaxed">
                        "{cite.excerpt}"
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Mode 2: Hybrid Search Results */}
      {mode === 'search' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500 px-1">
            <span>Found {searchResults.length} matching items</span>
          </div>

          {searchResults.length > 0 ? (
            <div className="space-y-3">
              {searchResults.map((item) => (
                <div
                  key={`${item.type}-${item.id}`}
                  className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {item.type === 'document' ? (
                        <span className="p-1.5 bg-blue-50 text-blue-600 rounded-lg">
                          <FileText className="w-4 h-4" />
                        </span>
                      ) : (
                        <span className="p-1.5 bg-purple-50 text-purple-600 rounded-lg">
                          <StickyNote className="w-4 h-4" />
                        </span>
                      )}
                      <h3 className="font-bold text-slate-900 text-sm sm:text-base">
                        {item.title}
                      </h3>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                        {item.category}
                      </span>
                    </div>

                    <span className="text-xs font-mono font-semibold text-emerald-600">
                      Score: {item.relevance_score}
                    </span>
                  </div>

                  <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
                    {item.snippet}
                  </p>

                  {item.tags && item.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 pt-1">
                      {item.tags.map((t, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 bg-slate-100 text-slate-500 rounded text-[10px] font-medium"
                        >
                          #{t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            query &&
            !loading && (
              <div className="bg-white p-12 text-center rounded-2xl border border-slate-200 text-slate-400">
                <SearchIcon className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm font-medium">No results found for "{query}"</p>
                <p className="text-xs mt-1">Try broader terms or switch to AI Q&A mode.</p>
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
};
