# Centinela: Auditoría Inteligente de Huella Digital

Proyecto de curso **PTIA** – Grupo 02 – Sebastián Granados.

Centinela actúa como un "investigador digital": revisa las fuentes que el usuario elige, arma un **expediente de caso** con línea de tiempo, calcula un **puntaje de exposición (0–100)** y explica el riesgo con recomendaciones.

## Flujo (basado en el prototipo de Figma)

| Vista | Qué hace |
|---|---|
| Consulta | El usuario escribe qué quiere revisar y elige las fuentes: correos (breaches), fotos con GPS, actividad de la cuenta, actividad bancaria y permisos de apps. |
| Caso | Línea de tiempo de hallazgos (más reciente primero) y detalle de cada uno con la validación **¿Fuiste tú?** |
| Riesgo | Puntaje, conteo por tipo de riesgo, diagnóstico del agente, recomendaciones y descarga del expediente. |

## Arquitectura

| Capa | Archivo | Rol |
|---|---|---|
| Interfaz | `src/main.py` | Streamlit, tres vistas y validación interactiva. |
| Fuentes | `src/connector.py` | Filtraciones (base local o API de Have I Been Pwned), EXIF/GPS real de fotos, actividad y permisos (demo o JSON propio). |
| Conocimiento | `src/engine.py` | Reglas y umbrales: ciudad habitual, horario, gasto atípico (> 3× la mediana), permisos sensibles sin uso (≥ 30 días), pesos por severidad y puntaje. |
| Razonamiento | `src/llm.py` | LLM (OpenAI) que redacta diagnóstico y recomendaciones; si no hay API key usa reglas. |

## Ejecución

```
pip install -r requirements.txt
streamlit run src/main.py
```

Opcional: copiar `.env.example` a `.env` y poner `OPENAI_API_KEY` (diagnóstico con LLM) y `HIBP_API_KEY` (filtraciones reales). Sin ellas funciona con datos demo y reglas.

Pruebas: `python -m unittest discover -s tests`

## Despliegue en Azure

App publicada: https://centinela-sebastiangranados.azurewebsites.net (App Service Linux, plan F1 gratis, grupo `rg-centinela`, North Central US).

La app se configuró con WebSockets activos (Streamlit los necesita) y este comando de inicio:

```
python -m streamlit run src/main.py --server.port 8000 --server.address 0.0.0.0 --server.headless true
```

Para publicar una versión nueva se sube un .zip con `src/`, `data/`, `.streamlit/` y `requirements.txt`:

```
az webapp deploy --name centinela-sebastiangranados --resource-group rg-centinela --src-path centinela.zip --type zip
```

## Datos demo

Están en `data/` (correo demo: `usuario@example.com`). Con todas las fuentes por defecto el caso da **62/100 – Expuesto**: 1 filtración, 1 acceso no habitual (Bogotá vs. Cali), 3 fotos con GPS y 2 permisos a revisar.
