"""
Patrón: la misma función de "leer una medición del PLC" funciona sobre
dos transportes físicos distintos (red y puerto serie), porque el
transporte se inyecta como dependencia en vez de estar hardcodeado.

Extracto representativo (renombrado y simplificado) - en el sistema real
hay equipos monitoreados por PLC de dos formas: algunos por Modbus TCP
(un gateway en la red, vía `pymodbus`) y otros por Modbus RTU directo
sobre puerto serie (vía `minimalmodbus`). Son protocolos de transporte distintos con el mismo
modelo de datos por encima (registros Modbus). Son implementaciones
reales pero deliberadamente delgadas - sin reconexión automática ni
manejo de errores robusto todavía, algo a tener en cuenta si se usan como
base para algo en producción.

Este ejemplo no depende de pymodbus/minimalmodbus instalados: se define
una interfaz mínima de "transporte" con dos implementaciones falsas
(en memoria) para poder correr sin hardware ni librerías de más. En el
sistema real, la implementación de `LectorTCP`/`LectorSerial` usa
`ModbusTcpClient`/`minimalmodbus.Instrument` en vez del diccionario falso
de acá.
"""

from typing import Protocol


class TransporteModbus(Protocol):
    def leer_registro(self, direccion: int) -> float: ...


class LectorTCP:
    """En el sistema real: pymodbus.client.ModbusTcpClient contra un
    gateway de red que expone el PLC vía Modbus TCP."""

    def __init__(self, host: str, puerto: int, registros_simulados: dict[int, float]):
        self.host, self.puerto = host, puerto
        self._registros = registros_simulados

    def leer_registro(self, direccion: int) -> float:
        return self._registros[direccion]


class LectorSerial:
    """En el sistema real: minimalmodbus.Instrument sobre un puerto COM,
    hablando Modbus RTU directo con el PLC (sin pasar por red)."""

    def __init__(self, puerto_com: str, registros_simulados: dict[int, float]):
        self.puerto_com = puerto_com
        self._registros = registros_simulados

    def leer_registro(self, direccion: int) -> float:
        return self._registros[direccion]


DIRECCION_PRESION_CONDENSADOR = 40001
DIRECCION_TEMPERATURA_EVAPORADOR = 40002


def leer_medicion(transporte: TransporteModbus, direccion: int) -> float:
    """El código que consume una medición no sabe ni le importa si el PLC
    está en la red o en un puerto serie - solo pide un `TransporteModbus`."""

    return transporte.leer_registro(direccion)


if __name__ == "__main__":
    lector_tcp = LectorTCP(
        host="10.0.0.50", puerto=502,
        registros_simulados={DIRECCION_PRESION_CONDENSADOR: 6.4},
    )
    lector_serial = LectorSerial(
        puerto_com="COM3",
        registros_simulados={DIRECCION_TEMPERATURA_EVAPORADOR: 4.8},
    )

    print("Presión condensador (vía TCP):", leer_medicion(lector_tcp, DIRECCION_PRESION_CONDENSADOR), "bar")
    print("Temp. evaporador (vía serie):", leer_medicion(lector_serial, DIRECCION_TEMPERATURA_EVAPORADOR), "°C")
