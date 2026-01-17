'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Topic {
  id: number;
  syllabus_id: number;
  parent_id: number | null;
  order_index: number;
  level: number;
  title: string;
  code: string | null;
  content: string | null;
  source_type: 'normativa' | 'manual' | 'ai_generated' | 'pending';
  source_reference: string | null;
  source_excerpt: string | null;
  content_status: 'empty' | 'partial' | 'complete' | 'verified';
  is_expanded: boolean;
  children: Topic[];
}

interface SyllabusDetail {
  id: number;
  name: string;
  description: string | null;
  total_topics: number;
  processed_topics: number;
  topics: Topic[];
}

interface Stats {
  total_topics: number;
  processed_topics: number;
  progress_percentage: number;
  by_status: Record<string, number>;
  by_source: Record<string, number>;
}

export default function SyllabusDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { token, loading: authLoading } = useAuth();
  const syllabusId = params.id as string;

  const [syllabus, setSyllabus] = useState<SyllabusDetail | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // UI State
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
  const [expandedTopics, setExpandedTopics] = useState<Set<number>>(new Set());
  const [showAddTopicModal, setShowAddTopicModal] = useState(false);
  const [parentForNewTopic, setParentForNewTopic] = useState<Topic | null>(null);
  const [newTopic, setNewTopic] = useState({ title: '', code: '', content: '' });
  const [editingTopic, setEditingTopic] = useState(false);

  useEffect(() => {
    if (!authLoading && !token) {
      router.push('/login');
    }
  }, [authLoading, token, router]);

  useEffect(() => {
    if (token && syllabusId) {
      fetchSyllabus();
      fetchStats();
    }
  }, [token, syllabusId]);

  const fetchSyllabus = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `http://localhost:7999/api/syllabi/syllabi/${syllabusId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!response.ok) throw new Error('Error al cargar temario');
      const data = await response.json();
      setSyllabus(data);

      // Inicializar temas expandidos
      const expanded = new Set<number>();
      const collectExpanded = (topics: Topic[]) => {
        topics.forEach(t => {
          if (t.is_expanded) expanded.add(t.id);
          if (t.children) collectExpanded(t.children);
        });
      };
      collectExpanded(data.topics);
      setExpandedTopics(expanded);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(
        `http://localhost:7999/api/syllabi/syllabi/${syllabusId}/stats`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch {
      // Stats are optional
    }
  };

  const toggleExpand = useCallback(async (topicId: number) => {
    setExpandedTopics(prev => {
      const next = new Set(prev);
      if (next.has(topicId)) {
        next.delete(topicId);
      } else {
        next.add(topicId);
      }
      return next;
    });

    // Persistir en servidor
    try {
      await fetch(`http://localhost:7999/api/syllabi/topics/${topicId}/toggle-expand`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch {
      // Ignore errors
    }
  }, [token]);

  const handleCreateTopic = async () => {
    if (!newTopic.title.trim()) return;

    try {
      const response = await fetch(
        `http://localhost:7999/api/syllabi/syllabi/${syllabusId}/topics`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            title: newTopic.title,
            code: newTopic.code || null,
            content: newTopic.content || null,
            parent_id: parentForNewTopic?.id || null,
            level: parentForNewTopic ? parentForNewTopic.level + 1 : 0,
            order_index: 0,
            content_status: newTopic.content ? 'complete' : 'empty',
            source_type: newTopic.content ? 'manual' : 'pending',
          }),
        }
      );

      if (!response.ok) throw new Error('Error al crear tema');

      setShowAddTopicModal(false);
      setNewTopic({ title: '', code: '', content: '' });
      setParentForNewTopic(null);
      fetchSyllabus();
      fetchStats();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error al crear tema');
    }
  };

  const handleUpdateTopic = async () => {
    if (!selectedTopic) return;

    try {
      const response = await fetch(
        `http://localhost:7999/api/syllabi/topics/${selectedTopic.id}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            title: selectedTopic.title,
            code: selectedTopic.code,
            content: selectedTopic.content,
            content_status: selectedTopic.content ? 'complete' : 'empty',
            source_type: 'manual',
          }),
        }
      );

      if (!response.ok) throw new Error('Error al guardar');

      setEditingTopic(false);
      fetchSyllabus();
      fetchStats();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error al guardar');
    }
  };

  const handleDeleteTopic = async (topicId: number) => {
    if (!confirm('¿Eliminar este tema y todos sus subtemas?')) return;

    try {
      const response = await fetch(
        `http://localhost:7999/api/syllabi/topics/${topicId}`,
        {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!response.ok) throw new Error('Error al eliminar');

      setSelectedTopic(null);
      fetchSyllabus();
      fetchStats();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error al eliminar');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'verified':
        return <span className="text-green-500" title="Verificado">✓</span>;
      case 'complete':
        return <span className="text-blue-500" title="Completo">●</span>;
      case 'partial':
        return <span className="text-yellow-500" title="Parcial">◐</span>;
      default:
        return <span className="text-gray-400" title="Pendiente">○</span>;
    }
  };

  const getSourceBadge = (source: string) => {
    const colors: Record<string, string> = {
      normativa: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
      manual: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      ai_generated: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
      pending: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    };
    const labels: Record<string, string> = {
      normativa: 'Normativa',
      manual: 'Manual',
      ai_generated: 'IA',
      pending: 'Pendiente',
    };
    return (
      <span className={`px-2 py-0.5 text-xs rounded-full ${colors[source]}`}>
        {labels[source]}
      </span>
    );
  };

  const renderTopicTree = (topics: Topic[], depth: number = 0) => {
    return topics.map((topic) => {
      const isExpanded = expandedTopics.has(topic.id);
      const hasChildren = topic.children && topic.children.length > 0;
      const isSelected = selectedTopic?.id === topic.id;

      return (
        <div key={topic.id} className="select-none">
          <div
            className={`
              flex items-center gap-2 py-2 px-3 rounded-lg cursor-pointer transition-colors
              ${isSelected ? 'bg-blue-100 dark:bg-blue-900/40' : 'hover:bg-gray-100 dark:hover:bg-gray-700/50'}
            `}
            style={{ paddingLeft: `${depth * 20 + 12}px` }}
            onClick={() => setSelectedTopic(topic)}
          >
            {/* Expand/Collapse Button */}
            {hasChildren ? (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleExpand(topic.id);
                }}
                className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
              >
                <svg
                  className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            ) : (
              <div className="w-6" />
            )}

            {/* Status Icon */}
            {getStatusIcon(topic.content_status)}

            {/* Code */}
            {topic.code && (
              <span className="text-xs font-mono text-gray-500 dark:text-gray-400">
                {topic.code}
              </span>
            )}

            {/* Title */}
            <span className="flex-1 text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
              {topic.title}
            </span>

            {/* Source Badge */}
            {topic.source_type !== 'pending' && getSourceBadge(topic.source_type)}

            {/* Add Child Button */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                setParentForNewTopic(topic);
                setShowAddTopicModal(true);
              }}
              className="p-1 opacity-0 group-hover:opacity-100 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
              title="Añadir subtema"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>

          {/* Children */}
          {hasChildren && isExpanded && (
            <div>{renderTopicTree(topic.children, depth + 1)}</div>
          )}
        </div>
      );
    });
  };

  if (authLoading || !token) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Cargando temario...</p>
        </div>
      </div>
    );
  }

  if (error || !syllabus) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400 mb-4">{error || 'Temario no encontrado'}</p>
          <button
            onClick={() => router.push('/syllabi')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg"
          >
            Volver a temarios
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.push('/syllabi')}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                {syllabus.name}
              </h1>
              {stats && (
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {stats.processed_topics}/{stats.total_topics} temas completados ({stats.progress_percentage}%)
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setParentForNewTopic(null);
                setShowAddTopicModal(true);
              }}
              className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Añadir Tema
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Tree Panel */}
        <div className="w-1/2 border-r border-gray-200 dark:border-gray-700 overflow-y-auto bg-white dark:bg-gray-800">
          <div className="p-4">
            {syllabus.topics.length === 0 ? (
              <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                <p className="mb-4">No hay temas. Añade el primero.</p>
                <button
                  onClick={() => setShowAddTopicModal(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Añadir Tema
                </button>
              </div>
            ) : (
              <div className="space-y-1 group">
                {renderTopicTree(syllabus.topics)}
              </div>
            )}
          </div>
        </div>

        {/* Content Panel */}
        <div className="w-1/2 overflow-y-auto bg-gray-50 dark:bg-gray-900">
          {selectedTopic ? (
            <div className="p-6">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                {editingTopic ? (
                  /* Edit Mode */
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Código
                      </label>
                      <input
                        type="text"
                        value={selectedTopic.code || ''}
                        onChange={(e) => setSelectedTopic({ ...selectedTopic, code: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm"
                        placeholder="Ej: Tema 1"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Título
                      </label>
                      <input
                        type="text"
                        value={selectedTopic.title}
                        onChange={(e) => setSelectedTopic({ ...selectedTopic, title: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Contenido (Markdown)
                      </label>
                      <textarea
                        value={selectedTopic.content || ''}
                        onChange={(e) => setSelectedTopic({ ...selectedTopic, content: e.target.value })}
                        rows={15}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm font-mono"
                      />
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          setEditingTopic(false);
                          fetchSyllabus();
                        }}
                        className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-sm"
                      >
                        Cancelar
                      </button>
                      <button
                        onClick={handleUpdateTopic}
                        className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                      >
                        Guardar
                      </button>
                    </div>
                  </div>
                ) : (
                  /* View Mode */
                  <>
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        {selectedTopic.code && (
                          <span className="text-sm text-gray-500 dark:text-gray-400 font-mono">
                            {selectedTopic.code}
                          </span>
                        )}
                        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                          {selectedTopic.title}
                        </h2>
                        <div className="flex items-center gap-2 mt-2">
                          {getStatusIcon(selectedTopic.content_status)}
                          <span className="text-sm text-gray-500 dark:text-gray-400">
                            {selectedTopic.content_status}
                          </span>
                          {getSourceBadge(selectedTopic.source_type)}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setEditingTopic(true)}
                          className="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg"
                          title="Editar"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDeleteTopic(selectedTopic.id)}
                          className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
                          title="Eliminar"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>

                    {selectedTopic.source_reference && (
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                        <strong>Fuente:</strong> {selectedTopic.source_reference}
                      </p>
                    )}

                    {selectedTopic.content ? (
                      <div className="prose prose-sm dark:prose-invert max-w-none">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {selectedTopic.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                        <p className="mb-4">Este tema no tiene contenido.</p>
                        <button
                          onClick={() => setEditingTopic(true)}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                        >
                          Añadir Contenido
                        </button>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
              <p>Selecciona un tema para ver su contenido</p>
            </div>
          )}
        </div>
      </div>

      {/* Add Topic Modal */}
      {showAddTopicModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-lg w-full">
            <div className="p-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                {parentForNewTopic ? `Añadir subtema a "${parentForNewTopic.title}"` : 'Añadir Tema'}
              </h2>

              <div className="space-y-4 mt-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Código (opcional)
                  </label>
                  <input
                    type="text"
                    value={newTopic.code}
                    onChange={(e) => setNewTopic({ ...newTopic, code: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm"
                    placeholder="Ej: Tema 1, 1.2.3"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Título *
                  </label>
                  <input
                    type="text"
                    value={newTopic.title}
                    onChange={(e) => setNewTopic({ ...newTopic, title: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm"
                    placeholder="Título del tema"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Contenido (opcional, Markdown)
                  </label>
                  <textarea
                    value={newTopic.content}
                    onChange={(e) => setNewTopic({ ...newTopic, content: e.target.value })}
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm font-mono"
                    placeholder="Contenido del tema..."
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => {
                    setShowAddTopicModal(false);
                    setNewTopic({ title: '', code: '', content: '' });
                    setParentForNewTopic(null);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleCreateTopic}
                  disabled={!newTopic.title.trim()}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  Crear
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
