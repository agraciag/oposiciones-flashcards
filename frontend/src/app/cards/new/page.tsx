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

export default function NewCardPage() {
  const { token } = useAuth();
  const router = useRouter();
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    deck_id: "",
    front: "",
    back: "",
    article_number: "",
    law_name: "",
    tags: "",
  });

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

        {/* Form */}
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
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
      </div>
    </main>
  );
}
