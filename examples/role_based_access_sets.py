"""
Patrón: los permisos son sets de roles y funciones puras que preguntan
"¿este rol está en este set?" - una sola fuente de verdad, inyectada a
las plantillas para que la interfaz y el backend nunca se desincronicen.

Extracto representativo (renombrado y simplificado) - en el sistema real
hay 3 roles (gerencia, administrador, técnico) y varias zonas de la app
restringidas a un subconjunto de ellos. La alternativa típica -
`if rol == "gerencia" or rol == "administrador":` repetida en cada ruta y
cada template - se desincroniza con el tiempo (alguien agrega un permiso
en la ruta y se olvida de ocultar el botón correspondiente en la
plantilla, o viceversa). Acá los permisos son sets declarados una vez;
agregar un rol nuevo a un permiso es agregarlo al set, no buscar y
reemplazar por todo el código. Y como se inyectan a las plantillas vía un
"context processor" (equivalente Flask de un middleware que corre antes
de cada render), ningún template tiene que recibir el rol como parámetro
a mano - simplemente está disponible.
"""

from typing import Optional

# --- 1. Fuente única de verdad: sets, no condicionales dispersos ----------

ROLES_EDICION_EQUIPOS = {"gerencia", "administrador"}
ROLES_GESTION_USUARIOS = {"gerencia"}
ROLES_MODULOS_INTERNOS = {"gerencia", "administrador"}


def puede_editar_equipos(rol: Optional[str]) -> bool:
    return rol in ROLES_EDICION_EQUIPOS


def puede_gestionar_usuarios(rol: Optional[str]) -> bool:
    return rol in ROLES_GESTION_USUARIOS


def puede_ver_modulos_internos(rol: Optional[str]) -> bool:
    return rol in ROLES_MODULOS_INTERNOS


# --- 2. Inyección a plantillas: se resuelve una vez, no en cada vista -----

def inyectar_permisos_usuario_actual(rol_usuario_actual: Optional[str]) -> dict:
    """En el sistema real esto se registra como
    `app.context_processor(inyectar_permisos_usuario_actual)`, y Flask lo
    llama automáticamente antes de renderizar CUALQUIER plantilla - así
    un `{% if puede_editar_equipos %}` funciona en cualquier .html sin que
    la ruta que lo renderiza tenga que acordarse de pasarlo."""

    return {
        "puede_editar_equipos": puede_editar_equipos(rol_usuario_actual),
        "puede_gestionar_usuarios": puede_gestionar_usuarios(rol_usuario_actual),
        "puede_ver_modulos_internos": puede_ver_modulos_internos(rol_usuario_actual),
    }


if __name__ == "__main__":
    for rol in ("tecnico", "administrador", "gerencia", None):
        permisos = inyectar_permisos_usuario_actual(rol)
        print(f"rol={rol!r:15} -> {permisos}")
