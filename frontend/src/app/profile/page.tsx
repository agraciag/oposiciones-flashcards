"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:7999";

export default function ProfilePage() {
  const { user, token, logout } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  // Email form
  const [emailForm, setEmailForm] = useState({
    new_email: "",
    current_password: "",
  });
  const [emailError, setEmailError] = useState("");
  const [emailSuccess, setEmailSuccess] = useState("");
  const [emailSubmitting, setEmailSubmitting] = useState(false);

  // Password form
  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
    confirm_new_password: "",
  });
  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] = useState("");
  const [passwordSubmitting, setPasswordSubmitting] = useState(false);

  useEffect(() => {
    if (!token) {
      router.push("/login");
    } else {
      setLoading(false);
    }
  }, [token, router]);

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailSubmitting(true);
    setEmailError("");
    setEmailSuccess("");

    try {
      const response = await fetch(`${API_URL}/api/profile/email`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(emailForm),
      });

      if (response.ok) {
        setEmailSuccess("Email actualizado correctamente");
        setEmailForm({ new_email: "", current_password: "" });
        // Actualizar usuario en contexto
        setTimeout(() => window.location.reload(), 1500);
      } else {
        const data = await response.json();
        setEmailError(data.detail || "Error al actualizar email");
      }
    } catch (err) {
      setEmailError("Error de conexión con el servidor");
    } finally {
      setEmailSubmitting(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordSubmitting(true);
    setPasswordError("");
    setPasswordSuccess("");

    try {
      const response = await fetch(`${API_URL}/api/profile/password`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(passwordForm),
      });

      if (response.ok) {
        setPasswordSuccess("Contraseña actualizada correctamente");
        setPasswordForm({
          current_password: "",
          new_password: "",
          confirm_new_password: "",
        });
      } else {
        const data = await response.json();
        setPasswordError(data.detail || "Error al actualizar contraseña");
      }
    } catch (err) {
      setPasswordError("Error de conexión con el servidor");
    } finally {
      setPasswordSubmitting(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Cargando...</div>;
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
            ← Volver al inicio
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">⚙️ Mi Perfil</h1>
          <p className="text-gray-600 mt-2">
            Usuario: <strong>{user?.username}</strong>
          </p>
          <p className="text-gray-600">
            Email actual: <strong>{user?.email}</strong>
          </p>
        </div>

        {/* Cambiar Email */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">📧 Cambiar Email</h2>

          {emailError && (
            <div className="p-3 mb-4 text-sm text-red-700 bg-red-100 rounded-lg">
              {emailError}
            </div>
          )}

          {emailSuccess && (
            <div className="p-3 mb-4 text-sm text-green-700 bg-green-100 rounded-lg">
              {emailSuccess}
            </div>
          )}

          <form onSubmit={handleEmailSubmit}>
            <div className="mb-4">
              <label className="block mb-2 text-sm font-medium text-gray-700">
                Nuevo Email
              </label>
              <input
                type="email"
                value={emailForm.new_email}
                onChange={(e) => setEmailForm({ ...emailForm, new_email: e.target.value })}
                className="w-full p-3 text-gray-900 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none placeholder:text-gray-400"
                required
                placeholder="nuevo@email.com"
              />
            </div>

            <div className="mb-4">
              <label className="block mb-2 text-sm font-medium text-gray-700">
                Contraseña Actual (para confirmar)
              </label>
              <input
                type="password"
                value={emailForm.current_password}
                onChange={(e) =>
                  setEmailForm({ ...emailForm, current_password: e.target.value })
                }
                className="w-full p-3 text-gray-900 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none placeholder:text-gray-400"
                required
              />
            </div>

            <button
              type="submit"
              disabled={emailSubmitting}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              {emailSubmitting ? "Actualizando..." : "Actualizar Email"}
            </button>
          </form>
        </div>

        {/* Cambiar Contraseña */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">🔒 Cambiar Contraseña</h2>

          {passwordError && (
            <div className="p-3 mb-4 text-sm text-red-700 bg-red-100 rounded-lg">
              {passwordError}
            </div>
          )}

          {passwordSuccess && (
            <div className="p-3 mb-4 text-sm text-green-700 bg-green-100 rounded-lg">
              {passwordSuccess}
            </div>
          )}

          <form onSubmit={handlePasswordSubmit}>
            <div className="mb-4">
              <label className="block mb-2 text-sm font-medium text-gray-700">
                Contraseña Actual
              </label>
              <input
                type="password"
                value={passwordForm.current_password}
                onChange={(e) =>
                  setPasswordForm({ ...passwordForm, current_password: e.target.value })
                }
                className="w-full p-3 text-gray-900 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none placeholder:text-gray-400"
                required
              />
            </div>

            <div className="mb-4">
              <label className="block mb-2 text-sm font-medium text-gray-700">
                Nueva Contraseña
              </label>
              <input
                type="password"
                value={passwordForm.new_password}
                onChange={(e) =>
                  setPasswordForm({ ...passwordForm, new_password: e.target.value })
                }
                className="w-full p-3 text-gray-900 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none placeholder:text-gray-400"
                required
                minLength={6}
              />
              <p className="text-xs text-gray-500 mt-1">Mínimo 6 caracteres</p>
            </div>

            <div className="mb-4">
              <label className="block mb-2 text-sm font-medium text-gray-700">
                Confirmar Nueva Contraseña
              </label>
              <input
                type="password"
                value={passwordForm.confirm_new_password}
                onChange={(e) =>
                  setPasswordForm({ ...passwordForm, confirm_new_password: e.target.value })
                }
                className="w-full p-3 text-gray-900 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none placeholder:text-gray-400"
                required
              />
            </div>

            <button
              type="submit"
              disabled={passwordSubmitting}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              {passwordSubmitting ? "Actualizando..." : "Cambiar Contraseña"}
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
