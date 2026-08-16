"""
Patrón: el borrador de IA no "alucina" el informe desde cero - se ancla al
texto de informes anteriores del mismo cliente, y los datos crudos del
formulario se normalizan antes de armar el prompt porque no todos los
formularios del sistema usan los mismos nombres de campo.

Extracto representativo (renombrado y simplificado) - en el sistema real
hay 4 variantes de formulario (una app hereda clientes con estructuras
de datos distintas, según el tipo de instalación), y el asistente de IA
que redacta un borrador de "Observaciones" necesita dos cosas antes de
poder llamar al LLM: (1) los campos ya en un formato único, sin importar
de qué formulario vinieron, y (2) contexto real - un resumen de los
últimos informes de ESE cliente, para que el borrador hable del mismo
equipo con el mismo criterio que un técnico humano lo haría, no en
abstracto. Es "RAG casero": no hay embeddings ni vector search, es
extracción de texto plano de PDFs anteriores más límite de tamaño, pero
resuelve el mismo problema (evitar que el modelo responda sin contexto).
"""


# --- 1. Normalización: 4 formularios, 1 forma interna ----------------------

# Cada tipo de formulario en el sistema real nombra sus campos distinto
# (arrastre histórico de cuando cada uno se armó por separado). Antes de
# construir el prompt, todo pasa por acá.
MAPEOS_POR_TIPO_FORMULARIO = {
    "tipo_a": {"temp_entrada": "temperatura_entrada", "temp_salida": "temperatura_salida"},
    "tipo_b": {"t_in": "temperatura_entrada", "t_out": "temperatura_salida"},
    "tipo_c": {"entrada_temp": "temperatura_entrada", "salida_temp": "temperatura_salida"},
    "tipo_d": {"temperatura_entrada": "temperatura_entrada", "temperatura_salida": "temperatura_salida"},
}


def normalizar_campos(tipo_formulario: str, datos_crudos: dict) -> dict:
    mapeo = MAPEOS_POR_TIPO_FORMULARIO[tipo_formulario]
    return {
        nombre_interno: datos_crudos[nombre_original]
        for nombre_original, nombre_interno in mapeo.items()
        if nombre_original in datos_crudos
    }


# --- 2. Contexto: extraer y recortar texto de informes anteriores ---------

LIMITE_CARACTERES_CONTEXTO = 4000


def construir_contexto_historial(textos_informes_previos: list[str]) -> str:
    """Concatena los informes anteriores del cliente (más reciente primero)
    hasta un límite de caracteres, para no exceder la ventana de contexto
    del modelo ni pagar tokens de más. Es deliberadamente simple - no hay
    embeddings, solo texto plano con un tope de tamaño."""

    contexto = ""
    for texto in textos_informes_previos:
        if len(contexto) + len(texto) > LIMITE_CARACTERES_CONTEXTO:
            break
        contexto += texto + "\n---\n"

    return contexto.strip()


# --- 3. Prompt final: datos normalizados + contexto real -------------------

def construir_prompt_borrador(campos: dict, contexto_historial: str) -> str:
    return (
        "Redacta observaciones técnicas breves para este mantenimiento, "
        "en el mismo tono que los informes anteriores de este cliente.\n\n"
        f"Mediciones actuales: entrada {campos['temperatura_entrada']}°C, "
        f"salida {campos['temperatura_salida']}°C.\n\n"
        f"Informes anteriores del cliente (contexto):\n{contexto_historial or '(sin historial previo)'}"
    )


if __name__ == "__main__":
    datos_crudos_tipo_b = {"t_in": 7.1, "t_out": 12.4}
    campos = normalizar_campos("tipo_b", datos_crudos_tipo_b)
    print("Campos normalizados:", campos)

    historial = [
        "Visita 2026-07: Chiller 1 operando normal, presión estable.",
        "Visita 2026-06: se detectó vibración leve en Torre 2, se recomendó monitoreo.",
    ]
    contexto = construir_contexto_historial(historial)

    prompt = construir_prompt_borrador(campos, contexto)
    print("\n--- Prompt que se enviaría al LLM ---")
    print(prompt)
