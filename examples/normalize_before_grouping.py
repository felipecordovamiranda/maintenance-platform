"""
Patrón: antes de agrupar/contar por una columna de texto libre, normalizar
el valor - si no, variantes de formato de la misma persona/entidad
cuentan como entidades distintas.

Extracto representativo (renombrado y simplificado) - en el sistema real
el nombre del técnico responsable de cada informe se escribió, con los
años, de formas distintas ("JUAN PEREZ ROJAS", "Juan perez Rojas",
"Juan Perez  Rojas" con doble espacio) - texto libre cargado por
distintas personas en distintos momentos, no un campo con selector fijo.
Un dashboard que cuenta "informes por técnico" agrupando directo por ese
texto crudo mostraría a la misma persona como 3 técnicos distintos.
Colapsar espacios + normalizar mayúsculas ANTES de agrupar es una línea
de código que evita ese conteo silenciosamente equivocado.
"""

from collections import Counter


def normalizar_nombre(nombre: str) -> str:
    """Colapsa espacios repetidos y pasa a Title Case, para que
    variantes de mayúsculas/espaciado cuenten como la misma persona."""

    limpio = " ".join((nombre or "").split())
    return limpio.title()


def contar_informes_por_tecnico(nombres_crudos: list[str]) -> Counter:
    return Counter(normalizar_nombre(n) for n in nombres_crudos)


if __name__ == "__main__":
    nombres_crudos = [
        "JUAN PEREZ ROJAS",
        "Juan perez Rojas",
        "Juan Perez  Rojas",  # doble espacio
        "Maria Jose Soto",
        "MARIA JOSE SOTO",
    ]

    sin_normalizar = Counter(nombres_crudos)
    print("Sin normalizar (INCORRECTO):", dict(sin_normalizar))
    print("  -> parece que hay", len(sin_normalizar), "técnicos distintos")

    normalizado = contar_informes_por_tecnico(nombres_crudos)
    print("\nNormalizado (correcto):", dict(normalizado))
    print("  ->", len(normalizado), "técnicos reales")
