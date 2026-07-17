# Guía Docente — Resiliencia Valle Norte (Brigadas y BCP)

## Despliegue
1. Repositorio de GitHub separado del simulador de crisis/comunicación (son dos apps
   independientes con su propio `requirements.txt`).
2. Streamlit Community Cloud → New app → main file `app.py`.
3. Un solo enlace por equipo; recomendamos que cada equipo abra la app **en una sola
   pantalla compartida** durante su sala de trabajo (breakout room), ya que el diseño
   asume decisión colectiva en tiempo real, no respuestas individuales simultáneas.

## Por qué está diseñado así (para tu debrief)
- **Dependencia entre módulos**: el número de brigadistas contra incendios que el
  equipo asigna en el Módulo 1 determina la capacidad de respuesta disponible en el
  Módulo 2 (si asignan menos de 4, el sistema limita el puntaje máximo a 70 y lo anuncia
  explícitamente). Esto obliga a que las decisiones tempranas se sientan como
  decisiones reales con consecuencias, no pasos aislados — ideal para discutir el
  concepto de "deuda de preparación" en el debrief.
- **No hay una única cifra "correcta" de dimensionamiento de brigada**: se pide al
  equipo justificar su criterio por escrito. Esto es intencional: la norma peruana
  (Ley 29783 y su reglamento) no fija una ratio universal, así que el ejercicio evalúa
  la calidad del razonamiento, no solo el número.
- **La tabla NFPA 704 y la tabla de radios de aislamiento son simplificaciones
  pedagógicas**, explícitamente marcadas como tales en la interfaz — no sustituyen al
  ERG oficial. Puedes usar esto para introducir la diferencia entre herramientas de
  aula y herramientas operativas reales.
- **El BIA del Módulo 3 verifica automáticamente coherencia RTO vs. MTPD** por
  proceso: si un proceso de criticidad alta queda con RTO mayor a su MTPD, el sistema
  lo marca como "brecha crítica" en el resultado — útil para explicar visualmente qué
  es una brecha de continuidad real.

## Estructura de tiempos (40 min por módulo + cierre)
| Bloque | Actividad | Duración sugerida |
|---|---|---|
| Módulo 1 | Brigadas: dimensionamiento y asignación | 40 min |
| Módulo 2 | MATPEL: EPP, zonas, contención, causa raíz | 40 min |
| Módulo 3 | BCP: BIA y estrategias de recuperación | 40 min |
| Cierre | Índice de Resiliencia + informe ejecutivo | 15-20 min |

## Panel Docente
- Contraseña por defecto: `Resiliencia2026` (cámbiala en `INSTRUCTOR_PASSWORD` antes
  de publicar).
- Muestra el Índice de Resiliencia por equipo, ranking, y permite exportar el CSV con
  las conclusiones ejecutivas completas de cada equipo — útil como insumo directo de
  calificación cualitativa.

## Ideas de extensión
- Puedes variar la sustancia del Módulo 2 (cambiar el escenario de ácido sulfúrico por
  un solvente inflamable) ajustando el diccionario `esperado` del rombo NFPA y el radio
  de referencia, para usar distintas versiones con distintos equipos y evitar que se
  compartan respuestas.
- Puedes ajustar `PRESUPUESTO_HORAS` y los costos de estrategias de BCP para calibrar
  la dificultad según el nivel del cohorte.
- Si quieres una versión donde cada integrante del equipo tenga su propio rol de login
  (coordinador de brigadas / especialista MATPEL / analista BCP) con vistas separadas,
  puedo construir una segunda versión con control de acceso por rol.
