"use client";

import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:7999";

interface FlashcardPreview {
  front: string;
  back: string;
  tags: string;
}

export default function ImportPDFPage() {
  const { token } = useAuth();
  const router = useRouter();
  const [step, setStep] = useState<"upload" | "preview">("upload");

  // Upload form
  const [file, setFile] = useState<File | null>(null);
  const [deckName, setDeckName] = useState("");
  const [description, setDescription] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  // Preview data
  const [flashcards, setFlashcards] = useState<FlashcardPreview[]>([]);
  const [saving, setSaving] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type !== "application/pdf") {
        setUploadError("Solo se permiten archivos PDF");
        return;
      }
      if (selectedFile.size > 10 * 1024 * 1024) {
        setUploadError("El archivo es demasiado grande (máximo 10MB)");
        return;
      }
      setFile(selectedFile);
      setUploadError("");
    }
  };

  const handleUpload = async () => {
    if (!file || !deckName.trim()) {
      setUploadError("Debes seleccionar un PDF y escribir un nombre para el mazo");
      return;
    }

    setUploading(true);
    setUploadError("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("deck_name", deckName);
      if (description) {
        formData.append("description", description);
      }

      const response = await fetch(`${API_URL}/api/decks/import-pdf`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setFlashcards(data.flashcards_preview);
        setStep("preview");
      } else {
        const error = await response.json();
        setUploadError(error.detail || "Error al procesar el PDF");
      }
    } catch (err) {
      setUploadError("Error de conexión con el servidor");
    } finally {
      setUploading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);

    try {
      const response = await fetch(`${API_URL}/api/decks/import-pdf/confirm`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          deck_name: deckName,
          description,
          flashcards,
        }),
      });

      if (response.ok) {
        router.push("/");
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (err) {
      alert("Error de conexión con el servidor");
    } finally {
      setSaving(false);
    }
  };

  const handleEditCard = (index: number, field: "front" | "back" | "tags", value: string) => {
    const updated = [...flashcards];
    updated[index][field] = value;
    setFlashcards(updated);
  };

  if (step === "upload") {
    return (
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="mb-6">
            <Link
              href="/"
              className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium mb-4 inline-block"
            >
              ← Volver al inicio
            </Link>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
              📄 Importar PDF
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              Sube un PDF y genera flashcards automáticamente con IA
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            {uploadError && (
              <div className="p-3 mb-4 text-sm text-red-700 bg-red-100 dark:bg-red-900/20 dark:text-red-400 rounded-lg">
                {uploadError}
              </div>
            )}

            <div className="mb-4">
              <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                Archivo PDF
              </label>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="w-full p-3 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-50 dark:file:bg-blue-900/20 file:text-blue-700 dark:file:text-blue-400 file:cursor-pointer"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Máximo 10MB
              </p>
            </div>

            <div className="mb-4">
              <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                Nombre del Mazo *
              </label>
              <input
                type="text"
                value={deckName}
                onChange={(e) => setDeckName(e.target.value)}
                className="w-full p-3 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none placeholder:text-gray-400"
                placeholder="Ej: Tema 1 - Constitución Española"
                required
              />
            </div>

            <div className="mb-4">
              <label className="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                Descripción (opcional)
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                className="w-full p-3 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none placeholder:text-gray-400"
                placeholder="Describe el contenido del mazo..."
              />
            </div>

            <button
              onClick={handleUpload}
              disabled={uploading || !file || !deckName.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              {uploading ? "Procesando PDF con IA... 🤖" : "Subir y Generar Flashcards"}
            </button>

            <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <strong>💡 Consejo:</strong> La IA analizará el contenido del PDF y
                generará flashcards automáticamente. Podrás revisarlas y editarlas antes
                de guardarlas.
              </p>
            </div>
          </div>
        </div>
      </main>
    );
  }

  // Preview Step
  return (
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            ✨ Flashcards Generadas
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Se generaron <strong>{flashcards.length} flashcards</strong>. Puedes editarlas
            antes de guardar.
          </p>
        </div>

        <div className="space-y-4 mb-6">
          {flashcards.map((card, index) => (
            <div
              key={index}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700"
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Tarjeta {index + 1}
                </h3>
              </div>

              <div className="mb-3">
                <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Pregunta (Front)
                </label>
                <textarea
                  value={card.front}
                  onChange={(e) => handleEditCard(index, "front", e.target.value)}
                  rows={2}
                  className="w-full p-2 text-sm text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <div className="mb-3">
                <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Respuesta (Back)
                </label>
                <textarea
                  value={card.back}
                  onChange={(e) => handleEditCard(index, "back", e.target.value)}
                  rows={3}
                  className="w-full p-2 text-sm text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                />
              </div>

              <div>
                <label className="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">
                  Tags
                </label>
                <input
                  type="text"
                  value={card.tags}
                  onChange={(e) => handleEditCard(index, "tags", e.target.value)}
                  className="w-full p-2 text-sm text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  placeholder="tag1,tag2,tag3"
                />
              </div>
            </div>
          ))}
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            {saving ? "Guardando..." : `💾 Guardar ${flashcards.length} Flashcards`}
          </button>
          <button
            onClick={() => setStep("upload")}
            className="px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Cancelar
          </button>
        </div>
      </div>
    </main>
  );
}
