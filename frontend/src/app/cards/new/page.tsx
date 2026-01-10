"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7999';

interface Deck {
  id: number;
  name: string;
}

type Mode = 'manual' | 'ai';

interface GeneratedCard {
  front: string;
  back: string;
  tags: string | null;
  article_number: string | null;
  law_name: string | null;
}

export default function NewCardPage() {
  const { token } = useAuth();
  const router = useRouter();
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [mode, setMode] = useState<Mode>('manual');

  // Estado para modo manual
  const [formData, setFormData] = useState({
    deck_id: "",
    front: "",
    back: "",
    article_number: "",
    law_name: "",
    tags: "",
  });

  // Estado para modo IA
  const [aiText, setAiText] = useState("");
  const [generating, setGenerating] = useState(false);
  const [generatedCards, setGeneratedCards] = useState<GeneratedCard[]>([]);
  const [showPreview, setShowPreview] = useState(false);
  const [selectedDeckForAI, setSelectedDeckForAI] = useState("");

  useEffect(() => {
    if (!token) {
      router.push("/login");
      return;
    }
    fetchDecks();
  }, [token, router]);

  const fetchDecks = async () => {
    if (!token) return;

    try {
      const response = await fetch(`${API_URL}/api/decks/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Error al obtener los mazos");
      }

      const data = await response.json();
      setDecks(Array.isArray(data) ? data : []);
      if (data.length > 0) {
        setFormData((prev) => ({ ...prev, deck_id: data[0].id.toString() }));
      }
    } catch (error) {
      console.error("Error fetching decks:", error);
      setDecks([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    setSubmitting(true);

    try {
      const response = await fetch(`${API_URL}/api/flashcards/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          deck_id: parseInt(formData.deck_id),
          front: formData.front,
          back: formData.back,
          article_number: formData.article_number || null,
          law_name: formData.law_name || null,
          tags: formData.tags || null,
        }),
      });

      if (response.ok) {
        router.push("/");
      } else {
        alert("Error al crear la flashcard");
      }
    } catch (error) {
      console.error("Error creating flashcard:", error);
      alert("Error al crear la flashcard");
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleGenerateWithAI = async () => {
    if (!aiText.trim()) {
      alert("Por favor ingresa texto para generar flashcards");
      return;
    }

    if (!selectedDeckForAI) {
      alert("Por favor selecciona un mazo");
      return;
    }

    setGenerating(true);

    try {
      const selectedDeck = decks.find(d => d.id.toString() === selectedDeckForAI);
      const deckContext = selectedDeck?.name || "";

      const response = await fetch(`${API_URL}/api/flashcards/generate-from-text`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          text: aiText,
          deck_context: deckContext,
          max_cards: 10,
        }),
      });

      if (response.ok) {
        const cards = await response.json();
        setGeneratedCards(cards);
        setShowPreview(true);
      } else {
        const error = await response.json();
        alert(error.detail || "Error al generar flashcards");
      }
    } catch (error) {
      console.error("Error generating flashcards:", error);
      alert("Error al generar flashcards");
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveGeneratedCards = async () => {
    if (generatedCards.length === 0) return;

    setSubmitting(true);

    try {
      let savedCount = 0;
      let failedCount = 0;

      for (const card of generatedCards) {
        try {
          const response = await fetch(`${API_URL}/api/flashcards/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              deck_id: parseInt(selectedDeckForAI),
              front: card.front,
              back: card.back,
              article_number: card.article_number || null,
              law_name: card.law_name || null,
              tags: card.tags || null,
            }),
          });

          if (response.ok) {
            savedCount++;
          } else {
            failedCount++;
          }
        } catch (error) {
          failedCount++;
        }
      }

      if (savedCount > 0) {
        alert(`${savedCount} flashcard(s) creadas exitosamente${failedCount > 0 ? `, ${failedCount} fallaron` : ""}`);
        router.push("/");
      } else {
        alert("Error al crear las flashcards");
      }
    } catch (error) {
      console.error("Error saving flashcards:", error);
      alert("Error al guardar las flashcards");
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditGeneratedCard = (index: number, field: keyof GeneratedCard, value: string) => {
    const updated = [...generatedCards];
    updated[index] = { ...updated[index], [field]: value };
    setGeneratedCards(updated);
  };

  const handleDeleteGeneratedCard = (index: number) => {
    setGeneratedCards(generatedCards.filter((_, i) => i !== index));
  };

  if (loading) {
    return (
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-300 rounded w-48 mb-6"></div>
            <div className="h-96 bg-gray-300 rounded"></div>
          </div>
        </div>
      </main>
    );
  }

  if (decks.length === 0) {
    return (
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="text-6xl mb-4">📚</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Primero crea un mazo
            </h2>
            <p className="text-gray-600 mb-6">
              Necesitas tener al menos un mazo creado antes de añadir flashcards.
            </p>
            <Link
              href="/decks/new"
              className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              Crear Mazo
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Link
            href="/"
            className="text-blue-600 hover:text-blue-800 font-medium mb-4 inline-block"
          >
            ← Volver
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">
            ➕ Nueva Flashcard
          </h1>
        </div>

        {/* Toggle Manual/IA */}
        <div className="flex gap-2 mb-6">
          <button
            type="button"
            onClick={() => setMode('manual')}
            className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-colors ${
              mode === 'manual'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            ✏️ Manual
          </button>
          <button
            type="button"
            onClick={() => setMode('ai')}
            className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-colors ${
              mode === 'ai'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            🤖 Generar con IA
          </button>
        </div>

        {/* Modo Manual */}
        {mode === 'manual' && (
          <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-6">
          {/* Deck Selection */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Mazo *
            </label>
            <select
              name="deck_id"
              value={formData.deck_id}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            >
              {decks.map((deck) => (
                <option key={deck.id} value={deck.id}>
                  {deck.name}
                </option>
              ))}
            </select>
          </div>

          {/* Front (Question) */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Pregunta (Anverso) *
            </label>
            <textarea
              name="front"
              value={formData.front}
              onChange={handleChange}
              required
              rows={3}
              placeholder="Ej: Art. 15 CE - ¿Qué derechos fundamentales protege?"
              className="w-full px-4 py-2 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none outline-none placeholder:text-gray-400"
            />
          </div>

          {/* Back (Answer) */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Respuesta (Reverso) *
            </label>
            <textarea
              name="back"
              value={formData.back}
              onChange={handleChange}
              required
              rows={5}
              placeholder="Ej: Derecho a la vida y a la integridad física y moral..."
              className="w-full px-4 py-2 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none outline-none placeholder:text-gray-400"
            />
          </div>

          {/* Metadata */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Artículo
              </label>
              <input
                type="text"
                name="article_number"
                value={formData.article_number}
                onChange={handleChange}
                placeholder="Ej: Art. 15"
                className="w-full px-4 py-2 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none placeholder:text-gray-400"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Ley
              </label>
              <input
                type="text"
                name="law_name"
                value={formData.law_name}
                onChange={handleChange}
                placeholder="Ej: Constitución Española"
                className="w-full px-4 py-2 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none placeholder:text-gray-400"
              />
            </div>
          </div>

          {/* Tags */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Etiquetas (separadas por comas)
            </label>
            <input
              type="text"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              placeholder="Ej: derechos-fundamentales, vida, integridad"
              className="w-full px-4 py-2 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none placeholder:text-gray-400"
            />
          </div>

          {/* Submit Button */}
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:cursor-not-allowed"
            >
              {submitting ? "Creando..." : "Crear Flashcard"}
            </button>
            <Link
              href="/"
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </Link>
          </div>
        </form>
        )}

        {/* Modo IA */}
        {mode === 'ai' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              🤖 Generar Flashcards con IA
            </h2>

            {/* Selector de mazo */}
            <div className="mb-4">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Mazo *
              </label>
              <select
                value={selectedDeckForAI}
                onChange={(e) => setSelectedDeckForAI(e.target.value)}
                className="w-full px-4 py-2 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none"
                required
              >
                <option value="">Selecciona un mazo</option>
                {decks.map((deck) => (
                  <option key={deck.id} value={deck.id}>
                    {deck.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Textarea para texto */}
            <div className="mb-4">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Pega el texto del que quieres generar flashcards
              </label>
              <textarea
                value={aiText}
                onChange={(e) => setAiText(e.target.value)}
                rows={20}
                className="w-full px-4 py-2 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none outline-none placeholder:text-gray-400"
                placeholder="Ej: Pega aquí el contenido de un artículo, ley, o tema de estudio..."
              />
              <p className="text-sm text-gray-500 mt-1">
                {aiText.length} / 15,000 caracteres
              </p>
            </div>

            {/* Botones */}
            <div className="flex gap-3">
              <button
                type="button"
                onClick={handleGenerateWithAI}
                disabled={generating || !aiText.trim() || !selectedDeckForAI}
                className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:cursor-not-allowed"
              >
                {generating ? "Generando..." : "🤖 Generar Flashcards"}
              </button>
              <Link
                href="/"
                className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </Link>
            </div>
          </div>
        )}

        {/* Modal de preview de flashcards generadas */}
        {showPreview && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                ✨ Flashcards Generadas ({generatedCards.length})
              </h2>

              <p className="text-gray-600 mb-6">
                Revisa y edita las flashcards antes de guardarlas
              </p>

              {/* Lista de cards generadas */}
              <div className="space-y-4 mb-6">
                {generatedCards.map((card, index) => (
                  <div key={index} className="border rounded-lg p-4 bg-gray-50">
                    <div className="flex justify-between items-start mb-3">
                      <span className="text-sm font-semibold text-gray-500">
                        Card {index + 1}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleDeleteGeneratedCard(index)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        ✕ Eliminar
                      </button>
                    </div>

                    {/* Front */}
                    <div className="mb-3">
                      <label className="block text-xs font-semibold text-gray-700 mb-1">
                        Pregunta
                      </label>
                      <textarea
                        value={card.front}
                        onChange={(e) => handleEditGeneratedCard(index, 'front', e.target.value)}
                        rows={2}
                        className="w-full px-3 py-2 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
                      />
                    </div>

                    {/* Back */}
                    <div className="mb-3">
                      <label className="block text-xs font-semibold text-gray-700 mb-1">
                        Respuesta
                      </label>
                      <textarea
                        value={card.back}
                        onChange={(e) => handleEditGeneratedCard(index, 'back', e.target.value)}
                        rows={3}
                        className="w-full px-3 py-2 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
                      />
                    </div>

                    {/* Metadata */}
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-xs font-semibold text-gray-700 mb-1">
                          Artículo
                        </label>
                        <input
                          type="text"
                          value={card.article_number || ''}
                          onChange={(e) => handleEditGeneratedCard(index, 'article_number', e.target.value)}
                          className="w-full px-3 py-2 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-gray-700 mb-1">
                          Ley
                        </label>
                        <input
                          type="text"
                          value={card.law_name || ''}
                          onChange={(e) => handleEditGeneratedCard(index, 'law_name', e.target.value)}
                          className="w-full px-3 py-2 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
                        />
                      </div>
                    </div>

                    {/* Tags */}
                    <div className="mt-2">
                      <label className="block text-xs font-semibold text-gray-700 mb-1">
                        Etiquetas
                      </label>
                      <input
                        type="text"
                        value={card.tags || ''}
                        onChange={(e) => handleEditGeneratedCard(index, 'tags', e.target.value)}
                        className="w-full px-3 py-2 text-sm text-gray-900 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Botones del modal */}
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleSaveGeneratedCards}
                  disabled={submitting || generatedCards.length === 0}
                  className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:cursor-not-allowed"
                >
                  {submitting ? "Guardando..." : `✓ Guardar ${generatedCards.length} Flashcard(s)`}
                </button>
                <button
                  type="button"
                  onClick={() => setShowPreview(false)}
                  className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
