'use client';

import { useState, useEffect } from 'react';

export interface NoteFormData {
  title: string;
  content: string;
  note_type: 'section' | 'content';
  tags: string;
  legal_reference: string;
  article_number: string;
}

interface NoteEditorProps {
  initialData?: Partial<NoteFormData>;
  onSave: (data: NoteFormData) => void;
  onCancel: () => void;
  isLoading?: boolean;
  className?: string;
}

export default function NoteEditor({
  initialData,
  onSave,
  onCancel,
  isLoading = false,
  className = '',
}: NoteEditorProps) {
  const [formData, setFormData] = useState<NoteFormData>({
    title: initialData?.title || '',
    content: initialData?.content || '',
    note_type: initialData?.note_type || 'content',
    tags: initialData?.tags || '',
    legal_reference: initialData?.legal_reference || '',
    article_number: initialData?.article_number || '',
  });

  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData({
        title: initialData.title || '',
        content: initialData.content || '',
        note_type: initialData.note_type || 'content',
        tags: initialData.tags || '',
        legal_reference: initialData.legal_reference || '',
        article_number: initialData.article_number || '',
      });
    }
  }, [initialData]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      alert('El título es obligatorio');
      return;
    }
    onSave(formData);
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const renderPreview = (content: string) => {
    if (!content) return <p className="text-gray-400 italic">Sin contenido</p>;

    return content.split('\n').map((line, i) => {
      if (line.startsWith('### ')) {
        return <h3 key={i} className="text-lg font-semibold mt-4 mb-2">{line.substring(4)}</h3>;
      }
      if (line.startsWith('## ')) {
        return <h2 key={i} className="text-xl font-semibold mt-5 mb-3">{line.substring(3)}</h2>;
      }
      if (line.startsWith('# ')) {
        return <h1 key={i} className="text-2xl font-bold mt-6 mb-4">{line.substring(2)}</h1>;
      }
      if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        return <li key={i} className="ml-6 mb-1">{line.trim().substring(2)}</li>;
      }

      const boldRegex = /\*\*(.+?)\*\*/g;
      if (boldRegex.test(line)) {
        const parts = line.split(boldRegex);
        return (
          <p key={i} className="mb-2">
            {parts.map((part, j) =>
              j % 2 === 1 ? <strong key={j}>{part}</strong> : part
            )}
          </p>
        );
      }

      if (line.trim() === '') {
        return <br key={i} />;
      }

      return <p key={i} className="mb-2">{line}</p>;
    });
  };

  return (
    <form onSubmit={handleSubmit} className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
          {initialData ? 'Editar Nota' : 'Nueva Nota'}
        </h2>
      </div>

      {/* Form Fields */}
      <div className="flex-1 overflow-y-auto space-y-4">
        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Título *
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            placeholder="Ej: Artículo 14 - Igualdad ante la ley"
          />
        </div>

        {/* Note Type */}
        <div>
          <label htmlFor="note_type" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Tipo de Nota
          </label>
          <select
            id="note_type"
            name="note_type"
            value={formData.note_type}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            <option value="content">Contenido</option>
            <option value="section">Sección/Encabezado</option>
          </select>
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Las secciones se usan como encabezados sin contenido propio
          </p>
        </div>

        {/* Content */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label htmlFor="content" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Contenido
            </label>
            <button
              type="button"
              onClick={() => setShowPreview(!showPreview)}
              className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
            >
              {showPreview ? 'Editar' : 'Vista previa'}
            </button>
          </div>

          {!showPreview ? (
            <>
              <textarea
                id="content"
                name="content"
                value={formData.content}
                onChange={handleChange}
                rows={10}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 font-mono text-sm"
                placeholder="Escribe el contenido aquí. Soporta formato básico markdown:&#10;# Título 1&#10;## Título 2&#10;### Título 3&#10;**negrita**&#10;- Lista&#10;- De items"
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Soporta Markdown básico: # encabezados, **negrita**, - listas
              </p>
            </>
          ) : (
            <div className="w-full min-h-[250px] px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900 prose dark:prose-invert max-w-none">
              {renderPreview(formData.content)}
            </div>
          )}
        </div>

        {/* Article Number */}
        <div>
          <label htmlFor="article_number" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Número de Artículo
          </label>
          <input
            type="text"
            id="article_number"
            name="article_number"
            value={formData.article_number}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            placeholder="Ej: Art. 14 CE"
          />
        </div>

        {/* Legal Reference */}
        <div>
          <label htmlFor="legal_reference" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Referencia Legal (BOE)
          </label>
          <input
            type="text"
            id="legal_reference"
            name="legal_reference"
            value={formData.legal_reference}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 font-mono text-sm"
            placeholder="Ej: BOE-A-1978-31229"
          />
        </div>

        {/* Tags */}
        <div>
          <label htmlFor="tags" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Etiquetas
          </label>
          <input
            type="text"
            id="tags"
            name="tags"
            value={formData.tags}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            placeholder="Ej: importante, examen, básico"
          />
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Separadas por comas
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <button
          type="button"
          onClick={onCancel}
          disabled={isLoading}
          className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors disabled:opacity-50"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Guardando...
            </>
          ) : (
            'Guardar'
          )}
        </button>
      </div>
    </form>
  );
}
