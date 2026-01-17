"""
Script para ejecutar todos los seeds con autenticación
"""

import requests
import subprocess
import sys

API_URL = "http://localhost:7999/api"

def get_auth_token(username, password):
    """Obtener token de autenticación"""
    print(f"🔐 Obteniendo token para usuario '{username}'...")

    data = {
        "username": username,
        "password": password
    }

    response = requests.post(f"{API_URL}/auth/token", data=data)

    if response.status_code == 200:
        token_data = response.json()
        print(f"✅ Token obtenido correctamente\n")
        return token_data['access_token']
    else:
        print(f"❌ Error obteniendo token: {response.json()}")
        return None

def run_seed_with_auth(script_name, token):
    """Ejecutar script de seed modificando las requests para incluir auth"""
    print(f"\n{'='*60}")
    print(f"📦 Ejecutando {script_name}...")
    print(f"{'='*60}\n")

    # Leer el script
    with open(script_name, 'r', encoding='utf-8') as f:
        script_content = f.read()

    # Modificar requests.post para incluir header de autenticación
    modified_script = script_content.replace(
        'requests.post(f"{API_URL}/decks/", json=deck_data)',
        f'requests.post(f"{{API_URL}}/decks/", json=deck_data, headers={{"Authorization": "Bearer {token}"}})'
    )

    modified_script = modified_script.replace(
        'requests.post(f"{API_URL}/flashcards/", json=flashcard)',
        f'requests.post(f"{{API_URL}}/flashcards/", json=flashcard, headers={{"Authorization": "Bearer {token}"}})'
    )

    # Ejecutar el script modificado
    exec(modified_script, globals())

def main():
    print("🚀 OpositApp - Seed All Data")
    print("="*60)
    print()

    # Pedir credenciales
    username = input("👤 Usuario (default: alejandro): ").strip() or "alejandro"
    password = input("🔑 Contraseña (default: oposit2026): ").strip() or "oposit2026"
    print()

    # Obtener token
    token = get_auth_token(username, password)

    if not token:
        print("\n❌ No se pudo obtener el token. Abortando...")
        sys.exit(1)

    # Scripts de seed
    seed_scripts = [
        'seed_tema1.py',
        'seed_tema2.py',
        'seed_tema3.py',
        'seed_tema4.py',
        'seed_tema5.py'
    ]

    print(f"\n📚 Se ejecutarán {len(seed_scripts)} scripts de seed\n")

    for script in seed_scripts:
        try:
            run_seed_with_auth(script, token)
        except Exception as e:
            print(f"❌ Error ejecutando {script}: {e}")
            continue

    print("\n" + "="*60)
    print("✅ Proceso de seed completado")
    print("="*60)

if __name__ == "__main__":
    main()
