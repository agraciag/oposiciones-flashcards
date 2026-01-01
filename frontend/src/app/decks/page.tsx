"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7999';

interface Deck {
  id: number;
  name: string;
  description: string;
  created_at: string;
}

export default function DecksPage() {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDecks();
  }, []);

  const fetchDecks = async () => {
    try {
      const response = await fetch(`${API_URL}/api/decks/`);
      const data = await response.json();
      setDecks(data);
    } catch (error) {
      console.error("Error fetching decks:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">📑 Mis Mazos</h1>
            <p className="text-gray-600">Gestiona tus colecciones de flashcards</p>
          </div>
          <Link
            href="/decks/new"
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg shadow-sm transition-colors"
          >
            + Crear Nuevo Mazo
          </Link>
        </div>

        {/* List */}
        {loading ? (
          <div className="text-center py-12 text-gray-500">Cargando...</div>
        ) : decks.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-500 mb-4">No tienes ningún mazo creado.</p>
            <Link
              href="/decks/new"
              className="text-blue-600 hover:underline"
            >
              Crear el primero
            </Link>
          </div>
        ) : (
          <div className="grid gap-4">
            {decks.map((deck) => (
              <Link
                key={deck.id}
                href={`/decks/${deck.id}`}
                className="block bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md hover:border-blue-300 transition-all"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900 mb-1">
                      {deck.name}
                    </h2>
                    <p className="text-gray-600 line-clamp-2">
                      {deck.description || "Sin descripción"}
                    </p>
                  </div>
                  <span className="text-blue-600 font-medium text-sm">Ver detalles →</span>
                </div>
                <div className="mt-4 text-xs text-gray-400">
                  Creado el {new Date(deck.created_at).toLocaleDateString('es-ES')}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
