# Configuración Estándar: WSL2 + Cloudflare Tunnel

Este documento define el estándar de configuración para exponer proyectos web locales a internet utilizando Cloudflare Tunnel en este entorno de desarrollo (WSL2).

## 1. Arquitectura del Túnel (Infraestructura)

El túnel de Cloudflare se ejecuta en un contenedor Docker independiente. Para que este contenedor pueda comunicarse con los servicios que corren en el "localhost" de la máquina WSL, se utiliza la configuración `extra_hosts`.

### Configuración del `docker-compose.yml` del Túnel:
```yaml
services:
  tunnel:
    image: cloudflare/cloudflared
    # ... otras configuraciones ...
    extra_hosts:
      - "host.docker.internal:host-gateway"
```
*Esto mapea `host.docker.internal` dentro del contenedor a la IP de la puerta de enlace de Docker en el host.*

## 2. Configuración de los Proyectos (Aplicaciones)

Para que el túnel pueda acceder a una aplicación corriendo en WSL, la aplicación **NO** puede escuchar solo en `localhost` (127.0.0.1), ya que Docker considera `localhost` como su propio entorno interno.

**Regla de Oro:** Todos los servidores de desarrollo deben escuchar en **`0.0.0.0`**.

### Next.js (Ejemplo: proyecto `menu`)
En `package.json`:
```json
"scripts": {
  "dev": "next dev -p [PUERTO] -H 0.0.0.0"
}
```

### Astro / Vite (Ejemplo: proyecto `alejandrogracia_web`)
Requiere dos pasos: escuchar en 0.0.0.0 y permitir el host externo en la config de Vite para evitar bloqueos de seguridad "Bad Gateway" o "Blocked Request".

**1. En `package.json`:**
```json
"scripts": {
  "dev": "astro dev --host 0.0.0.0 --port [PUERTO]"
}
```

**2. En `astro.config.mjs` (Configuración de Vite):**
```javascript
export default defineConfig({
  server: {
    host: true, // Escuchar en 0.0.0.0
    port: [PUERTO]
  },
  vite: {
    server: {
      allowedHosts: true // Permitir acceso desde el dominio del túnel (CRÍTICO)
    }
  }
});
```

### Python / Django
```bash
python manage.py runserver 0.0.0.0:[PUERTO]
```

### Node / Express
```javascript
app.listen([PUERTO], '0.0.0.0', () => { ... });
```

### FastAPI (Python)
```python
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Escuchar en todas las interfaces
        port=[PUERTO],
        reload=True
    )
```

## 3. Configuración en el Panel de Cloudflare

Al configurar el "Public Hostname" en el dashboard de Zero Trust:
- **Service Type:** HTTP
- **URL:** `http://host.docker.internal:[PUERTO]`

---

## Configuración para OpositApp

### Puertos Actuales:
- **Frontend (Next.js):** 2998
- **Backend (FastAPI):** 7999
- **PostgreSQL:** 5399
- **Redis:** 6379
- **pgAdmin:** 5049

### Frontend Next.js (Ya Configurado)
```json
{
  "scripts": {
    "dev": "next dev -p 2998 -H 0.0.0.0"
  }
}
```

### Backend FastAPI (Ya Configurado)
```python
# backend/main.py
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # ✅ Ya configurado
        port=7999,
        reload=settings.DEBUG
    )
```

### Configuración en Cloudflare Zero Trust:

**Para Frontend:**
- Service Type: HTTP
- URL: `http://host.docker.internal:2998`
- Public Hostname: `oposit.tudominio.com` (o el que prefieras)

**Para Backend API:**
- Service Type: HTTP
- URL: `http://host.docker.internal:7999`
- Public Hostname: `api-oposit.tudominio.com` (o el que prefieras)

### CORS Backend

Asegúrate de añadir el dominio de Cloudflare a `ALLOWED_ORIGINS` en `backend/.env`:

```env
ALLOWED_ORIGINS=http://localhost:2998,http://localhost:7999,https://oposit.tudominio.com,https://api-oposit.tudominio.com
```

---

## Checklist para Exponer un Nuevo Proyecto

- [ ] Servidor escucha en `0.0.0.0` (no en `localhost`)
- [ ] Puerto configurado en `package.json` o script de inicio
- [ ] Cloudflare Tunnel tiene `extra_hosts: host.docker.internal:host-gateway`
- [ ] Public Hostname apunta a `http://host.docker.internal:[PUERTO]`
- [ ] CORS configurado si es una API (incluir dominio Cloudflare)
- [ ] Vite/Astro: `allowedHosts: true` si aplica
- [ ] Probar acceso desde el dominio público

---

**Última actualización:** 1 enero 2026
