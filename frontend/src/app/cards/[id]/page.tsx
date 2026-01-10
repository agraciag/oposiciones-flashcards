"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7999';

interface Deck {
  id: number;
  name: string;
}

export default function EditCardPage() {
  const { token } = useAuth();
  const router = useRouter();
  const params = useParams();
  const cardId = params.id;

  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

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

    const fetchData = async () => {
      if (!token) return;

      try {
        // Fetch decks first
        const decksRes = await fetch(`${API_URL}/api/decks/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!decksRes.ok) throw new Error("Error al obtener mazos");
        const decksData = await decksRes.json();
        setDecks(Array.isArray(decksData) ? decksData : []);

        // Fetch card details
        const cardRes = await fetch(`${API_URL}/api/flashcards/${cardId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!cardRes.ok) throw new Error("Card not found");
        const cardData = await cardRes.json();
        
        setFormData({
            deck_id: cardData.deck_id.toString(),
            front: cardData.front,
            back: cardData.back,
            article_number: cardData.article_number || "",
            law_name: cardData.law_name || "",
            tags: cardData.tags || "",
        });

      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Error al cargar la tarjeta");
      } finally {
        setLoading(false);
      }
    };

    if (cardId) {
      fetchData();
    }
  }, [cardId, token, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    setSubmitting(true);

    try {
      const response = await fetch(`${API_URL}/api/flashcards/${cardId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          front: formData.front,
          back: formData.back,
          article_number: formData.article_number || null,
          law_name: formData.law_name || null,
          tags: formData.tags || null,
        }),
      });

      if (response.ok) {
        // Go back to the deck page
        const deckId = formData.deck_id; // current deck id
        router.push(`/decks/${deckId}`);
      } else {
        alert("Error al actualizar la flashcard");
      }
    } catch (error) {
      console.error("Error updating flashcard:", error);
      alert("Error al actualizar la flashcard");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
      if(!confirm("¿Estás seguro de que quieres eliminar esta tarjeta?")) return;
      
      try {
          const res = await fetch(`${API_URL}/api/flashcards/${cardId}`, {
              method: 'DELETE'
          });
          if (res.ok) {
              router.push(`/decks/${formData.deck_id}`);
          } else {
              alert("Error al eliminar");
          }
      } catch (e) {
          console.error(e);
          alert("Error al eliminar");
      }
  }

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  if (loading) {
    return <div className="text-center py-10">Cargando...</div>;
  }

  if (error) {
      return <div className="text-center py-10 text-red-600">{error}</div>;
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex justify-between items-end">
          <div>
            <Link
                href={`/decks/${formData.deck_id}`}
                className="text-blue-600 hover:text-blue-800 font-medium mb-4 inline-block"
            >
                ← Volver al Mazo
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">
                ✏️ Editar Flashcard
            </h1>
          </div>
          <button 
            onClick={handleDelete}
            className="text-red-600 hover:text-red-800 font-medium"
          >
              Eliminar
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-6">
          {/* Deck Selection (Read Only for now or editable if backend supports moving decks?) 
              The PUT endpoint I added handles updating properties. 
              Checking the backend code: `update_flashcard` updates attributes. 
              The `FlashcardUpdate` schema doesn't include `deck_id`. 
              So I should disable deck selection or remove it from update payload.
              I'll keep it disabled for now to be safe.
           */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Mazo
            </label>
            <select
              name="deck_id"
              value={formData.deck_id}
              disabled
              className="w-full px-4 py-2 text-gray-900 dark:text-gray-100 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg cursor-not-allowed outline-none"
            >
              {decks.map((deck) => (
                <option key={deck.id} value={deck.id}>
                  {deck.name}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">Para mover una tarjeta de mazo, crea una nueva y borra esta (por ahora).</p>
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
              className="w-full px-4 py-2 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none placeholder:text-gray-400"
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
              className="w-full px-4 py-2 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none placeholder:text-gray-400"
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
              {submitting ? "Guardando..." : "Guardar Cambios"}
            </button>
            <Link
              href={`/decks/${formData.deck_id}`}
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
