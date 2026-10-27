"""Lógica principal del sistema de reservas de laboratorio."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4

INVENTARIO_PATH = Path(__file__).resolve().parent / "inventario.json"


class ReservaError(Exception):
    """Error de negocio al crear una reserva."""


@dataclass(frozen=True)
class Unidad:
    id: str
    name: str


@dataclass
class Reserva:
    id: str
    unidad_id: str
    solicitante: str
    inicio: datetime
    fin: datetime
    cancelada: bool = False


class SistemaReservas:
    def __init__(self, inventario_path: Path | str | None = None) -> None:
        self._inventario_path = Path(inventario_path) if inventario_path else INVENTARIO_PATH
        self.unidades: dict[str, Unidad] = {}
        self.reservas: list[Reserva] = []
        self.cargar_inventario()

    def cargar_inventario(self) -> dict[str, Unidad]:
        if not self._inventario_path.is_file():
            raise ReservaError(f"No se encontró el inventario en {self._inventario_path}")

        with self._inventario_path.open(encoding="utf-8") as archivo:
            datos = json.load(archivo)

        unidades: dict[str, Unidad] = {}
        for item in datos:
            unidad = Unidad(id=item["id"], name=item["name"])
            unidades[unidad.id] = unidad

        self.unidades = unidades
        return self.unidades

    def crear_reserva(
        self,
        unidad_id: str,
        solicitante: str,
        inicio: datetime | str,
        fin: datetime | str,
    ) -> Reserva:
        if unidad_id not in self.unidades:
            raise ReservaError(f"La unidad '{unidad_id}' no existe en el inventario")

        nombre = (solicitante or "").strip()
        if not nombre:
            raise ReservaError("El solicitante no puede estar vacío")

        inicio_dt = self._parsear_fecha(inicio, "inicio")
        fin_dt = self._parsear_fecha(fin, "fin")

        if inicio_dt >= fin_dt:
            raise ReservaError("El inicio debe ser estrictamente anterior al fin")

        if self._hay_superposicion(unidad_id, inicio_dt, fin_dt):
            raise ReservaError(
                f"La unidad '{unidad_id}' ya tiene una reserva activa en ese horario"
            )

        reserva = Reserva(
            id=str(uuid4()),
            unidad_id=unidad_id,
            solicitante=nombre,
            inicio=inicio_dt,
            fin=fin_dt,
        )
        self.reservas.append(reserva)
        return reserva

    def _parsear_fecha(self, valor: datetime | str, campo: str) -> datetime:
        if isinstance(valor, datetime):
            return valor
        try:
            return datetime.fromisoformat(valor)
        except (TypeError, ValueError) as exc:
            raise ReservaError(f"La fecha de {campo} no es válida") from exc

    def _hay_superposicion(self, unidad_id: str, inicio: datetime, fin: datetime) -> bool:
        """Detecta solapamiento con reservas activas de la misma unidad.

        Los intervalos se tratan como [inicio, fin): dos reservas consecutivas
        (una termina cuando la otra empieza) no se consideran superpuestas.
        Unidades distintas nunca se comparan entre sí.
        """
        for reserva in self.reservas:
            if reserva.cancelada or reserva.unidad_id != unidad_id:
                continue
            if inicio < reserva.fin and reserva.inicio < fin:
                return True
        return False
