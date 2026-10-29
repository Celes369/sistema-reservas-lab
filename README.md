# Sistema-reservas-lab

## # Sistema de Reservas de Laboratorio con Agentes

## 1. Especificación breve

* **Problema:** La coordinación de un laboratorio registraba pedidos manualmente en mensajes y planillas, lo que generaba superposiciones de turnos para una misma unidad y bloqueos incorrectos tras cancelaciones.
* **Alcance:** Sistema local para consultar disponibilidad, crear reservas y cancelar unidades físicas del inventario, persistiendo el estado entre reinicios.
* **Reglas de negocio y supuestos:**
  * Unidades conocidas: `MIC-01`, `MIC-02`, `OSC-01`, `MUL-01`, `FUE-01`.
  * Una reserva activa ocupa el intervalo; una cancelada libera el horario.
  * El solicitante no puede estar vacío ni compuesto solo por espacios.
  * El inicio debe ser estrictamente anterior al fin.
  * Se rechazan superposiciones de reservas activas para la misma unidad, pero se permiten turnos consecutivos (ej. una termina a las 11:00 y otra empieza a las 11:00) y reservas simultáneas de unidades distintas.

## 2. Solución

* **Estructura técnica:** Desarrollado en Python utilizando `dataclasses`, gestión de excepciones de negocio y almacenamiento local en formato JSON `reservas.json` e `inventario.json`)[cite: 2].
* **Requisitos previos:** Python 3.x y la librería de pruebas `pytest`.
* **Instalación y ejecución de pruebas:**
  1. Instalar dependencias: `python -m pip install pytest`
  2. Ejecutar la suite de pruebas automáticas: `python -m pytest`
* **Persistencia:** Los datos de reservas se guardan automáticamente en `reservas.json` y se recargan al reiniciar la aplicación.

## 3. Preparación del agente

* **Entorno y modelo:** Entorno de desarrollo **Cursor** utilizando un modelo avanzado de lenguaje Cursor Grok 4.6 médium como *harness* de programación.
* **Instrucciones y contexto:** Se suministró un archivo de especificaciones `especificacion.md`) y el archivo de inventario inicial `inventario.json`), estableciendo restricciones estrictas sobre superposiciones, manejo de fechas ISO y persistencia local.
* **Controles humanos:** Supervisión directa del código generado, iteración por módulos y ejecución manual de pruebas de integración y validación.

## 4. Registro de decisiones y delegación (Episodios)

### Episodio 1: Lógica principal y validaciones

* **Objetivo y contexto:** Desarrollar la estructura base en Python para cargar el inventario, validar solicitantes y aplicar la lógica de intervalos semiabiertos para evitar superposiciones permitiendo turnos consecutivos.
* **Acción del agente:** Creación del archivo `sistema_reservas.py` con las clases `Unidad`, `Reserva` y `SistemaReservas`, implementando el método de detección de solapamiento.
* **Revisión humana:** Aceptado tras verificar que la validación de intervalos `inicio < reserva.fin and reserva.inicio < fin`) maneja correctamente los límites consecutivos.
* **Evidencia:** Commit inicial de la lógica principal en el repositorio.

### Episodio 2: Persistencia local y cancelación

* **Objetivo y contexto:** Incorporar el almacenamiento persistente en archivos JSON para que las reservas no se pierdan al reiniciar, y añadir la funcionalidad de cancelación que libera el horario pero conserva el registro.
* **Acción del agente:** Incorporación de los métodos `guardar_reservas`, `cargar_reservas` y `cancelar_reserva` utilizando cadenas en formato ISO para las fechas.
* **Revisión humana:** Validación de que al reiniciar la instancia del sistema las reservas se cargan correctamente desde el archivo físico.
* **Evidencia:** Commit correspondiente a la persistencia y gestión de estados.

### Episodio 3: Pruebas automáticas y verificación

* **Objetivo y contexto:** Escribir una suite completa de pruebas automáticas utilizando `pytest` para certificar el cumplimiento de todas las reglas del negocio.
* **Acción del agente:** Generación del archivo `test_reservas.py` cubriendo 12 escenarios de prueba (creación válida, rechazo de solapamientos, turnos consecutivos, unidades simultáneas, entradas inválidas, cancelación y persistencia).
* **Revisión humana:** Ejecución exitosa de la suite mediante `python -m pytest` comprobando el 100 de aciertos `12 passed`).
* **Evidencia:** Archivo `test_reservas.py` y salida de ejecución satisfactoria.
* **Interfaz Web opcional:** Se incluyó una aplicación interactiva desarrollada en Streamlit `app.py`) para gestionar las reservas visualmente mediante un navegador web.
* **Ejecución de la interfaz web:**
  1. Instalar Streamlit: `python -m pip install streamlit`
  2. Ejecutar la aplicación: `streamlit run app.py`