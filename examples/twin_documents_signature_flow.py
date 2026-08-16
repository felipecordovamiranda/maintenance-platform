"""
Patrón: dos documentos que nacen de una misma visita (una hoja de
servicio firmada y su registro de horas trabajadas) comparten folio, para
que quede explícito que describen el mismo trabajo - y el documento no se
puede cerrar sin las firmas que le corresponden.

Extracto representativo (renombrado y simplificado) - en el sistema real
cada visita en terreno genera una "Hoja de Servicio" (folio `HS-2026-0042`)
y, si corresponde, una "Hoja de Horas" asociada. En vez de dos folios
independientes que hay que vincular a mano (y que se pueden desincronizar
si alguien borra o edita uno de los dos), la Hoja de Horas deriva su folio
del de la Hoja de Servicio, cambiando solo el prefijo: `HH-2026-0042`. Con
solo mirar el folio se sabe que ambos documentos son la misma visita, sin
necesitar una tabla de relaciones aparte. El flujo de firma real exige
hasta 3 firmas (técnico y cliente siempre, supervisor cuando corresponde)
antes de dar el documento por cerrado.
"""

from datetime import datetime


def generar_folio(folios_existentes: list[str], anio: int) -> str:
    """Folio correlativo por año: HS-{año}-{consecutivo con 4 dígitos}."""

    prefijo = f"HS-{anio}-"
    cantidad_del_anio = sum(1 for f in folios_existentes if f.startswith(prefijo))
    siguiente = cantidad_del_anio + 1
    return f"{prefijo}{siguiente:04d}"


def folio_horas_de(folio_hoja_servicio: str) -> str:
    """El folio de la Hoja de Horas es el MISMO número que el de la Hoja
    de Servicio que la originó - solo cambia el prefijo HS por HH, para
    dejar explícito que ambos documentos corresponden al mismo trabajo,
    sin necesitar una tabla de relaciones aparte."""

    _, resto = folio_hoja_servicio.split("-", 1)
    return f"HH-{resto}"


FIRMAS_REQUERIDAS = {"tecnico", "cliente"}  # "supervisor" es opcional


def documento_listo_para_cerrar(firmas_presentes: set[str]) -> bool:
    """No se puede dar por cerrado un documento sin las firmas mínimas -
    aunque ya tenga folio asignado y todos los demás campos llenos."""

    return FIRMAS_REQUERIDAS.issubset(firmas_presentes)


if __name__ == "__main__":
    folios_2026 = ["HS-2026-0001", "HS-2026-0002"]

    nuevo_folio = generar_folio(folios_2026, anio=2026)
    folio_horas = folio_horas_de(nuevo_folio)
    print(f"Hoja de Servicio: {nuevo_folio}")
    print(f"Hoja de Horas asociada: {folio_horas}")

    firmas = {"tecnico"}
    print(f"\n¿Lista para cerrar con solo firma de técnico? {documento_listo_para_cerrar(firmas)}")
    firmas.add("cliente")
    print(f"¿Lista para cerrar con técnico + cliente? {documento_listo_para_cerrar(firmas)}")
