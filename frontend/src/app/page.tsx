"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { ThemeToggle } from "@/components/ThemeToggle";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7999';

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
  const { user, loading: authLoading, logout, fetchWithAuth } = useAuth();
  const router = useRouter();
  const [decks, setDecks] = useState<Deck[]>([]);
  const [stats, setStats] = useState<StudyStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
      return;
    }

    if (user) {
      fetchDecks();
      fetchStats();
    }
  }, [user, authLoading]);

  const fetchDecks = async () => {
    try {
      const response = await fetchWithAuth(`${API_URL}/api/decks/`);
      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data)) {
          setDecks(data);
        } else {
          console.error("Data received is not an array:", data);
          setDecks([]);
        }
      }
    } catch (error) {
      console.error("Error fetching decks:", error);
      setDecks([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetchWithAuth(`${API_URL}/api/study/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  if (authLoading || (!user && !authLoading)) {
    return <div className="flex items-center justify-center min-h-screen">Cargando...</div>;
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex justify-between items-start">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              🧠 OpositApp
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Bienvenido de nuevo, <span className="font-semibold text-blue-600 dark:text-blue-400">{user?.username}</span>
            </p>
          </div>
          <div className="flex gap-3 items-center">
            <ThemeToggle />
            <Link
              href="/profile"
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              ⚙️ Mi Perfil
            </Link>
            <button
              onClick={logout}
              className="px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
            >
              Cerrar Sesión
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {stats.total_cards}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Total Tarjetas</div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                {stats.cards_to_review}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Para Revisar</div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                {stats.cards_learning}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Aprendiendo</div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                {stats.cards_mastered}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Dominadas</div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4 mb-8">
          <Link
            href="/study"
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition-colors"
          >
            📚 Estudiar Ahora
          </Link>
          <Link
            href="/decks/explore"
            className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition-colors"
          >
            🌍 Explorar Comunidad
          </Link>
          <Link
            href="/decks"
            className="bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-100 font-semibold py-3 px-6 rounded-lg shadow-md border-2 border-gray-200 dark:border-gray-600 transition-colors"
          >
            📑 Mis Mazos
          </Link>
          <Link
            href="/cards/new"
            className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition-colors"
          >
            ➕ Nueva Tarjeta
          </Link>
          <Link
            href="/decks/import"
            className="bg-orange-600 hover:bg-orange-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition-colors"
          >
            📄 Importar PDF
          </Link>
          <Link
            href="/notes"
            className="bg-teal-600 hover:bg-teal-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition-colors"
          >
            📝 Apuntes
          </Link>
          <Link
            href="/study-docs"
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition-colors"
          >
            📖 Docs Interactivos
          </Link>
          <Link
            href="/syllabi"
            className="bg-amber-600 hover:bg-amber-700 text-white font-semibold py-3 px-6 rounded-lg shadow-md transition-colors"
          >
            📋 Temarios
          </Link>
        </div>

        {/* Decks List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Mis Mazos</h2>

          {loading ? (
            <div className="text-center py-8 text-gray-500">
              Cargando mazos...
            </div>
          ) : (!Array.isArray(decks) || decks.length === 0) ? (
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
          API Backend: {API_URL}
        </div>
      </div>
    </main>
  );
}
