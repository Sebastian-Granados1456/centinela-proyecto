"""Capa de razonamiento: el LLM redacta el diagnóstico; si no hay API key se usan reglas."""

import json
import os

from engine import Hallazgo, hace

PROMPT_SISTEMA = (
    "Eres Centinela, un investigador digital de privacidad. Recibes los hallazgos de un caso "
    "y respondes SOLO un JSON con las claves 'resumen' (máximo 3 frases, lenguaje simple, sin "
    "alarmismo) y 'recomendaciones' (lista de 3 a 5 pasos concretos, ordenados por prioridad). "
    "Ten en cuenta la validación del usuario: si reconoció un acceso no lo trates como riesgo; "
    "si no lo reconoció es lo más urgente."
)

RECOMENDACIONES_BASE = {
    "acceso_no": "Cierra las sesiones abiertas y cambia la contraseña de la cuenta afectada ahora mismo.",
    "acceso": "Valida los accesos pendientes en la pestaña Caso (¿Fuiste tú?).",
    "breach": "Cambia la contraseña del correo filtrado y no la reutilices en otros servicios.",
    "breach_2fa": "Activa la verificación en dos pasos en tu correo principal.",
    "foto": "Desactiva la ubicación en la cámara y borra los metadatos antes de compartir fotos.",
    "permiso": "Revoca los permisos de las apps que no usan su acceso desde hace más de un mes.",
    "ok": "No hay señales de riesgo activas. Repite la revisión periódicamente.",
}


def _serializar(hallazgos: list[Hallazgo]) -> list[dict]:
    return [{"id": h.id, "tipo": h.vector, "titulo": h.titulo, "detalle": h.detalle,
             "cuando": hace(h.fecha), "severidad": h.severidad, "validacion": h.estado}
            for h in hallazgos]


def diagnostico_reglas(hallazgos: list[Hallazgo], score: int, estado: str) -> dict:
    activos = [h for h in hallazgos if h.estado != "reconocido"]
    recs = []
    if any(h.estado == "no_reconocido" for h in activos):
        recs.append(RECOMENDACIONES_BASE["acceso_no"])
    if any(h.validable and h.estado == "pendiente" for h in activos):
        recs.append(RECOMENDACIONES_BASE["acceso"])
    if any(h.vector == "breach" for h in activos):
        recs += [RECOMENDACIONES_BASE["breach"], RECOMENDACIONES_BASE["breach_2fa"]]
    if any(h.vector == "foto" for h in activos):
        recs.append(RECOMENDACIONES_BASE["foto"])
    if any(h.vector == "permiso" for h in activos):
        recs.append(RECOMENDACIONES_BASE["permiso"])
    if not recs:
        recs.append(RECOMENDACIONES_BASE["ok"])

    if not activos:
        resumen = f"Tu puntaje es {score}/100 ({estado}). No encontramos señales que requieran atención."
    else:
        peor = max(activos, key=lambda h: h.peso)
        resumen = (f"Tu puntaje es {score}/100 ({estado}). Encontramos {len(activos)} señales; "
                   f"la más importante es: {peor.titulo.lower()} ({hace(peor.fecha).lower()}). "
                   "Una señal no confirma un incidente, pero conviene revisarla.")
    return {"resumen": resumen, "recomendaciones": recs, "origen": "reglas"}


def diagnostico(hallazgos: list[Hallazgo], score: int, estado: str, consulta: str = "") -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return diagnostico_reglas(hallazgos, score, estado)
    try:
        from openai import OpenAI
        cliente = OpenAI(api_key=api_key, timeout=12)
        entrada = {"consulta_usuario": consulta, "puntaje": score, "estado": estado,
                   "hallazgos": _serializar(hallazgos)}
        r = cliente.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": PROMPT_SISTEMA},
                      {"role": "user", "content": json.dumps(entrada, ensure_ascii=False)}],
        )
        datos = json.loads(r.choices[0].message.content)
        return {"resumen": datos["resumen"], "recomendaciones": list(datos["recomendaciones"]),
                "origen": "llm"}
    except Exception:
        return diagnostico_reglas(hallazgos, score, estado)
