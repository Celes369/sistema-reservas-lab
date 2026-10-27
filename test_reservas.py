"""Pruebas automáticas del sistema de reservas de laboratorio."""

from datetime import datetime
from pathlib import Path

import pytest

from sistema_reservas import ReservaError, SistemaReservas

INICIO = "2026-10-27T09:00:00"
FIN = "2026-10-27T11:00:00"


@pytest.fixture
def sistema(tmp_path: Path) -> SistemaReservas:
    return SistemaReservas(reservas_path=tmp_path / "reservas.json")


def test_creacion_valida_de_reserva(sistema: SistemaReservas) -> None:
    reserva = sistema.crear_reserva("MIC-01", "Ana Pérez", INICIO, FIN)

    assert reserva.id
    assert reserva.unidad_id == "MIC-01"
    assert reserva.solicitante == "Ana Pérez"
    assert reserva.inicio == datetime.fromisoformat(INICIO)
    assert reserva.fin == datetime.fromisoformat(FIN)
    assert reserva.cancelada is False
    assert reserva in sistema.reservas


def test_rechaza_superposicion_misma_unidad(sistema: SistemaReservas) -> None:
    sistema.crear_reserva("MIC-01", "Ana", INICIO, FIN)

    with pytest.raises(ReservaError, match="reserva activa"):
        sistema.crear_reserva("MIC-01", "Bruno", "2026-10-27T10:00:00", "2026-10-27T12:00:00")


def test_permite_turnos_consecutivos(sistema: SistemaReservas) -> None:
    primera = sistema.crear_reserva("MIC-01", "Ana", INICIO, FIN)
    segunda = sistema.crear_reserva("MIC-01", "Bruno", FIN, "2026-10-27T13:00:00")

    assert primera.fin == segunda.inicio
    assert len(sistema.reservas) == 2


def test_permite_reservas_simultaneas_en_unidades_distintas(sistema: SistemaReservas) -> None:
    microscopio = sistema.crear_reserva("MIC-01", "Ana", INICIO, FIN)
    osciloscopio = sistema.crear_reserva("OSC-01", "Bruno", INICIO, FIN)

    assert microscopio.unidad_id != osciloscopio.unidad_id
    assert microscopio.inicio == osciloscopio.inicio
    assert microscopio.fin == osciloscopio.fin


@pytest.mark.parametrize(
    "solicitante,inicio,fin",
    [
        ("", INICIO, FIN),
        ("   ", INICIO, FIN),
        ("Ana", FIN, INICIO),
        ("Ana", INICIO, INICIO),
        ("Ana", "fecha-invalida", FIN),
        ("Ana", INICIO, "no-es-una-fecha"),
    ],
)
def test_rechaza_entradas_invalidas(
    sistema: SistemaReservas,
    solicitante: str,
    inicio: str,
    fin: str,
) -> None:
    with pytest.raises(ReservaError):
        sistema.crear_reserva("MIC-01", solicitante, inicio, fin)


def test_cancelacion_conserva_registro_y_libera_horario(sistema: SistemaReservas) -> None:
    original = sistema.crear_reserva("MIC-01", "Ana", INICIO, FIN)

    cancelada = sistema.cancelar_reserva(original.id)

    assert cancelada.id == original.id
    assert cancelada.unidad_id == original.unidad_id
    assert cancelada.solicitante == original.solicitante
    assert cancelada.inicio == original.inicio
    assert cancelada.fin == original.fin
    assert cancelada.cancelada is True
    assert original in sistema.reservas

    nueva = sistema.crear_reserva("MIC-01", "Bruno", INICIO, FIN)
    assert nueva.cancelada is False
    assert nueva.id != original.id
    assert len(sistema.reservas) == 2


def test_persistencia_al_reinstanciar_sistema(tmp_path: Path) -> None:
    archivo = tmp_path / "reservas.json"
    original = SistemaReservas(reservas_path=archivo)
    reserva = original.crear_reserva("MIC-01", "Ana Pérez", INICIO, FIN)

    recargado = SistemaReservas(reservas_path=archivo)

    assert len(recargado.reservas) == 1
    recuperada = recargado.reservas[0]
    assert recuperada.id == reserva.id
    assert recuperada.unidad_id == reserva.unidad_id
    assert recuperada.solicitante == reserva.solicitante
    assert recuperada.inicio == reserva.inicio
    assert recuperada.fin == reserva.fin
    assert recuperada.cancelada is False
