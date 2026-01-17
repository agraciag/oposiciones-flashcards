'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Panel, Group as PanelGroup, Separator as PanelResizeHandle } from 'react-resizable-panels';

interface Annotation {
  id: number;
  document_id: number;
  start_pos: number;
  end_pos: number;
  selected_text: string;
  annotation_title: string | null;
  linked_content: string;
  legal_reference: string | null;
  article_number: string | null;
}

interface StudyDocument {
  id: number;
  title: string;
  content: string;
  description: string | null;
  is_public: boolean;
  annotations: Annotation[];
}

interface Selection {
  text: string;
  start: number;
  end: number;
  rect: DOMRect | null;
}

type ViewMode = 'study' | 'reading' | 'immersive';

interface UserPreferences {
  fontSize: number;
  lineHeight: number;
  panelSize: number;
  viewMode: ViewMode;
}

const DEFAULT_PREFERENCES: UserPreferences = {
  fontSize: 16,
  lineHeight: 1.8,
  panelSize: 35,
  viewMode: 'study',
};

const FONT_SIZES = [14, 16, 18, 20, 22, 24];
const LINE_HEIGHTS = [1.5, 1.6, 1.8, 2.0, 2.2];

export default function StudyDocViewerPage() {
  const params = useParams();
  const router = useRouter();
  const { token, loading: authLoading } = useAuth();
  const documentId = params.id as string;

  const [document, setDocument] = useState<StudyDocument | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // User preferences (persisted)
  const [preferences, setPreferences] = useState<UserPreferences>(DEFAULT_PREFERENCES);
  const [showSettings, setShowSettings] = useState(false);

  // Selection state
  const [selection, setSelection] = useState<Selection | null>(null);
  const [showAnnotationForm, setShowAnnotationForm] = useState(false);
  const [newAnnotation, setNewAnnotation] = useState({
    title: '',
    content: '',
    article_number: '',
    legal_reference: '',
  });

  // Panel state
  const [selectedAnnotation, setSelectedAnnotation] = useState<Annotation | null>(null);

  // Edit annotation state
  const [editingAnnotation, setEditingAnnotation] = useState(false);
  const [editAnnotationData, setEditAnnotationData] = useState({
    annotation_title: '',
    linked_content: '',
    article_number: '',
    legal_reference: '',
  });

  const contentRef = useRef<HTMLDivElement>(null);

  // Load preferences from localStorage
  useEffect(() => {
    const saved = localStorage.getItem(`study-doc-preferences-${documentId}`);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setPreferences({ ...DEFAULT_PREFERENCES, ...parsed });
      } catch {
        // Ignore invalid JSON
      }
    }
  }, [documentId]);

  // Save preferences to localStorage
  const updatePreferences = useCallback((updates: Partial<UserPreferences>) => {
    setPreferences(prev => {
      const newPrefs = { ...prev, ...updates };
      localStorage.setItem(`study-doc-preferences-${documentId}`, JSON.stringify(newPrefs));
      return newPrefs;
    });
  }, [documentId]);

  useEffect(() => {
    if (!authLoading && !token) {
      router.push('/login');
    }
  }, [authLoading, token, router]);

  useEffect(() => {
    if (token && documentId) {
      fetchDocument();
    }
  }, [token, documentId]);

  const fetchDocument = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `http://localhost:7999/api/study-docs/documents/${documentId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!response.ok) throw new Error('Error al cargar documento');
      const data = await response.json();
      setDocument(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  // Handle text selection
  const handleMouseUp = useCallback(() => {
    if (preferences.viewMode === 'reading' || preferences.viewMode === 'immersive') {
      return; // No selection in reading modes
    }

    const sel = window.getSelection();
    if (!sel || sel.isCollapsed || !contentRef.current) {
      return;
    }

    const text = sel.toString().trim();
    if (!text || text.length < 2) {
      return;
    }

    const range = sel.getRangeAt(0);
    const preSelectionRange = range.cloneRange();
    preSelectionRange.selectNodeContents(contentRef.current);
    preSelectionRange.setEnd(range.startContainer, range.startOffset);
    const start = preSelectionRange.toString().length;
    const end = start + text.length;

    const rect = range.getBoundingClientRect();
    setSelection({ text, start, end, rect });
  }, [preferences.viewMode]);

  // Create annotation
  const handleCreateAnnotation = async () => {
    if (!selection || !document) return;

    try {
      const response = await fetch(
        `http://localhost:7999/api/study-docs/documents/${documentId}/annotations`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            start_pos: selection.start,
            end_pos: selection.end,
            selected_text: selection.text,
            annotation_title: newAnnotation.title || null,
            linked_content: newAnnotation.content,
            legal_reference: newAnnotation.legal_reference || null,
            article_number: newAnnotation.article_number || null,
          }),
        }
      );

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Error al crear anotación');
      }

      await fetchDocument();
      setShowAnnotationForm(false);
      setSelection(null);
      setNewAnnotation({ title: '', content: '', article_number: '', legal_reference: '' });
      window.getSelection()?.removeAllRanges();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error al crear anotación');
    }
  };

  // Start editing annotation
  const startEditingAnnotation = (ann: Annotation) => {
    setEditAnnotationData({
      annotation_title: ann.annotation_title || '',
      linked_content: ann.linked_content,
      article_number: ann.article_number || '',
      legal_reference: ann.legal_reference || '',
    });
    setEditingAnnotation(true);
  };

  // Save edited annotation
  const handleSaveAnnotation = async () => {
    if (!selectedAnnotation) return;

    try {
      const response = await fetch(
        `http://localhost:7999/api/study-docs/annotations/${selectedAnnotation.id}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            annotation_title: editAnnotationData.annotation_title || null,
            linked_content: editAnnotationData.linked_content,
            legal_reference: editAnnotationData.legal_reference || null,
            article_number: editAnnotationData.article_number || null,
          }),
        }
      );

      if (!response.ok) throw new Error('Error al guardar');

      await fetchDocument();
      setEditingAnnotation(false);
      const updated = await response.json();
      setSelectedAnnotation(updated);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error al guardar');
    }
  };

  // Delete annotation
  const handleDeleteAnnotation = async (annotationId: number) => {
    if (!confirm('¿Eliminar esta anotación?')) return;

    try {
      const response = await fetch(
        `http://localhost:7999/api/study-docs/annotations/${annotationId}`,
        {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!response.ok) throw new Error('Error al eliminar');

      await fetchDocument();
      setSelectedAnnotation(null);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error al eliminar');
    }
  };

  // Render content with highlighted annotations
  const renderContent = () => {
    if (!document) return null;

    const { content, annotations } = document;
    const sortedAnnotations = [...annotations].sort((a, b) => a.start_pos - b.start_pos);

    const elements: React.ReactNode[] = [];
    let lastIndex = 0;

    sortedAnnotations.forEach((ann, i) => {
      if (ann.start_pos > lastIndex) {
        elements.push(
          <span key={`text-${i}`}>{content.slice(lastIndex, ann.start_pos)}</span>
        );
      }

      elements.push(
        <button
          key={`ann-${ann.id}`}
          onClick={() => {
            if (preferences.viewMode === 'study') {
              setSelectedAnnotation(ann);
            }
          }}
          className={`
            inline text-blue-600 dark:text-blue-400 border-b-2 border-dotted border-blue-400
            hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors
            ${preferences.viewMode === 'study' ? 'cursor-pointer' : 'cursor-default'}
            ${selectedAnnotation?.id === ann.id ? 'bg-blue-100 dark:bg-blue-900/50' : ''}
          `}
          title={ann.annotation_title || ann.selected_text}
        >
          {ann.selected_text}
        </button>
      );

      lastIndex = ann.end_pos;
    });

    if (lastIndex < content.length) {
      elements.push(<span key="text-end">{content.slice(lastIndex)}</span>);
    }

    return elements;
  };

  // Export functions
  const handleExportHTML = () => {
    window.open(
      `http://localhost:7999/api/study-docs/documents/${documentId}/export/html`,
      '_blank'
    );
  };

  const handleExportPDF = () => {
    window.open(
      `http://localhost:7999/api/study-docs/documents/${documentId}/export/pdf`,
      '_blank'
    );
  };

  // Toggle fullscreen for immersive mode
  const toggleImmersive = () => {
    if (preferences.viewMode === 'immersive') {
      updatePreferences({ viewMode: 'study' });
      if (window.document.fullscreenElement) {
        window.document.exitFullscreen();
      }
    } else {
      updatePreferences({ viewMode: 'immersive' });
      window.document.documentElement.requestFullscreen?.();
    }
  };

  // Exit fullscreen handler
  useEffect(() => {
    const handleFullscreenChange = () => {
      if (!window.document.fullscreenElement && preferences.viewMode === 'immersive') {
        updatePreferences({ viewMode: 'study' });
      }
    };
    window.document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => window.document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, [preferences.viewMode, updatePreferences]);

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
          <p className="text-gray-600 dark:text-gray-400">Cargando documento...</p>
        </div>
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400 mb-4">{error || 'Documento no encontrado'}</p>
          <button
            onClick={() => router.push('/study-docs')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg"
          >
            Volver a documentos
          </button>
        </div>
      </div>
    );
  }

  const showPanel = preferences.viewMode === 'study';
  const isImmersive = preferences.viewMode === 'immersive';

  return (
    <div className={`h-screen flex flex-col ${isImmersive ? 'bg-gray-900' : 'bg-gray-50 dark:bg-gray-900'}`}>
      {/* Header - hidden in immersive mode */}
      {!isImmersive && (
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => router.push('/study-docs')}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                title="Volver"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <div>
                <h1 className="text-lg font-bold text-gray-900 dark:text-gray-100 line-clamp-1">
                  {document.title}
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {document.annotations.length} anotaciones
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              {/* View Mode Buttons */}
              <div className="flex items-center bg-gray-100 dark:bg-gray-700 rounded-lg p-1 mr-2">
                <button
                  onClick={() => updatePreferences({ viewMode: 'study' })}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    preferences.viewMode === 'study'
                      ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                  }`}
                  title="Modo Estudio: Panel lateral visible, crear anotaciones"
                >
                  Estudio
                </button>
                <button
                  onClick={() => updatePreferences({ viewMode: 'reading' })}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    preferences.viewMode === 'reading'
                      ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                  }`}
                  title="Modo Lectura: Sin panel, documento maximizado"
                >
                  Lectura
                </button>
                <button
                  onClick={toggleImmersive}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    preferences.viewMode === 'immersive'
                      ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-400 shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                  }`}
                  title="Modo Inmersivo: Pantalla completa"
                >
                  Inmersivo
                </button>
              </div>

              {/* Settings Button */}
              <button
                onClick={() => setShowSettings(!showSettings)}
                className={`p-2 rounded-lg transition-colors ${
                  showSettings
                    ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
                title="Configuración de lectura"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>

              {/* Edit Button */}
              <button
                onClick={() => router.push(`/study-docs/${documentId}/edit`)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                title="Editar documento"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>

              {/* Export Buttons */}
              <button
                onClick={handleExportHTML}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-green-600"
                title="Exportar HTML"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </button>
              <button
                onClick={handleExportPDF}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-red-600"
                title="Exportar PDF"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </button>
            </div>
          </div>

          {/* Settings Panel */}
          {showSettings && (
            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
              <div className="flex flex-wrap items-center gap-6">
                {/* Font Size */}
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Tamaño:</span>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => {
                        const idx = FONT_SIZES.indexOf(preferences.fontSize);
                        if (idx > 0) updatePreferences({ fontSize: FONT_SIZES[idx - 1] });
                      }}
                      className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                      disabled={preferences.fontSize === FONT_SIZES[0]}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                      </svg>
                    </button>
                    <span className="text-sm font-medium w-8 text-center">{preferences.fontSize}</span>
                    <button
                      onClick={() => {
                        const idx = FONT_SIZES.indexOf(preferences.fontSize);
                        if (idx < FONT_SIZES.length - 1) updatePreferences({ fontSize: FONT_SIZES[idx + 1] });
                      }}
                      className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded"
                      disabled={preferences.fontSize === FONT_SIZES[FONT_SIZES.length - 1]}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Line Height */}
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Interlineado:</span>
                  <select
                    value={preferences.lineHeight}
                    onChange={(e) => updatePreferences({ lineHeight: parseFloat(e.target.value) })}
                    className="text-sm border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-gray-700"
                  >
                    {LINE_HEIGHTS.map(lh => (
                      <option key={lh} value={lh}>{lh}</option>
                    ))}
                  </select>
                </div>

                {/* Reset */}
                <button
                  onClick={() => updatePreferences(DEFAULT_PREFERENCES)}
                  className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
                >
                  Restablecer
                </button>
              </div>
            </div>
          )}
        </header>
      )}

      {/* Immersive mode exit button */}
      {isImmersive && (
        <button
          onClick={toggleImmersive}
          className="fixed top-4 right-4 z-50 p-2 bg-gray-800/80 hover:bg-gray-700 text-white rounded-lg"
          title="Salir de modo inmersivo (Esc)"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}

      {/* Main content */}
      <div className="flex-1 overflow-hidden">
        {showPanel ? (
          <PanelGroup
            orientation="horizontal"
            onLayoutChange={(layout: Record<string, number>) => {
              const sideSize = Object.values(layout)[1];
              if (sideSize && sideSize !== preferences.panelSize) {
                updatePreferences({ panelSize: sideSize });
              }
            }}
          >
            {/* Document Panel */}
            <Panel id="main" defaultSize={100 - preferences.panelSize} minSize={40}>
              <main className="h-full overflow-y-auto p-6">
                <div className={`mx-auto ${isImmersive ? 'max-w-3xl' : 'max-w-4xl'}`}>
                  <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 ${isImmersive ? 'bg-gray-800' : ''}`}>
                    {/* Instructions - only in study mode */}
                    {preferences.viewMode === 'study' && (
                      <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-sm text-blue-800 dark:text-blue-200">
                        <strong>Modo Estudio:</strong> Selecciona texto para crear anotaciones.
                        Las palabras subrayadas tienen contenido vinculado.
                      </div>
                    )}

                    {/* Content */}
                    <div
                      ref={contentRef}
                      onMouseUp={handleMouseUp}
                      className="prose prose-sm md:prose-base dark:prose-invert max-w-none whitespace-pre-wrap select-text"
                      style={{
                        fontSize: `${preferences.fontSize}px`,
                        lineHeight: preferences.lineHeight,
                        fontFamily: 'Georgia, "Times New Roman", serif',
                        userSelect: 'text',
                      }}
                    >
                      {renderContent()}
                    </div>
                  </div>
                </div>
              </main>
            </Panel>

            {/* Resize Handle */}
            <PanelResizeHandle className="w-2 bg-gray-200 dark:bg-gray-700 hover:bg-blue-400 dark:hover:bg-blue-500 transition-colors cursor-col-resize flex items-center justify-center">
              <div className="w-1 h-8 bg-gray-400 dark:bg-gray-500 rounded-full" />
            </PanelResizeHandle>

            {/* Side Panel */}
            <Panel id="side" defaultSize={preferences.panelSize} minSize={20} maxSize={50}>
              <aside className="h-full bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 overflow-y-auto">
                {selectedAnnotation ? (
                  /* Annotation viewer/editor */
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 line-clamp-2">
                        {editingAnnotation ? 'Editar Anotación' : (selectedAnnotation.annotation_title || selectedAnnotation.selected_text)}
                      </h2>
                      <button
                        onClick={() => {
                          setSelectedAnnotation(null);
                          setEditingAnnotation(false);
                        }}
                        className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded flex-shrink-0"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>

                    {editingAnnotation ? (
                      /* Edit form */
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Título
                          </label>
                          <input
                            type="text"
                            value={editAnnotationData.annotation_title}
                            onChange={(e) => setEditAnnotationData({ ...editAnnotationData, annotation_title: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Artículo
                          </label>
                          <input
                            type="text"
                            value={editAnnotationData.article_number}
                            onChange={(e) => setEditAnnotationData({ ...editAnnotationData, article_number: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Referencia legal
                          </label>
                          <input
                            type="text"
                            value={editAnnotationData.legal_reference}
                            onChange={(e) => setEditAnnotationData({ ...editAnnotationData, legal_reference: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Contenido *
                          </label>
                          <textarea
                            value={editAnnotationData.linked_content}
                            onChange={(e) => setEditAnnotationData({ ...editAnnotationData, linked_content: e.target.value })}
                            rows={12}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm font-mono"
                          />
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => setEditingAnnotation(false)}
                            className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-sm"
                          >
                            Cancelar
                          </button>
                          <button
                            onClick={handleSaveAnnotation}
                            className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                          >
                            Guardar
                          </button>
                        </div>
                      </div>
                    ) : (
                      /* View mode */
                      <>
                        {selectedAnnotation.article_number && (
                          <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                            <strong>Artículo:</strong> {selectedAnnotation.article_number}
                          </p>
                        )}
                        {selectedAnnotation.legal_reference && (
                          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                            <strong>Referencia:</strong> {selectedAnnotation.legal_reference}
                          </p>
                        )}

                        <div
                          className="prose prose-sm dark:prose-invert max-w-none"
                          style={{ fontSize: `${Math.max(14, preferences.fontSize - 2)}px` }}
                        >
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {selectedAnnotation.linked_content}
                          </ReactMarkdown>
                        </div>

                        <div className="flex gap-2 mt-6">
                          <button
                            onClick={() => startEditingAnnotation(selectedAnnotation)}
                            className="flex-1 px-4 py-2 text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors text-sm"
                          >
                            Editar
                          </button>
                          <button
                            onClick={() => handleDeleteAnnotation(selectedAnnotation.id)}
                            className="flex-1 px-4 py-2 text-red-600 border border-red-300 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors text-sm"
                          >
                            Eliminar
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                ) : (
                  /* Annotations list */
                  <div className="p-6">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                      Tabla de Contenidos
                    </h2>
                    {document.annotations.length === 0 ? (
                      <p className="text-gray-500 dark:text-gray-400 text-sm">
                        No hay anotaciones. Selecciona texto para crear una.
                      </p>
                    ) : (
                      <ul className="space-y-2">
                        {document.annotations
                          .sort((a, b) => a.start_pos - b.start_pos)
                          .map((ann) => (
                            <li key={ann.id}>
                              <button
                                onClick={() => setSelectedAnnotation(ann)}
                                className="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                              >
                                <span className="text-blue-600 dark:text-blue-400 font-medium text-sm">
                                  {ann.annotation_title || ann.selected_text}
                                </span>
                                {ann.article_number && (
                                  <span className="block text-xs text-gray-500 dark:text-gray-400">
                                    {ann.article_number}
                                  </span>
                                )}
                              </button>
                            </li>
                          ))}
                      </ul>
                    )}
                  </div>
                )}
              </aside>
            </Panel>
          </PanelGroup>
        ) : (
          /* Reading / Immersive mode - no panel */
          <main className="h-full overflow-y-auto p-6">
            <div className={`mx-auto ${isImmersive ? 'max-w-2xl' : 'max-w-3xl'}`}>
              <div className={`rounded-lg p-8 ${isImmersive ? 'bg-gray-800 text-gray-100' : 'bg-white dark:bg-gray-800 shadow-md'}`}>
                {/* Reading mode header */}
                {preferences.viewMode === 'reading' && (
                  <div className="mb-6 text-center">
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                      {document.title}
                    </h1>
                    {document.description && (
                      <p className="text-gray-600 dark:text-gray-400">{document.description}</p>
                    )}
                  </div>
                )}

                {/* Content */}
                <div
                  ref={contentRef}
                  className="prose prose-sm md:prose-base dark:prose-invert max-w-none whitespace-pre-wrap"
                  style={{
                    fontSize: `${preferences.fontSize}px`,
                    lineHeight: preferences.lineHeight,
                    fontFamily: 'Georgia, "Times New Roman", serif',
                  }}
                >
                  {renderContent()}
                </div>
              </div>
            </div>
          </main>
        )}
      </div>

      {/* Floating button for selection */}
      {selection && !showAnnotationForm && preferences.viewMode === 'study' && (
        <div
          className="fixed z-50"
          style={{
            top: selection.rect ? selection.rect.bottom + 10 : 100,
            left: selection.rect ? selection.rect.left : 100,
          }}
        >
          <button
            onClick={() => setShowAnnotationForm(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg shadow-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            Vincular "{selection.text.slice(0, 20)}{selection.text.length > 20 ? '...' : ''}"
          </button>
          <button
            onClick={() => {
              setSelection(null);
              window.getSelection()?.removeAllRanges();
            }}
            className="ml-2 p-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Annotation form modal */}
      {showAnnotationForm && selection && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                Crear Anotación
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                Texto seleccionado: <span className="font-medium text-blue-600">"{selection.text}"</span>
              </p>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Título (opcional)
                  </label>
                  <input
                    type="text"
                    value={newAnnotation.title}
                    onChange={(e) => setNewAnnotation({ ...newAnnotation, title: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                    placeholder="Ej: Artículo 1 - Objeto de la LOE"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Número de artículo (opcional)
                    </label>
                    <input
                      type="text"
                      value={newAnnotation.article_number}
                      onChange={(e) => setNewAnnotation({ ...newAnnotation, article_number: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      placeholder="Ej: Art. 1 LOE"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Referencia legal (opcional)
                    </label>
                    <input
                      type="text"
                      value={newAnnotation.legal_reference}
                      onChange={(e) => setNewAnnotation({ ...newAnnotation, legal_reference: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                      placeholder="Ej: BOE-A-1999-21567"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Contenido vinculado *
                  </label>
                  <textarea
                    value={newAnnotation.content}
                    onChange={(e) => setNewAnnotation({ ...newAnnotation, content: e.target.value })}
                    rows={10}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 font-mono text-sm"
                    placeholder="Pega aquí el contenido del artículo, ley o cualquier material de estudio...

Soporta Markdown:
- **negrita**
- *cursiva*
- Listas
- Tablas"
                    required
                  />
                  <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    Soporta formato Markdown
                  </p>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => {
                    setShowAnnotationForm(false);
                    setSelection(null);
                    setNewAnnotation({ title: '', content: '', article_number: '', legal_reference: '' });
                    window.getSelection()?.removeAllRanges();
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleCreateAnnotation}
                  disabled={!newAnnotation.content.trim()}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  Crear Anotación
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
