"""
Patrón: el reporte de cada cliente se arma leyendo un diccionario de
configuración, no ramificando el código con if/else por nombre de cliente.

Extracto representativo (renombrado y simplificado) - en el sistema real
hay ~35 clientes distintos (edificios, malls, centros de datos) y cada uno
necesita: su propio tipo de plantilla, su logo, y un puñado de banderas
que activan o desactivan secciones específicas del informe (ej. "este
edificio no tiene la cámara secundaria de refrigeración" o "este cliente
usa un sistema de limpieza automática de tubos y no lleva las tablas de
tratamiento de agua").

La alternativa obvia - un `if cliente_id == "x": ...` repetido en cada
generador de informe (PDF, Word, formulario web) - se vuelve inmanejable
apenas hay más de 5-6 clientes: cada cliente nuevo obliga a tocar 3
archivos distintos, y es fácil olvidar uno. Con esta config, agregar un
cliente es agregar una fila; el generador de informes es el mismo código
para los 35.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ClienteConfig:
    nombre: str
    tipo: str  # "edificio" | "mall" | "datacenter"
    logo: str
    # Banderas que activan/desactivan secciones del informe. El default
    # (todo True) reproduce el informe "completo" - cada cliente solo
    # declara las excepciones a esa norma.
    usa_camara_secundaria: bool = True
    usa_conductimetro: bool = True
    usa_tabla_tratamiento_agua: bool = True


# En el sistema real esto vive en config/clientes.py con ~35 entradas.
# Estos 3 alcanzan para mostrar el patrón: uno "estándar", uno con una
# excepción, y uno con dos.
CLIENTES = {
    "edificio_ejemplo_a": ClienteConfig(
        nombre="Edificio Ejemplo A", tipo="edificio", logo="logo_a.png",
    ),
    "edificio_ejemplo_b": ClienteConfig(
        nombre="Edificio Ejemplo B", tipo="edificio", logo="logo_b.png",
        usa_conductimetro=False,
    ),
    "mall_ejemplo_c": ClienteConfig(
        # Este cliente usa limpieza automática de tubos en vez de
        # tratamiento químico de agua: no tiene sentido pedirle al
        # técnico que llene tablas de un sistema que no existe en terreno.
        nombre="Mall Ejemplo C", tipo="mall", logo="logo_c.png",
        usa_tabla_tratamiento_agua=False,
    ),
}


def secciones_del_informe(cliente_id: str) -> list[str]:
    """Devuelve, en orden, las secciones que debe llevar el informe de
    este cliente. El generador de PDF/Word real solo itera esta lista -
    nunca pregunta "es este cliente en particular?"."""

    cfg = CLIENTES[cliente_id]

    secciones = ["encabezado", "tabla_equipos", "registro_visual"]

    if cfg.usa_camara_secundaria:
        secciones.append("camara_secundaria")
    if cfg.usa_conductimetro:
        secciones.append("conductimetro")
    if cfg.usa_tabla_tratamiento_agua:
        secciones.append("tratamiento_agua")

    secciones.append("firma_y_observaciones")
    return secciones


if __name__ == "__main__":
    for cliente_id in CLIENTES:
        print(f"{cliente_id}: {secciones_del_informe(cliente_id)}")

    # edificio_ejemplo_a: informe completo (todas las secciones)
    # edificio_ejemplo_b: sin "conductimetro"
    # mall_ejemplo_c: sin "tratamiento_agua"
