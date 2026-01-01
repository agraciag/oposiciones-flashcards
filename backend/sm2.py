"""
Algoritmo SuperMemo 2 (SM-2) para repetición espaciada

Basado en el algoritmo original de Piotr Wozniak (1987)
https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
"""

from typing import Dict


def calculate_sm2(
    quality: int,
    repetitions: int,
    easiness: float,
    interval: int
) -> Dict[str, float | int]:
    """
    Calcula el siguiente intervalo usando SuperMemo 2

    Args:
        quality: Calidad de la respuesta (0-5)
            0 = Complete blackout
            1 = Incorrect, but familiar
            2 = Incorrect, but seemed easy
            3 = Correct, but difficult
            4 = Correct, hesitation
            5 = Perfect response

        repetitions: Número de repeticiones correctas consecutivas
        easiness: Factor de facilidad (E-Factor, default 2.5)
        interval: Intervalo actual en días

    Returns:
        Dict con nuevos valores de repetitions, easiness, interval
    """

    # Si la calidad es menor a 3, resetear repeticiones
    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        # Primera repetición: 1 día
        if repetitions == 0:
            interval = 1
        # Segunda repetición: 6 días
        elif repetitions == 1:
            interval = 6
        # Siguientes: multiplicar por easiness factor
        else:
            interval = round(interval * easiness)

        repetitions += 1

    # Actualizar easiness factor
    # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    easiness = easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

    # Easiness factor mínimo de 1.3
    if easiness < 1.3:
        easiness = 1.3

    return {
        'repetitions': repetitions,
        'easiness': round(easiness, 2),
        'interval': interval
    }


def quality_to_sm2_value(quality_label: str) -> int:
    """
    Convierte etiquetas de calidad a valores SM-2

    Args:
        quality_label: 'again', 'hard', 'good', 'easy'

    Returns:
        Valor numérico para SM-2 (0-5)
    """
    mapping = {
        'again': 0,  # No la sabía
        'hard': 2,   # Difícil
        'good': 3,   # Bien
        'easy': 4    # Fácil
    }

    return mapping.get(quality_label.lower(), 3)


# Ejemplo de uso
if __name__ == "__main__":
    print("🧠 Algoritmo SM-2 - Ejemplo")
    print("=" * 50)

    # Tarjeta nueva
    rep = 0
    ef = 2.5
    interval = 0

    # Simulación de estudio
    reviews = [
        ('good', 3),   # Día 0: Bien
        ('good', 3),   # Día 1: Bien
        ('hard', 2),   # Día 6: Difícil
        ('good', 3),   # Día 7: Bien
        ('easy', 4),   # Día 13: Fácil
    ]

    for i, (label, quality) in enumerate(reviews):
        print(f"\nReview {i+1}: {label.upper()}")
        print(f"  Antes: reps={rep}, ef={ef:.2f}, intervalo={interval} días")

        result = calculate_sm2(quality, rep, ef, interval)

        rep = result['repetitions']
        ef = result['easiness']
        interval = result['interval']

        print(f"  Después: reps={rep}, ef={ef:.2f}, intervalo={interval} días")
        print(f"  ➡️ Próximo repaso en {interval} días")

    print("\n" + "=" * 50)
    print(f"Estado final: La verás de nuevo en {interval} días")
