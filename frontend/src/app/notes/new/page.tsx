'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';

export default function NewCollectionPage() {
  const router = useRouter();
  const { token, loading: authLoading } = useAuth();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    collection_type: 'custom' as 'temario' | 'normativa' | 'custom',
    is_public: false,
  });

  // Redirigir a login si no está autenticado
  useEffect(() => {
    if (!authLoading && !token) {
      router.push('/login');
    }
  }, [authLoading, token, router]);

  // Mostrar loading mientras se verifica la autenticación
  if (authLoading || !token) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      alert('El nombre es obligatorio');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch('http://localhost:7999/api/notes/collections', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error('Error al crear colección');

      const collection = await response.json();
      router.push(`/notes/${collection.id}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error al crear colección');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Nueva Colección de Apuntes
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Organiza tu contenido en temarios, normativa o colecciones personalizadas
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name */}
            <div>
              <label
                htmlFor="name"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
              >
                Nombre *
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                placeholder="Ej: Tema 1 - La Constitución Española"
              />
            </div>

            {/* Description */}
            <div>
              <label
                htmlFor="description"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
              >
                Descripción
              </label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
                placeholder="Describe el contenido de esta colección..."
              />
            </div>

            {/* Collection Type */}
            <div>
              <label
                htmlFor="collection_type"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Tipo de Colección
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <label
                  className={`
                    flex flex-col items-center p-4 border-2 rounded-lg cursor-pointer transition-all
                    ${
                      formData.collection_type === 'temario'
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-300 dark:border-gray-600 hover:border-blue-300'
                    }
                  `}
                >
                  <input
                    type="radio"
                    name="collection_type"
                    value="temario"
                    checked={formData.collection_type === 'temario'}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        collection_type: e.target.value as 'temario',
                      })
                    }
                    className="sr-only"
                  />
                  <span className="text-3xl mb-2">📚</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">Temario</span>
                  <span className="text-xs text-gray-600 dark:text-gray-400 text-center mt-1">
                    Para organizar el temario de oposición
                  </span>
                </label>

                <label
                  className={`
                    flex flex-col items-center p-4 border-2 rounded-lg cursor-pointer transition-all
                    ${
                      formData.collection_type === 'normativa'
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-300 dark:border-gray-600 hover:border-blue-300'
                    }
                  `}
                >
                  <input
                    type="radio"
                    name="collection_type"
                    value="normativa"
                    checked={formData.collection_type === 'normativa'}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        collection_type: e.target.value as 'normativa',
                      })
                    }
                    className="sr-only"
                  />
                  <span className="text-3xl mb-2">⚖️</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">Normativa</span>
                  <span className="text-xs text-gray-600 dark:text-gray-400 text-center mt-1">
                    Para leyes y normativa completa
                  </span>
                </label>

                <label
                  className={`
                    flex flex-col items-center p-4 border-2 rounded-lg cursor-pointer transition-all
                    ${
                      formData.collection_type === 'custom'
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-300 dark:border-gray-600 hover:border-blue-300'
                    }
                  `}
                >
                  <input
                    type="radio"
                    name="collection_type"
                    value="custom"
                    checked={formData.collection_type === 'custom'}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        collection_type: e.target.value as 'custom',
                      })
                    }
                    className="sr-only"
                  />
                  <span className="text-3xl mb-2">📝</span>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    Personalizado
                  </span>
                  <span className="text-xs text-gray-600 dark:text-gray-400 text-center mt-1">
                    Para cualquier otro contenido
                  </span>
                </label>
              </div>
            </div>

            {/* Public Toggle */}
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="is_public"
                checked={formData.is_public}
                onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
              <label htmlFor="is_public" className="text-sm text-gray-700 dark:text-gray-300">
                Hacer pública esta colección
                <span className="block text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Otros usuarios podrán ver y clonar tu colección
                </span>
              </label>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={() => router.back()}
                disabled={loading}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Creando...
                  </>
                ) : (
                  'Crear Colección'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
