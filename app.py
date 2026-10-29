"""Interfaz web del sistema de reservas de laboratorio."""

from datetime import datetime, time

import streamlit as st

from sistema_reservas import ReservaError, SistemaReservas

st.set_page_config(page_title="Reservas de laboratorio", layout="wide")


def sistema() -> SistemaReservas:
    return SistemaReservas()


def etiqueta_unidad(sistema_reservas: SistemaReservas, unidad_id: str) -> str:
    unidad = sistema_reservas.unidades.get(unidad_id)
    if unidad is None:
        return unidad_id
    return f"{unidad.id} — {unidad.name}"


def main() -> None:
    st.title("Sistema de reservas de laboratorio")

    app = sistema()

    st.header("Inventario")
    for unidad in app.unidades.values():
        st.write(f"- **{unidad.id}**: {unidad.name}")

    st.header("Nueva reserva")
    with st.form("formulario_reserva"):
        # Mensajes de éxito o error dentro del formulario para evitar hacer scroll hacia arriba
        if "mensaje_ok" in st.session_state:
            st.success(st.session_state.pop("mensaje_ok"))
        if "mensaje_error" in st.session_state:
            st.error(st.session_state.pop("mensaje_error"))

        unidad_id = st.selectbox(
            "Unidad",
            options=list(app.unidades.keys()),
            format_func=lambda uid: etiqueta_unidad(app, uid),
        )
        solicitante = st.text_input("Solicitante")
        col_inicio, col_fin = st.columns(2)
        with col_inicio:
            fecha_inicio = st.date_input("Fecha de inicio")
            hora_inicio = st.time_input("Hora de inicio", value=time(9, 0))
        with col_fin:
            fecha_fin = st.date_input("Fecha de fin")
            hora_fin = st.time_input("Hora de fin", value=time(11, 0))
        crear = st.form_submit_button("Crear reserva")

    if crear:
        inicio = datetime.combine(fecha_inicio, hora_inicio)
        fin = datetime.combine(fecha_fin, hora_fin)
        try:
            reserva = app.crear_reserva(unidad_id, solicitante, inicio, fin)
            st.session_state["mensaje_ok"] = f"Reserva creada correctamente (id: {reserva.id})."
        except ReservaError as exc:
            st.session_state["mensaje_error"] = str(exc)
        st.rerun()

    st.header("Reservas")
    if not app.reservas:
        st.info("No hay reservas registradas.")
        return

    for reserva in app.reservas:
        estado = "Cancelada" if reserva.cancelada else "Activa"
        columnas = st.columns([2, 2, 2, 2, 1, 1])
        columnas[0].write(etiqueta_unidad(app, reserva.unidad_id))
        columnas[1].write(reserva.solicitante)
        columnas[2].write(reserva.inicio.strftime("%Y-%m-%d %H:%M"))
        columnas[3].write(reserva.fin.strftime("%Y-%m-%d %H:%M"))
        columnas[4].write(estado)
        if reserva.cancelada:
            columnas[5].write("—")
            continue
        if columnas[5].button("Cancelar", key=f"cancelar_{reserva.id}"):
            try:
                app.cancelar_reserva(reserva.id)
                st.session_state["mensaje_ok"] = "Reserva cancelada. El horario quedó disponible."
            except ReservaError as exc:
                st.session_state["mensaje_error"] = str(exc)
            st.rerun()


if __name__ == "__main__":
    main()