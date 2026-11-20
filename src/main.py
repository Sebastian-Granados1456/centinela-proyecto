"""Interfaz de Centinela como app móvil simulada: Consulta -> Caso -> Riesgo."""

import random
import time

import streamlit as st
from dotenv import load_dotenv

from connector import DataConnector
from engine import VECTORES, CentinelaEngine, hace
from llm import diagnostico
from ui import CSS, icono, barra_estado

load_dotenv()
st.set_page_config(page_title="Centinela", page_icon="🛡️", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)

ICONO_VECTOR = {"breach": "correo", "acceso": "ubicacion", "foto": "imagen", "permiso": "ajustes"}

engine = CentinelaEngine()
ss = st.session_state
ss.setdefault("vista", "Consulta")
ss.setdefault("caso", None)
ss.setdefault("detalle", None)


def ir(vista, detalle=None):
    ss.vista, ss.detalle = vista, detalle


def actualizar_diagnostico():
    caso = ss.caso
    reporte = engine.generate_case_report(caso["id"], caso["hallazgos"])
    caso["reporte"] = reporte
    caso["diag"] = diagnostico(caso["hallazgos"], reporte["score"], reporte["status"], caso["consulta"])


def validar(h, fue_el_usuario):
    engine.validar(h, fue_el_usuario)
    actualizar_diagnostico()


def empezar_caso():
    fuentes = {k: ss[f"f_{k}"] for k in ("breach", "foto", "acceso", "banco", "permiso")}
    if not any(fuentes.values()):
        ss.aviso = "Selecciona al menos una fuente."
        return
    fotos_sub, act_sub, perm_sub = ss.get("fotos_sub"), ss.get("act_sub"), ss.get("perm_sub")
    inicio = time.time()
    c = DataConnector(ss.correo)
    datos = {}
    if fuentes["breach"]:
        datos["breaches"] = c.fetch_breach_data()
    if fuentes["foto"]:
        datos["fotos"] = c.fetch_photo_metadata(fotos_sub or None)
    if fuentes["acceso"] or fuentes["banco"]:
        act = c.fetch_activity_logs(act_sub)
        datos["actividad"] = {"accesos": act["accesos"] if fuentes["acceso"] else [],
                              "movimientos": act["movimientos"] if fuentes["banco"] else []}
    if fuentes["permiso"]:
        datos["permisos"] = c.fetch_permissions(perm_sub)
    ss.caso = {"id": random.randint(100, 999), "correo": ss.correo, "consulta": ss.consulta,
               "hallazgos": engine.analizar(datos),
               "simulado": not (fotos_sub or act_sub or perm_sub)}
    actualizar_diagnostico()
    ss.caso["segundos"] = round(time.time() - inicio, 2)
    ir("Caso")


def html(contenido):
    st.markdown(contenido, unsafe_allow_html=True)


def chip(texto, color="var(--texto-2)"):
    return f"<span class='chip' style='color:{color}'>{texto}</span>"


def fuente(clave, icono_nombre, titulo, subtitulo, activa):
    with st.container(key=f"fuente_{clave}"):
        c1, c2 = st.columns([6, 1], vertical_alignment="center")
        c1.markdown(f"<div class='fila'>{icono(icono_nombre)}<div><div class='t'>{titulo}</div>"
                    f"<div class='s'>{subtitulo}</div></div></div>", unsafe_allow_html=True)
        c2.checkbox(titulo, activa, key=f"f_{clave}", label_visibility="collapsed")


def vista_consulta():
    html(f"<div class='marca'><div class='logo'>{icono('escudo', 30)}</div><div><div class='h1'>Centinela</div>"
         f"<div class='s'>Listo para revisar tu privacidad</div></div></div>")
    html(f"<div class='fila-entre'><div class='h2'>Una revisión, más claridad.</div>{chip('Modo demo', 'var(--acento)')}</div>")
    st.text_input("Correo a auditar", "usuario@example.com", key="correo")
    st.text_area("¿Qué deseas que revise?", placeholder="Por ejemplo: la privacidad de mis fotos",
                 key="consulta", height=90)

    html("<div class='fila-entre'><div class='h3'>Fuentes a revisar</div><div class='s'>Tú eliges qué compartir</div></div>")
    fuente("breach", "correo", "Correos (Breaches)", "Filtraciones públicas", True)
    fuente("foto", "imagen", "Fotos recientes (GPS)", "Ubicación en tus imágenes", True)
    fuente("acceso", "ubicacion", "Actividad de la cuenta", "Inicios de sesión", True)
    fuente("banco", "banco", "Actividad bancaria", "Datos que tú proporciones", False)
    fuente("permiso", "ajustes", "Permisos de apps", "Cámara, micrófono, ubicación", True)

    with st.expander("Usar mis propios datos"):
        st.file_uploader("Fotos (JPG)", type=["jpg", "jpeg"], accept_multiple_files=True, key="fotos_sub")
        st.file_uploader("Actividad (JSON)", type="json", key="act_sub")
        st.file_uploader("Permisos (JSON)", type="json", key="perm_sub")
        st.caption("Mismo formato que los archivos de data/.")

    st.button("Empezar Caso", type="primary", use_container_width=True, on_click=empezar_caso, key="empezar")
    if ss.pop("aviso", None):
        st.warning("Selecciona al menos una fuente.")
    html(f"<div class='nota'>{icono('candado', 16)}<span>Prototipo académico PTIA. Datos simulados o "
         f"aportados por ti; nada se guarda.</span></div>")


def encabezado(titulo, subtitulo, derecha=""):
    html(f"<div class='fila-entre arriba'><div><div class='h1'>{titulo}</div><div class='s'>{subtitulo}</div></div>"
         f"{derecha}</div>")


def vista_caso():
    caso = ss.caso
    if ss.detalle is not None:
        return vista_detalle(next(h for h in caso["hallazgos"] if h.id == ss.detalle))
    encabezado(caso["reporte"]["case_id"], "Tu privacidad, señal por señal.",
               chip("Datos simulados") if caso["simulado"] else "")
    html("<div class='fila-entre'><div class='h3'>Actividad del caso</div><div class='s'>Más reciente primero</div></div>")
    if not caso["hallazgos"]:
        st.success("No se encontraron señales de riesgo en las fuentes seleccionadas.")
    for h in caso["hallazgos"]:
        pendiente = h.validable and h.estado == "pendiente"
        clase = "alerta" if pendiente else "critica" if h.estado == "no_reconocido" else ""
        with st.container(key=f"hallazgo_{h.id}"):
            html(f"<div class='tl {clase}'><div class='cuando'>{hace(h.fecha)}</div>"
                 f"<div class='ico'>{icono(ICONO_VECTOR[h.vector], 18)}</div>"
                 f"<div class='t'>{h.titulo}</div></div>")
            if pendiente:
                etiqueta = "Requiere tu validación →"
            elif h.estado == "reconocido":
                etiqueta = "Reconocido por ti ✓"
            elif h.estado == "no_reconocido":
                etiqueta = "No reconocido: prioridad alta →"
            else:
                etiqueta = VECTORES[h.vector] + " →"
            st.button(etiqueta, key=f"ver{h.id}", type="tertiary", on_click=ir, args=("Caso", h.id))
    html(f"<div class='nota'>{icono('info', 16)}<span>Una señal no confirma un incidente. "
         f"Valida el acceso para entender qué ocurrió.</span></div>")


def vista_detalle(h):
    c1, c2 = st.columns([1, 1], vertical_alignment="center")
    c1.button("← Volver", type="tertiary", on_click=ir, args=("Caso",), key="volver")
    c2.markdown(f"<div style='text-align:right'>{chip(ss.caso['reporte']['case_id'], 'var(--acento)')}</div>",
                unsafe_allow_html=True)
    html(f"<div class='h1'>Detalle del hallazgo #{h.id}</div><div class='s'>{h.titulo}</div>")
    pendiente = h.validable and h.estado == "pendiente"
    estado = {"pendiente": "Acceso por validar" if h.validable else f"Severidad {h.severidad}",
              "reconocido": "Reconocido por ti", "no_reconocido": "No reconocido"}[h.estado]
    extra = ""
    if "habitual" in h.extra:
        extra = (f"<div class='comparar'><div><div class='s'>Ubicación habitual</div><div class='g'>{h.extra['habitual']}</div></div>"
                 f"<div class='flecha'>→</div><div><div class='s'>Acceso del {h.fecha:%d/%m}</div>"
                 f"<div class='g rojo'>{h.extra['ciudad']}</div></div></div>")
    html(f"<div class='tarjeta {'alerta' if pendiente or h.estado == 'no_reconocido' else ''}'>"
         f"<div class='estado'>{icono('alerta', 18)}<span>{estado}</span></div>"
         f"<p class='detalle'>{h.detalle}</p>{extra}</div>")
    if "lat" in h.extra:
        st.map({"lat": [h.extra["lat"]], "lon": [h.extra["lon"]]}, zoom=11, height=200)

    if h.validable:
        html("<div class='h2'>¿Fuiste tú?</div><div class='s'>Tu respuesta ayuda a interpretar esta señal.</div>")
        c1, c2 = st.columns(2)
        c1.button("Sí", use_container_width=True, on_click=validar, args=(h, True),
                  disabled=h.estado != "pendiente", key="si")
        c2.button("No", type="primary", use_container_width=True, on_click=validar, args=(h, False),
                  disabled=h.estado != "pendiente", key="no", icon=":material/gpp_maybe:")
        if h.estado == "reconocido":
            mensaje = "Marcado como reconocido: ya no suma riesgo al caso."
        elif h.estado == "no_reconocido":
            mensaje = "Marcado como no reconocido. Revisa tus sesiones y cambia tu contraseña ahora."
        else:
            mensaje = "Si no reconoces el acceso, revisa tus sesiones y cambia tu contraseña."
        html(f"<div class='nota caja'>{icono('info', 16)}<span>{mensaje}</span></div>")


def anillo(score, estado):
    color = "#6dd3a0" if score >= 80 else "#f2c46d" if score >= 50 else "#ff6b78"
    largo = 2 * 3.1416 * 80
    return (f"<div class='anillo'><svg viewBox='0 0 200 200' width='180' height='180'>"
            f"<circle cx='100' cy='100' r='80' stroke='#2a2a2c' stroke-width='12' fill='none'/>"
            f"<circle cx='100' cy='100' r='80' stroke='{color}' stroke-width='12' fill='none' stroke-linecap='round'"
            f" stroke-dasharray='{largo * score / 100:.1f} {largo:.1f}' transform='rotate(-90 100 100)'/></svg>"
            f"<div class='centro'><div class='num'>{score}/100</div><div style='color:{color}'>{estado}</div></div></div>")


def vista_riesgo():
    caso = ss.caso
    r = caso["reporte"]
    encabezado("Resumen de riesgo", "Una vista clara de tu exposición.", chip(r["case_id"], "var(--acento)"))
    aviso = "Hay señales que necesitan tu atención." if r["score"] < 80 else "Tu exposición es baja."
    html(f"<div class='tarjeta centrada'>{anillo(r['score'], r['status'])}<div class='s'>{aviso}<br>"
         f"{'Puntuación ilustrativa con datos simulados.' if caso['simulado'] else ''}</div></div>")
    n = r["summary_counts"]
    metricas = [("breach", "correo", "Filtraciones halladas"), ("acceso", "ubicacion", "Actividad sospechosa"),
                ("foto", "imagen", "Fotos con GPS visible"), ("permiso", "ajustes", "Permisos a revisar")]
    html("<div class='grilla'>" + "".join(
        f"<div class='metrica'><div class='fila-entre'><div class='num'>{n[k]}</div>{icono(ic, 20)}</div>"
        f"<div class='s'>{t}</div></div>" for k, ic, t in metricas) + "</div>")

    d = caso["diag"]
    with st.expander("Ver recomendaciones →", expanded=False):
        html(f"<p class='detalle'>{d['resumen']}</p>")
        html("<ol class='recs'>" + "".join(f"<li>{x}</li>" for x in d["recomendaciones"]) + "</ol>")
        st.caption(f"Generado por {'LLM' if d['origen'] == 'llm' else 'el motor de reglas'} "
                   f"en {caso.get('segundos', 0)} s.")
        st.download_button("Descargar expediente", expediente_md(caso), file_name=f"expediente_{caso['id']}.md",
                           use_container_width=True, icon=":material/download:")
    pendientes = [h for h in caso["hallazgos"] if h.validable and h.estado == "pendiente"]
    if pendientes:
        html(f"<div class='s centrado'>Empieza por validar: {pendientes[0].titulo.lower()}.</div>")


def expediente_md(caso) -> str:
    r, d = caso["reporte"], caso["diag"]
    lineas = [f"# Expediente {r['case_id']}", "", f"- Correo: {caso['correo']}",
              f"- Puntaje: {r['score']}/100 ({r['status']})", "", "## Línea de tiempo", ""]
    for h in caso["hallazgos"]:
        lineas.append(f"- **{hace(h.fecha)}** · {h.titulo} [{h.severidad}, {h.estado}]: {h.detalle}")
    lineas += ["", "## Diagnóstico", "", d["resumen"], "", "## Recomendaciones", ""]
    lineas += [f"{i}. {x}" for i, x in enumerate(d["recomendaciones"], 1)]
    return "\n".join(lineas)


def navegacion():
    with st.container(key="nav"):
        cols = st.columns(3)
        for col, (vista, ic) in zip(cols, [("Consulta", ":material/verified_user:"), ("Caso", ":material/history:"),
                                           ("Riesgo", ":material/monitoring:")]):
            col.button(vista, key=f"nav_{vista}", icon=ic, use_container_width=True,
                       type="primary" if ss.vista == vista else "secondary", on_click=ir, args=(vista,))


html(barra_estado())
with st.container(key="pantalla"):
    if ss.vista == "Consulta":
        vista_consulta()
    elif ss.caso is None:
        html(f"<div class='vacio'>{icono('escudo', 40)}<div class='h2'>Aún no hay un caso</div>"
             f"<div class='s'>Elige tus fuentes en Consulta y pulsa «Empezar Caso».</div></div>")
    elif ss.vista == "Caso":
        vista_caso()
    else:
        vista_riesgo()
navegacion()
