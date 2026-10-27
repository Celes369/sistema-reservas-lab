# Especificación: Sistema de Reservas de Laboratorio

## Reglas de Negocio:
1. **Inventario:** Leer el archivo `inventario.json`.
2. **Reservas:** 
   - Una reserva debe tener: ID de unidad, solicitante (no vacío ni solo espacios), fecha/hora de inicio y fecha/hora de fin.
   - El inicio debe ser estrictamente anterior al fin.
   - **No permitir superposiciones** de reservas activas para la misma unidad.
   - **Permitir turnos consecutivos** (ej: si una reserva termina a las 11:00, otra puede arrancar a las 11:00).
   - Unidades distintas pueden reservarse en el mismo horario simultáneamente.
3. **Cancelaciones:** 
   - Una reserva cancelada conserva su identificador y datos, pero libera el horario para que vuelva a estar disponible.
4. **Persistencia:**
   - Las reservas deben guardarse en un archivo local (ej. `reservas.json`) para que no se pierdan al reiniciar la aplicación.