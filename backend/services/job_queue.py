"""
Cola de Jobs con Redis para procesamiento asíncrono de temas
"""

import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import redis.asyncio as redis

from config import settings


class JobStatus(str, Enum):
    """Estados posibles de un job"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobQueue:
    """Cola de procesamiento de temas con Redis"""

    QUEUE_KEY = "ollama:processing_queue"
    STATUS_KEY_PREFIX = "ollama:job_status:"
    RESULT_KEY_PREFIX = "ollama:job_result:"
    PROCESSING_SET = "ollama:processing"

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self._redis: Optional[redis.Redis] = None

    async def _get_redis(self) -> redis.Redis:
        """Obtiene o crea conexión Redis"""
        if self._redis is None:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    async def close(self):
        """Cierra la conexión Redis"""
        if self._redis:
            await self._redis.close()
            self._redis = None

    async def enqueue(
        self,
        topic_id: int,
        extra_context: Optional[str] = None,
        use_embeddings: bool = False,
        priority: int = 0
    ) -> str:
        """
        Añade un job a la cola.

        Args:
            topic_id: ID del tema a procesar
            extra_context: Contexto adicional para el procesamiento
            use_embeddings: Si usar búsqueda semántica
            priority: Prioridad (mayor = más importante)

        Returns:
            job_id único
        """
        r = await self._get_redis()

        job_id = f"job:{topic_id}:{datetime.utcnow().timestamp()}"
        job_data = {
            "job_id": job_id,
            "topic_id": topic_id,
            "extra_context": extra_context,
            "use_embeddings": use_embeddings,
            "priority": priority,
            "created_at": datetime.utcnow().isoformat(),
            "status": JobStatus.PENDING.value
        }

        # Guardar datos del job
        await r.set(
            f"{self.STATUS_KEY_PREFIX}{topic_id}",
            json.dumps(job_data),
            ex=3600 * 24  # Expira en 24 horas
        )

        # Añadir a la cola (usando sorted set para prioridad)
        await r.zadd(self.QUEUE_KEY, {json.dumps(job_data): -priority})

        return job_id

    async def dequeue(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene el siguiente job de la cola.

        Returns:
            Datos del job o None si la cola está vacía
        """
        r = await self._get_redis()

        # Obtener job con mayor prioridad (menor score en sorted set)
        result = await r.zpopmin(self.QUEUE_KEY, count=1)

        if not result:
            return None

        job_json, _ = result[0]
        job_data = json.loads(job_json)

        # Marcar como procesando
        job_data["status"] = JobStatus.PROCESSING.value
        job_data["started_at"] = datetime.utcnow().isoformat()

        await r.set(
            f"{self.STATUS_KEY_PREFIX}{job_data['topic_id']}",
            json.dumps(job_data),
            ex=3600 * 24
        )

        # Añadir a set de procesando
        await r.sadd(self.PROCESSING_SET, str(job_data["topic_id"]))

        return job_data

    async def complete_job(
        self,
        topic_id: int,
        result: Dict[str, Any],
        success: bool = True
    ):
        """
        Marca un job como completado.

        Args:
            topic_id: ID del tema
            result: Resultado del procesamiento
            success: Si el procesamiento fue exitoso
        """
        r = await self._get_redis()

        # Obtener datos actuales del job
        job_json = await r.get(f"{self.STATUS_KEY_PREFIX}{topic_id}")
        if job_json:
            job_data = json.loads(job_json)
        else:
            job_data = {"topic_id": topic_id}

        # Actualizar estado
        job_data["status"] = JobStatus.COMPLETED.value if success else JobStatus.FAILED.value
        job_data["completed_at"] = datetime.utcnow().isoformat()
        job_data["success"] = success

        # Guardar resultado
        await r.set(
            f"{self.RESULT_KEY_PREFIX}{topic_id}",
            json.dumps(result),
            ex=3600 * 24
        )

        # Actualizar estado
        await r.set(
            f"{self.STATUS_KEY_PREFIX}{topic_id}",
            json.dumps(job_data),
            ex=3600 * 24
        )

        # Remover de procesando
        await r.srem(self.PROCESSING_SET, str(topic_id))

    async def get_status(self, topic_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene el estado de un job.

        Args:
            topic_id: ID del tema

        Returns:
            Estado del job o None si no existe
        """
        r = await self._get_redis()

        job_json = await r.get(f"{self.STATUS_KEY_PREFIX}{topic_id}")
        if not job_json:
            return None

        job_data = json.loads(job_json)

        # Incluir resultado si está disponible
        result_json = await r.get(f"{self.RESULT_KEY_PREFIX}{topic_id}")
        if result_json:
            job_data["result"] = json.loads(result_json)

        return job_data

    async def get_result(self, topic_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene el resultado de un job completado.

        Args:
            topic_id: ID del tema

        Returns:
            Resultado del procesamiento o None
        """
        r = await self._get_redis()

        result_json = await r.get(f"{self.RESULT_KEY_PREFIX}{topic_id}")
        if result_json:
            return json.loads(result_json)
        return None

    async def get_queue_length(self) -> int:
        """Obtiene el número de jobs en cola"""
        r = await self._get_redis()
        return await r.zcard(self.QUEUE_KEY)

    async def get_processing_count(self) -> int:
        """Obtiene el número de jobs en procesamiento"""
        r = await self._get_redis()
        return await r.scard(self.PROCESSING_SET)

    async def get_queue_status(self) -> Dict[str, Any]:
        """Obtiene estado general de la cola"""
        r = await self._get_redis()

        queue_length = await r.zcard(self.QUEUE_KEY)
        processing_count = await r.scard(self.PROCESSING_SET)
        processing_ids = await r.smembers(self.PROCESSING_SET)

        return {
            "pending_jobs": queue_length,
            "processing_jobs": processing_count,
            "processing_topic_ids": list(processing_ids),
            "status": "idle" if queue_length == 0 and processing_count == 0 else "active"
        }

    async def clear_job(self, topic_id: int):
        """Limpia los datos de un job específico"""
        r = await self._get_redis()

        await r.delete(f"{self.STATUS_KEY_PREFIX}{topic_id}")
        await r.delete(f"{self.RESULT_KEY_PREFIX}{topic_id}")
        await r.srem(self.PROCESSING_SET, str(topic_id))

    async def clear_all(self):
        """Limpia toda la cola (usar con cuidado)"""
        r = await self._get_redis()

        # Obtener todas las keys
        status_keys = await r.keys(f"{self.STATUS_KEY_PREFIX}*")
        result_keys = await r.keys(f"{self.RESULT_KEY_PREFIX}*")

        # Borrar
        if status_keys:
            await r.delete(*status_keys)
        if result_keys:
            await r.delete(*result_keys)

        await r.delete(self.QUEUE_KEY)
        await r.delete(self.PROCESSING_SET)

    async def enqueue_bulk(
        self,
        topic_ids: List[int],
        extra_context: Optional[str] = None
    ) -> List[str]:
        """
        Encola múltiples temas a la vez.

        Args:
            topic_ids: Lista de IDs de temas
            extra_context: Contexto adicional (se aplica a todos)

        Returns:
            Lista de job_ids
        """
        job_ids = []
        for i, topic_id in enumerate(topic_ids):
            job_id = await self.enqueue(
                topic_id=topic_id,
                extra_context=extra_context,
                priority=len(topic_ids) - i  # Procesar en orden
            )
            job_ids.append(job_id)
        return job_ids


class ProcessingWorker:
    """Worker para procesar jobs de la cola"""

    def __init__(self, queue: JobQueue, db_factory):
        self.queue = queue
        self.db_factory = db_factory
        self._running = False
        self._current_job = None

    async def start(self):
        """Inicia el worker"""
        self._running = True
        print("🤖 Worker de procesamiento iniciado")

        while self._running:
            try:
                job = await self.queue.dequeue()

                if job:
                    self._current_job = job
                    await self._process_job(job)
                    self._current_job = None
                else:
                    # Cola vacía, esperar
                    await asyncio.sleep(2)

            except Exception as e:
                print(f"❌ Error en worker: {e}")
                await asyncio.sleep(5)

    async def stop(self):
        """Detiene el worker"""
        self._running = False
        print("🛑 Worker de procesamiento detenido")

    async def _process_job(self, job: Dict[str, Any]):
        """Procesa un job individual"""
        topic_id = job["topic_id"]
        extra_context = job.get("extra_context")
        use_embeddings = job.get("use_embeddings", False)

        print(f"📝 Procesando tema {topic_id}...")

        try:
            # Importar aquí para evitar circular imports
            from services.rag_processor import RAGProcessor

            # Crear sesión de BD
            db = self.db_factory()

            try:
                processor = RAGProcessor(db)
                result = await processor.process_topic(
                    topic_id=topic_id,
                    extra_context=extra_context,
                    use_embeddings=use_embeddings
                )

                await self.queue.complete_job(topic_id, result, result.get("success", False))

                if result.get("success"):
                    print(f"✅ Tema {topic_id} procesado correctamente")
                else:
                    print(f"⚠️ Tema {topic_id}: {result.get('error', 'Error desconocido')}")

            finally:
                db.close()

        except Exception as e:
            error_result = {"success": False, "error": str(e)}
            await self.queue.complete_job(topic_id, error_result, False)
            print(f"❌ Error procesando tema {topic_id}: {e}")


# Instancia global de la cola
job_queue = JobQueue()


# Worker global (se inicializa en main.py)
worker: Optional[ProcessingWorker] = None


async def start_worker(db_factory):
    """Inicia el worker de procesamiento"""
    global worker
    worker = ProcessingWorker(job_queue, db_factory)
    asyncio.create_task(worker.start())


async def stop_worker():
    """Detiene el worker de procesamiento"""
    global worker
    if worker:
        await worker.stop()
