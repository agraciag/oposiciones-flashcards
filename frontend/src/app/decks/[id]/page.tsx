"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7999';

interface Deck {
  id: number;
  name: string;
  description: string;
  created_at: string;
}

interface Flashcard {
  id: number;
  front: string;
  back: string;
  tags: string;
  next_review: string;
}

export default function DeckDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [deck, setDeck] = useState<Deck | null>(null);
  const [cards, setCards] = useState<Flashcard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const deckId = params.id;

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch deck details
        const deckRes = await fetch(`${API_URL}/api/decks/${deckId}`);
        if (!deckRes.ok) throw new Error("Deck not found");
        const deckData = await deckRes.json();
        setDeck(deckData);

        // Fetch cards for this deck
        const cardsRes = await fetch(`${API_URL}/api/flashcards/?deck_id=${deckId}`);
        if (cardsRes.ok) {
          const cardsData = await cardsRes.json();
          setCards(cardsData);
        }
      } catch (err) {
        setError("Error al cargar el mazo");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (deckId) {
      fetchData();
    }
  }, [deckId]);

  const handleDelete = async () => {
    if (!confirm("¿Estás seguro de que quieres eliminar este mazo y todas sus tarjetas?")) return;

    try {
      const res = await fetch(`${API_URL}/api/decks/${deckId}`, {
        method: "DELETE",
      });
      if (res.ok) {
        router.push("/");
      } else {
        alert("Error al eliminar el mazo");
      }
    } catch (err) {
      console.error(err);
      alert("Error al eliminar");
    }
  };

  if (loading) return <div className="text-center py-10">Cargando...</div>;
  if (error || !deck) return <div className="text-center py-10 text-red-600">{error || "Mazo no encontrado"}</div>;

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Link
            href="/"
            className="text-blue-600 hover:text-blue-800 font-medium mb-4 inline-block"
          >
            ← Volver al inicio
          </Link>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{deck.name}</h1>
              <p className="text-gray-600">{deck.description}</p>
            </div>
            <div className="flex gap-2">
              <Link
                href={`/study?deckId=${deck.id}`}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
              >
                ▶ Estudiar
              </Link>
              <button
                onClick={handleDelete}
                className="bg-red-100 hover:bg-red-200 text-red-700 px-4 py-2 rounded-lg font-semibold transition-colors"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>

        {/* Stats / Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-sm text-gray-500">Total Tarjetas</div>
            <div className="text-2xl font-bold text-gray-900">{cards.length}</div>
          </div>
          {/* Placeholder for future stats */}
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-sm text-gray-500">A repasar hoy</div>
            <div className="text-2xl font-bold text-gray-900">
             {cards.filter(c => new Date(c.next_review) <= new Date()).length}
            </div>
          </div>
        </div>

        {/* Cards List */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
            <h2 className="text-lg font-semibold text-gray-900">Tarjetas del Mazo</h2>
            <Link
              href={`/cards/new?deckId=${deck.id}`}
              className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-md hover:bg-blue-700 transition-colors"
            >
              + Nueva Tarjeta
            </Link>
          </div>
          
          {cards.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              No hay tarjetas en este mazo todavía.
              <br />
              <Link href={`/cards/new?deckId=${deck.id}`} className="text-blue-600 hover:underline mt-2 inline-block">
                ¡Crea la primera!
              </Link>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {cards.map((card) => (
                <div key={card.id} className="p-4 hover:bg-gray-50 transition-colors flex justify-between items-start group">
                  <div className="flex-1 pr-4">
                    <div className="font-medium text-gray-900 mb-1">{card.front}</div>
                    <div className="text-sm text-gray-500 line-clamp-2">{card.back}</div>
                    {card.tags && (
                      <div className="mt-2 flex gap-1">
                        {card.tags.split(',').map((tag, i) => (
                          <span key={i} className="inline-block px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">
                            {tag.trim()}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
                     <Link
                      href={`/cards/${card.id}`}
                      className="text-gray-400 hover:text-blue-600"
                    >
                      ✏️
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
