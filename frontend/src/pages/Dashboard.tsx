import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  StickyNote,
  HelpCircle,
  Flame,
  HardDrive,
  BookOpen,
  ArrowUpRight,
  Sparkles,
  Plus,
  Clock,
  Tag as TagIcon,
  BrainCircuit
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell
} from 'recharts';
import { api } from '../services/api';
import { AnalyticsSummary } from '../types';
import { useAuth } from '../context/AuthContext';

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [data, setData] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const summary = await api.getAnalytics();
        setData(summary);
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard metrics.');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const categoryChartData = data?.categories
    ? Object.entries(data.categories).map(([name, count]) => ({ name, count }))
    : [];

  const COLORS = ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ec4899', '#06b6d4'];

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 KB';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-emerald-900 to-slate-900 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="inline-flex items-center space-x-2 px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full text-xs font-semibold backdrop-blur-sm border border-emerald-500/30">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Knowledge Space Ready</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
            Welcome back, {user?.full_name?.split(' ')[0]}!
          </h2>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Your second brain is actively indexing notes, extracting insights, and preparing revision schedules. What would you like to learn today?
          </p>

          <div className="flex flex-wrap gap-3 pt-2">
            <Link
              to="/documents"
              className="inline-flex items-center space-x-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-xl shadow-md transition-all"
            >
              <Plus className="w-4 h-4" />
              <span>Upload Document</span>
            </Link>
            <Link
              to="/notes"
              className="inline-flex items-center space-x-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold rounded-xl border border-slate-700 transition-all"
            >
              <StickyNote className="w-4 h-4 text-emerald-400" />
              <span>New Note</span>
            </Link>
            <Link
              to="/search"
              className="inline-flex items-center space-x-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold rounded-xl border border-slate-700 transition-all"
            >
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>Ask AI RAG</span>
            </Link>
          </div>
        </div>

        {/* Background decorative pattern */}
        <div className="absolute right-0 top-0 bottom-0 w-1/3 opacity-10 pointer-events-none flex items-center justify-center">
          <BrainCircuit className="w-96 h-96 text-white" />
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Documents</p>
            <h3 className="text-2xl font-bold text-slate-900">{data?.total_documents || 0}</h3>
            <p className="text-xs text-slate-400 mt-0.5">{formatBytes(data?.storage_used_bytes || 0)} stored</p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
            <StickyNote className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Study Notes</p>
            <h3 className="text-2xl font-bold text-slate-900">{data?.total_notes || 0}</h3>
            <p className="text-xs text-slate-400 mt-0.5">{data?.total_words?.toLocaleString() || 0} total words</p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
            <HelpCircle className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Quizzes Taken</p>
            <h3 className="text-2xl font-bold text-slate-900">{data?.total_quizzes_taken || 0}</h3>
            <p className="text-xs text-amber-600 font-semibold mt-0.5">
              {data?.average_quiz_score ? `${data.average_quiz_score}% avg` : 'No attempts yet'}
            </p>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center">
            <Flame className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Learning Streak</p>
            <h3 className="text-2xl font-bold text-slate-900">{data?.active_streak_days || 0} Days</h3>
            <p className="text-xs text-emerald-600 font-semibold mt-0.5">Active momentum</p>
          </div>
        </div>
      </div>

      {/* Analytics and Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Distribution Chart */}
        <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-bold text-slate-900 text-base">Knowledge Topics & Categories</h3>
              <p className="text-xs text-slate-500">Distribution of items across subjects</p>
            </div>
            <Link to="/documents" className="text-xs font-semibold text-emerald-600 hover:text-emerald-700 flex items-center">
              <span>View all</span>
              <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
            </Link>
          </div>

          {categoryChartData.length > 0 ? (
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryChartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} interval={0} angle={-15} textAnchor="end" />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', border: 'none', color: '#fff', fontSize: '12px' }}
                  />
                  <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                    {categoryChartData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-400 space-y-2">
              <BookOpen className="w-10 h-10 stroke-[1.5]" />
              <p className="text-sm font-medium">No documents or notes categorized yet</p>
              <Link to="/documents" className="text-xs text-emerald-600 font-semibold">Upload your first document</Link>
            </div>
          )}
        </div>

        {/* Top Tags & Concepts Card */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="font-bold text-slate-900 text-base mb-1">Top Tags & Concepts</h3>
            <p className="text-xs text-slate-500 mb-5">Auto-generated topical tags in your library</p>

            {data?.top_tags && data.top_tags.length > 0 ? (
              <div className="space-y-3">
                {data.top_tags.map((tag) => (
                  <div key={tag.id} className="flex items-center justify-between p-2.5 bg-slate-50 rounded-xl hover:bg-slate-100 transition-colors">
                    <div className="flex items-center space-x-2.5">
                      <TagIcon className="w-4 h-4 text-emerald-600" />
                      <span className="text-sm font-medium text-slate-800">#{tag.name}</span>
                    </div>
                    <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-xs font-semibold rounded-full">
                      {tag.count} items
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-48 flex flex-col items-center justify-center text-slate-400 space-y-2">
                <TagIcon className="w-8 h-8 stroke-[1.5]" />
                <p className="text-xs font-medium">Tags will appear as you add content</p>
              </div>
            )}
          </div>

          <Link
            to="/graph"
            className="mt-6 w-full py-2.5 px-4 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold rounded-xl flex items-center justify-center space-x-2 transition-colors"
          >
            <span>Explore Knowledge Graph</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Recent Activity Stream */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <h3 className="font-bold text-slate-900 text-base mb-1">Recent Activity</h3>
        <p className="text-xs text-slate-500 mb-6">Latest events in your knowledge base</p>

        {data?.recent_activity && data.recent_activity.length > 0 ? (
          <div className="divide-y divide-slate-100">
            {data.recent_activity.map((item, index) => (
              <div key={index} className="py-3 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-500" />
                  <div>
                    <p className="text-sm font-medium text-slate-800">{item.title}</p>
                    <span className="text-xs text-slate-400">{item.category}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-1 text-xs text-slate-400">
                  <Clock className="w-3.5 h-3.5" />
                  <span>{new Date(item.timestamp).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-400 py-6 text-center">No recent activities recorded yet.</p>
        )}
      </div>
    </div>
  );
};
