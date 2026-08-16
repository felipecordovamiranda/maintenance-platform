"""
Patrón: la duración de la cookie de sesión no es un número arbitrario -
responde a una falla real observada en producción con la app instalada
como PWA en Android.

Contexto real: la app se puede instalar como Progressive Web App en el
celular. Android, para ahorrar batería/memoria, puede matar el proceso de
una PWA que está en segundo plano en cualquier momento (ej. mientras el
celular pasa de mano en mano en terreno para que técnico, cliente y
supervisor firmen un mismo documento). Si la cookie de sesión es una
"cookie de sesión pura" (sin `Expires`/`Max-Age` explícito), el navegador
la trata como más desechable y es más probable que se pierda al matar el
proceso - cerrando la sesión de golpe a mitad de un flujo de firma, sin
que el usuario haya pedido salir. La solución de Flask es marcar la
sesión como "permanente" con una duración explícita (7 días, no
indefinida) - eso hace que la cookie SÍ lleve expiración real y sobreviva
al ciclo de vida de la PWA.

Este ejemplo simula ambos tipos de cookie con un dict + reloj falso (sin
Flask), para mostrar la diferencia sin depender de un framework.
"""

from datetime import datetime, timedelta


class Cookie:
    def __init__(self, valor: str, expira_en: datetime | None):
        self.valor = valor
        self.expira_en = expira_en  # None == "cookie de sesión pura"

    def sigue_valida(self, ahora: datetime, proceso_fue_matado: bool) -> bool:
        if self.expira_en is None:
            # Sin expiración explícita: el navegador es libre de
            # descartarla apenas mata el proceso en segundo plano.
            return not proceso_fue_matado

        return ahora < self.expira_en


def iniciar_sesion(permanente: bool, ahora: datetime) -> Cookie:
    if not permanente:
        return Cookie("token_de_sesion", expira_en=None)

    # PERMANENT_SESSION_LIFETIME real: 7 días, no "para siempre" - un
    # balance entre "no obligar a re-loguearse a cada rato" y no dejar
    # sesiones vivas indefinidamente en un celular perdido o compartido.
    return Cookie("token_de_sesion", expira_en=ahora + timedelta(days=7))


if __name__ == "__main__":
    ahora = datetime(2026, 8, 16, 10, 0)

    sesion_normal = iniciar_sesion(permanente=False, ahora=ahora)
    sesion_permanente = iniciar_sesion(permanente=True, ahora=ahora)

    # Simula: Android mata el proceso de la PWA a mitad de un flujo de firma.
    print("Proceso de la PWA muere en segundo plano...")
    print("Sesión normal   sigue viva?", sesion_normal.sigue_valida(ahora, proceso_fue_matado=True))
    print("Sesión permanente sigue viva?", sesion_permanente.sigue_valida(ahora, proceso_fue_matado=True))

    # Simula: pasan 8 días - incluso la permanente debe caducar.
    ocho_dias_despues = ahora + timedelta(days=8)
    print("\n8 días después, sesión permanente sigue viva?",
          sesion_permanente.sigue_valida(ocho_dias_despues, proceso_fue_matado=False))
