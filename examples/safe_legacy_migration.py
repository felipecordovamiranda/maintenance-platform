"""
Patrón: migrar datos de un formato viejo (JSON en disco) a uno nuevo
(base de datos relacional) de forma idempotente, sin romper referencias
externas que otro código ya está usando.

Extracto representativo (renombrado y simplificado) - en el sistema real
el historial de informes vivía en un archivo `historial.json` versionado
en git; se migró a una tabla SQLite que no viaja por git (cada máquina
tiene la suya). El script de migración tenía que cumplir dos cosas:
(1) ser seguro de correr más de una vez sin duplicar filas (cada máquina
- el entorno de desarrollo, el servidor de producción - corre su propia
migración una vez, y un reinicio accidental del script no debe duplicar
todo), y (2) preservar exactamente la misma forma de datos que el código
que YA lee el historial espera, para no tener que tocar ese código
consumidor a la vez que se migra el origen de los datos.
"""

import json
import sqlite3
import tempfile
import os


def crear_tabla(conexion: sqlite3.Connection):
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS historial_informes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id TEXT,
            fecha TEXT,
            archivo_pdf TEXT
        )
    """)


def migrar(conexion: sqlite3.Connection, historial_json: list[dict], forzar: bool = False) -> str:
    """Idempotente: si la tabla ya tiene filas, no hace nada salvo que se
    pase `forzar=True`. Evita duplicar datos si el script se corre dos
    veces por error (ej. reinicio accidental a mitad de un despliegue)."""

    existentes = conexion.execute("SELECT COUNT(*) FROM historial_informes").fetchone()[0]
    if existentes and not forzar:
        return f"Ya hay {existentes} fila(s), no se migra de nuevo (usa forzar=True para re-importar)."

    conexion.executemany(
        "INSERT INTO historial_informes (cliente_id, fecha, archivo_pdf) VALUES (?, ?, ?)",
        [(item["cliente_id"], item["fecha"], item["archivo_pdf"]) for item in historial_json],
    )
    conexion.commit()

    total = conexion.execute("SELECT COUNT(*) FROM historial_informes").fetchone()[0]
    return f"Migrados {len(historial_json)} informes. La tabla ahora tiene {total} fila(s)."


if __name__ == "__main__":
    historial_de_ejemplo = [
        {"cliente_id": "edificio_ejemplo_a", "fecha": "2026-07-01", "archivo_pdf": "informe_1.pdf"},
        {"cliente_id": "mall_ejemplo_c", "fecha": "2026-07-15", "archivo_pdf": "informe_2.pdf"},
    ]

    ruta_db = os.path.join(tempfile.gettempdir(), "ejemplo_migracion.db")
    if os.path.exists(ruta_db):
        os.remove(ruta_db)

    conexion = sqlite3.connect(ruta_db)
    crear_tabla(conexion)

    print(migrar(conexion, historial_de_ejemplo))
    print(migrar(conexion, historial_de_ejemplo))  # segunda corrida: no duplica
    print(migrar(conexion, historial_de_ejemplo, forzar=True))  # forzada: sí duplica

    conexion.close()
    os.remove(ruta_db)
