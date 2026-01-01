"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface Deck {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
}

interface StudyStats {
  total_cards: number;
  cards_to_review: number;
  cards_learning: number;
  cards_mastered: number;
}

export default function Home() {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [stats, setStats] = useState<StudyStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDecks();
    fetchStats();
  }, []);

  const fetchDecks = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/decks/");
      const data = await response.json();
      setDecks(data);
    } catch (error) {
      console.error("Error fetching decks:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/study/stats");
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🧠 OpositApp
          </h1>
          <p className="text-gray-600">
            Sistema inteligente de flashcards con repetición espaciada
          </p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-2xl font-bold text-blue-600">
                {stats.total_cards}
              </div>
              <div className="text-sm text-gray-600">Total Tarjetas</div>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-2xl font-bold text-orange-600">
                {stats.cards_to_review}
              </div>
              <div className="text-sm text-gray-600">Para Revisar</div>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-2xl font-bold text-yellow-600">
                {stats.cards_learning}
              </div>
              <div className="text-sm text-gray-600">Aprendiendo</div>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-2xl font-bold text-green-600">
                {stats.cards_mastered}
              </div>
              <div className="text-sm text-gray-600">Dominadas</div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-4 mb-8">
          <Link
            href="/study"
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition-colors"
          >
            📚 Estudiar Ahora
          </Link>
          <Link
            href="/decks"
            className="bg-white hover:bg-gray-50 text-gray-900 font-semibold py-3 px-6 rounded-lg shadow-md border-2 border-gray-200 transition-colors"
          >
            📑 Gestionar Mazos
          </Link>
          <Link
            href="/cards/new"
            className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition-colors"
          >
            ➕ Nueva Tarjeta
          </Link>
        </div>

        {/* Decks List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Mis Mazos</h2>

          {loading ? (
            <div className="text-center py-8 text-gray-500">
              Cargando mazos...
            </div>
          ) : decks.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No hay mazos creados aún. ¡Crea tu primer mazo!
              <div className="mt-4">
                <Link
                  href="/decks/new"
                  className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                >
                  Crear Mazo
                </Link>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {decks.map((deck) => (
                <div
                  key={deck.id}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {deck.name}
                      </h3>
                      {deck.description && (
                        <p className="text-sm text-gray-600 mt-1">
                          {deck.description}
                        </p>
                      )}
                      <p className="text-xs text-gray-400 mt-2">
                        Creado: {new Date(deck.created_at).toLocaleDateString('es-ES')}
                      </p>
                    </div>
                    <Link
                      href={`/decks/${deck.id}`}
                      className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors"
                    >
                      Ver Mazo
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* API Status */}
        <div className="mt-8 text-center text-sm text-gray-500">
          API Backend: http://localhost:8000
        </div>
      </div>
    </main>
  );
}
