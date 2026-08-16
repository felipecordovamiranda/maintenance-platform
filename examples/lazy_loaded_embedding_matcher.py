"""
Patrón: un modelo de ML pesado se carga UNA sola vez, la primera vez que
de verdad se necesita - no al arrancar la aplicación.

Extracto representativo (renombrado y simplificado) - en el sistema real
esto carga un modelo CLIP (vía sentence-transformers) para encontrar,
entre un set de imágenes de referencia, cuál corresponde mejor a una foto
subida por un técnico. El modelo y sus dependencias (torch incluido)
tardan varios segundos en cargar y ocupan memoria de forma permanente.
Si se cargaran al importar el módulo, cada arranque de la aplicación
(incluyendo reinicios frecuentes en desarrollo) pagaría ese costo aunque
nadie use la función esa sesión. Con carga perezosa + cache en un dict de
módulo, el costo se paga una sola vez, y solo si la función se usa.

Este ejemplo no depende de sentence-transformers/torch para poder
correr solo: el "cargador" real se inyecta como parámetro (una función),
así se ve el patrón de lazy-loading + cache aislado del modelo concreto.
"""

from typing import Callable


class BuscadorConCache:
    """Envuelve cualquier "cargador" costoso (en el sistema real: cargar
    CLIP + los embeddings de referencia desde disco) para que se ejecute
    como máximo una vez."""

    def __init__(self, cargador: Callable[[], object]):
        self._cargador = cargador
        self._instancia = None
        self._veces_cargado = 0

    def _asegurar_cargado(self):
        if self._instancia is None:
            self._instancia = self._cargador()
            self._veces_cargado += 1

    def buscar(self, consulta: str) -> str:
        self._asegurar_cargado()
        modelo = self._instancia
        return modelo["descripciones"].get(consulta, "sin coincidencia")


def cargador_costoso_de_ejemplo() -> dict:
    """Simula lo que en el sistema real es `SentenceTransformer('clip-ViT-B-32')`
    + cargar embeddings.npy - una operación cara que solo debe pasar una vez."""

    print("[cargando modelo pesado... esto solo debería imprimirse UNA vez]")
    return {"descripciones": {"foto_chiller": "Vista frontal del chiller", "foto_torre": "Torre de enfriamiento"}}


if __name__ == "__main__":
    buscador = BuscadorConCache(cargador_costoso_de_ejemplo)

    print(buscador.buscar("foto_chiller"))
    print(buscador.buscar("foto_torre"))
    print(buscador.buscar("foto_chiller"))  # ya cacheado, no vuelve a "cargar"

    print(f"\nEl cargador costoso se ejecutó {buscador._veces_cargado} vez(es) "
          f"para {3} búsquedas.")
