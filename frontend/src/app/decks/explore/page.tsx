"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7999';

interface Deck {
  id: number;
  name: string;
  description: string;
  user_id: number;
  created_at: string;
}

export default function ExploreDecksPage() {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);
  const [cloningId, setCloningId] = useState<number | null>(null);
  const { fetchWithAuth, user, loading: authLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
      return;
    }
    if (user) {
      fetchPublicDecks();
    }
  }, [user, authLoading]);

  const fetchPublicDecks = async () => {
    try {
      const response = await fetchWithAuth(`${API_URL}/api/decks/public`);
      if (response.ok) {
        const data = await response.json();
        setDecks(data);
      }
    } catch (error) {
      console.error("Error fetching public decks:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleClone = async (deckId: number) => {
    setCloningId(deckId);
    try {
      const response = await fetchWithAuth(`${API_URL}/api/decks/${deckId}/clone`, {
        method: "POST",
      });
      if (response.ok) {
        const newDeck = await response.json();
        alert("¡Mazo clonado con éxito! Ahora puedes encontrarlo en tus mazos.");
        router.push(`/decks/${newDeck.id}`);
      } else {
        alert("Error al clonar el mazo");
      }
    } catch (error) {
      console.error("Error cloning deck:", error);
      alert("Error de conexión");
    } finally {
      setCloningId(null);
    }
  };

  if (authLoading || !user) return <div className="text-center py-10">Cargando...</div>;

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <Link href="/" className="text-blue-600 hover:underline mb-4 inline-block">← Volver al inicio</Link>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🌍 Explorar Comunidad</h1>
          <p className="text-gray-600">Descubre mazos compartidos por otros opositores e impórtalos a tu librería.</p>
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-500">Buscando mazos públicos...</div>
        ) : decks.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <div className="text-5xl mb-4">🔍</div>
            <p className="text-gray-500 text-lg">Parece que no hay mazos públicos disponibles en este momento.</p>
            <p className="text-sm text-gray-400 mt-2">¡Sé el primero en compartir uno de tus mazos!</p>
          </div>
        ) : (
          <div className="grid gap-6">
            {decks.map((deck) => (
              <div
                key={deck.id}
                className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h2 className="text-xl font-bold text-gray-900 mb-1">{deck.name}</h2>
                    <p className="text-gray-600 mb-4 line-clamp-2">{deck.description || "Sin descripción"}</p>
                    <div className="flex items-center gap-4 text-xs text-gray-400">
                      <span>Publicado el {new Date(deck.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleClone(deck.id)}
                    disabled={cloningId === deck.id}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors disabled:bg-blue-300"
                  >
                    {cloningId === deck.id ? "Clonando..." : "Importar Mazo"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
