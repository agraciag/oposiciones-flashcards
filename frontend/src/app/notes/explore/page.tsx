'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';

interface NoteCollection {
  id: number;
  user_id: number;
  name: string;
  description: string | null;
  collection_type: 'temario' | 'normativa' | 'custom';
  is_public: boolean;
  created_at: string;
  updated_at: string | null;
}

export default function ExploreNotesPage() {
  const router = useRouter();
  const { token } = useAuth();
  const [collections, setCollections] = useState<NoteCollection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('all');

  useEffect(() => {
    fetchPublicCollections();
  }, [token]);

  const fetchPublicCollections = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:7999/api/notes/collections/public', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Error al cargar colecciones públicas');

      const data = await response.json();
      setCollections(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const cloneCollection = async (id: number) => {
    if (!confirm('¿Clonar esta colección a tu biblioteca?')) return;

    try {
      const response = await fetch(`http://localhost:7999/api/notes/collections/${id}/clone`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Error al clonar colección');

      const newCollection = await response.json();
      alert(`✓ Colección clonada: ${newCollection.name}`);
      router.push(`/notes/${newCollection.id}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error al clonar');
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'temario':
        return '📚';
      case 'normativa':
        return '⚖️';
      default:
        return '📝';
    }
  };

  const getTypeName = (type: string) => {
    switch (type) {
      case 'temario':
        return 'Temario';
      case 'normativa':
        return 'Normativa';
      default:
        return 'Personalizado';
    }
  };

  const filteredCollections = collections.filter((c) =>
    filterType === 'all' ? true : c.collection_type === filterType
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Cargando colecciones públicas...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <button
                onClick={() => router.push('/notes')}
                className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors"
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
              <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
                Explorar Colecciones Públicas
              </h1>
            </div>
            <p className="text-gray-600 dark:text-gray-400 ml-14">
              Descubre y clona colecciones compartidas por la comunidad
            </p>
          </div>
        </div>

        {/* Filter */}
        <div className="mb-6 flex gap-2">
          <button
            onClick={() => setFilterType('all')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filterType === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            Todas
          </button>
          <button
            onClick={() => setFilterType('temario')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filterType === 'temario'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            Temario
          </button>
          <button
            onClick={() => setFilterType('normativa')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filterType === 'normativa'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            Normativa
          </button>
          <button
            onClick={() => setFilterType('custom')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filterType === 'custom'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            Personalizado
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Collections Grid */}
        {filteredCollections.length === 0 ? (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
              No hay colecciones públicas
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              {filterType === 'all'
                ? 'Aún no hay colecciones compartidas por la comunidad'
                : `No hay colecciones públicas de tipo ${getTypeName(filterType)}`}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCollections.map((collection) => (
              <div
                key={collection.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{getTypeIcon(collection.collection_type)}</span>
                    <div>
                      <h3 className="font-semibold text-lg text-gray-900 dark:text-gray-100">
                        {collection.name}
                      </h3>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {getTypeName(collection.collection_type)}
                      </span>
                    </div>
                  </div>

                  <span className="text-xs bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 px-2 py-1 rounded-full">
                    Público
                  </span>
                </div>

                {collection.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-3">
                    {collection.description}
                  </p>
                )}

                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => router.push(`/notes/${collection.id}`)}
                    className="flex-1 px-3 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 text-sm rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                  >
                    Vista Previa
                  </button>
                  <button
                    onClick={() => cloneCollection(collection.id)}
                    className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                      />
                    </svg>
                    Clonar
                  </button>
                </div>

                <div className="text-xs text-gray-500 dark:text-gray-400 mt-4">
                  Creada: {new Date(collection.created_at).toLocaleDateString('es-ES')}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
