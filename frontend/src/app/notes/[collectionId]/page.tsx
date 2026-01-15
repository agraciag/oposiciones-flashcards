'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import NotesTree, { NoteTreeNode } from '@/components/NotesTree';
import NotesTreeDraggable from '@/components/NotesTreeDraggable';
import NoteViewer, { Note } from '@/components/NoteViewer';
import NoteEditor, { NoteFormData } from '@/components/NoteEditor';
import NoteSearch from '@/components/NoteSearch';

interface Collection {
  id: number;
  user_id: number;
  name: string;
  description: string | null;
  collection_type: 'temario' | 'normativa' | 'custom';
  is_public: boolean;
  created_at: string;
  updated_at: string | null;
}

type ViewMode = 'view' | 'edit' | 'new';

export default function CollectionPage() {
  const params = useParams();
  const router = useRouter();
  const { token } = useAuth();
  const collectionId = params.collectionId as string;

  const [collection, setCollection] = useState<Collection | null>(null);
  const [tree, setTree] = useState<NoteTreeNode[]>([]);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [selectedNoteId, setSelectedNoteId] = useState<number | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('view');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [dragMode, setDragMode] = useState(false);

  useEffect(() => {
    if (collectionId && token) {
      fetchCollection();
      fetchTree();
    }
  }, [collectionId, token]);

  useEffect(() => {
    if (selectedNoteId && token) {
      fetchNote(selectedNoteId);
    }
  }, [selectedNoteId, token]);

  const fetchCollection = async () => {
    try {
      const response = await fetch(
        `http://localhost:7999/api/notes/collections/${collectionId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (!response.ok) throw new Error('Error al cargar colección');
      const data = await response.json();
      setCollection(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    }
  };

  const fetchTree = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `http://localhost:7999/api/notes/collections/${collectionId}/tree`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (!response.ok) throw new Error('Error al cargar árbol');
      const data = await response.json();
      setTree(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const fetchNote = async (noteId: number) => {
    try {
      const response = await fetch(`http://localhost:7999/api/notes/notes/${noteId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Error al cargar nota');
      const data = await response.json();
      setSelectedNote(data);
      setViewMode('view');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar nota');
    }
  };

  const handleSelectNote = (noteId: number) => {
    setSelectedNoteId(noteId);
  };

  const handleCreateNote = async (data: NoteFormData) => {
    try {
      // Crear la nota
      const noteResponse = await fetch('http://localhost:7999/api/notes/notes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      if (!noteResponse.ok) throw new Error('Error al crear nota');
      const newNote = await noteResponse.json();

      // Añadirla a la colección (crear jerarquía)
      const hierarchyResponse = await fetch('http://localhost:7999/api/notes/hierarchies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          collection_id: parseInt(collectionId),
          note_id: newNote.id,
          parent_id: null, // Por ahora siempre en la raíz
          order_index: tree.length,
          is_featured: false,
        }),
      });

      if (!hierarchyResponse.ok) throw new Error('Error al añadir nota a colección');

      // Recargar árbol y seleccionar la nueva nota
      await fetchTree();
      setSelectedNoteId(newNote.id);
      setViewMode('view');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error al crear nota');
    }
  };

  const handleUpdateNote = async (data: NoteFormData) => {
    if (!selectedNote) return;

    try {
      const response = await fetch(
        `http://localhost:7999/api/notes/notes/${selectedNote.id}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(data),
        }
      );

      if (!response.ok) throw new Error('Error al actualizar nota');

      // Recargar nota y árbol
      await fetchNote(selectedNote.id);
      await fetchTree();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error al actualizar nota');
    }
  };

  const handleDeleteNote = async (noteId: number) => {
    try {
      const response = await fetch(`http://localhost:7999/api/notes/notes/${noteId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) throw new Error('Error al eliminar nota');

      // Recargar árbol y limpiar selección
      await fetchTree();
      setSelectedNote(null);
      setSelectedNoteId(null);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error al eliminar nota');
    }
  };

  const handleExport = () => {
    // Abrir en nueva pestaña para descargar
    window.open(
      `http://localhost:7999/api/notes/collections/${collectionId}/export`,
      '_blank'
    );
  };

  const handleReorder = async (hierarchyId: number, newOrderIndex: number) => {
    try {
      const response = await fetch(
        `http://localhost:7999/api/notes/hierarchies/${hierarchyId}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ order_index: newOrderIndex }),
        }
      );

      if (!response.ok) throw new Error('Error al reordenar');

      // Recargar árbol
      await fetchTree();
    } catch (err) {
      console.error('Error reordering:', err);
    }
  };

  const handleGenerateFlashcards = async (noteId: number) => {
    const deckId = prompt('Introduce el ID del mazo donde guardar las flashcards:');
    if (!deckId) return;

    try {
      const response = await fetch(
        `http://localhost:7999/api/notes/notes/${noteId}/generate-flashcards?deck_id=${deckId}&max_cards=5`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) throw new Error('Error al generar flashcards');

      const result = await response.json();

      if (confirm(`Se generaron ${result.preview.length} flashcards. ¿Guardar?`)) {
        const confirmResponse = await fetch(
          `http://localhost:7999/api/notes/notes/${noteId}/generate-flashcards/confirm`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              flashcards: result.preview,
              deck_id: parseInt(deckId),
            }),
          }
        );

        if (confirmResponse.ok) {
          alert('✓ Flashcards guardadas exitosamente');
        }
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error al generar flashcards');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Cargando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/notes')}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </button>
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                {collection?.name}
              </h1>
              {collection?.description && (
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {collection.description}
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors lg:hidden"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
            <button
              onClick={() => setDragMode(!dragMode)}
              className={`px-4 py-2 rounded-lg transition-colors flex items-center gap-2 ${
                dragMode
                  ? 'bg-purple-600 text-white hover:bg-purple-700'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
              title="Modo reorganizar"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 8h16M4 16h16"
                />
              </svg>
              {dragMode ? 'Modo Normal' : 'Reorganizar'}
            </button>
            <button
              onClick={handleExport}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
              title="Exportar a Markdown"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              Exportar
            </button>
            <button
              onClick={() => {
                setSelectedNote(null);
                setSelectedNoteId(null);
                setViewMode('new');
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              Nueva Nota
            </button>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 px-6 py-3">
          {error}
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - Tree */}
        <div
          className={`
            ${showSidebar ? 'w-80' : 'w-0'}
            bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700
            transition-all duration-300 overflow-hidden
          `}
        >
          <div className="h-full flex flex-col">
            {/* Search */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <NoteSearch onSelectNote={handleSelectNote} />
            </div>

            {/* Tree */}
            <div className="flex-1 overflow-y-auto p-4">
              {dragMode ? (
                <NotesTreeDraggable
                  tree={tree}
                  onSelectNote={handleSelectNote}
                  selectedNoteId={selectedNoteId}
                  onReorder={handleReorder}
                />
              ) : (
                <NotesTree
                  tree={tree}
                  onSelectNote={handleSelectNote}
                  selectedNoteId={selectedNoteId}
                />
              )}
            </div>
          </div>
        </div>

        {/* Main Panel */}
        <div className="flex-1 overflow-hidden bg-gray-50 dark:bg-gray-900">
          <div className="h-full overflow-y-auto p-6">
            <div className="max-w-4xl mx-auto">
              {viewMode === 'view' && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 h-full">
                  <NoteViewer
                    note={selectedNote}
                    onEdit={(note) => setViewMode('edit')}
                    onDelete={handleDeleteNote}
                    onGenerateFlashcards={handleGenerateFlashcards}
                  />
                </div>
              )}

              {viewMode === 'edit' && selectedNote && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                  <NoteEditor
                    initialData={{
                      title: selectedNote.title,
                      content: selectedNote.content || '',
                      note_type: selectedNote.note_type,
                      tags: selectedNote.tags || '',
                      legal_reference: selectedNote.legal_reference || '',
                      article_number: selectedNote.article_number || '',
                    }}
                    onSave={handleUpdateNote}
                    onCancel={() => setViewMode('view')}
                  />
                </div>
              )}

              {viewMode === 'new' && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                  <NoteEditor
                    onSave={handleCreateNote}
                    onCancel={() => {
                      setViewMode('view');
                      if (selectedNoteId) {
                        fetchNote(selectedNoteId);
                      }
                    }}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
