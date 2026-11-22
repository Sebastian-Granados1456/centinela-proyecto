"""Motor del Agente Centinela: detecta hallazgos, arma la línea de tiempo y calcula el puntaje."""

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from statistics import median

# Base de conocimiento: pesos por severidad y umbrales
PESOS = {"baja": 2, "media": 6, "alta": 10, "crítica": 20}
PERMISOS_SENSIBLES = {"ubicación", "micrófono", "cámara", "contactos", "fotos"}
DIAS_PERMISO_INACTIVO = 30
FACTOR_GASTO_ATIPICO = 3
HORA_INICIO_HABITUAL, HORA_FIN_HABITUAL = 6, 23
MIN_ACCESOS_PATRON = 3

VECTORES = {
    "breach": "Filtraciones públicas",
    "acceso": "Actividad de la cuenta",
    "foto": "Metadatos de la imagen",
    "permiso": "Permisos de aplicaciones",
}


@dataclass
class Hallazgo:
    id: int
    vector: str
    titulo: str
    detalle: str
    fecha: datetime
    severidad: str
    peso: int
    validable: bool = False
    estado: str = "pendiente"  # pendiente | reconocido | no_reconocido
    extra: dict = field(default_factory=dict)


def hace(fecha: datetime, ahora: datetime | None = None) -> str:
    dias = ((ahora or datetime.now()) - fecha).days
    if dias < 1:
        return "Hoy"
    if dias < 7:
        return f"Hace {dias} día" + ("s" if dias > 1 else "")
    if dias < 30:
        s = dias // 7
        return f"Hace {s} semana" + ("s" if s > 1 else "")
    if dias < 365:
        m = dias // 30
        return f"Hace {m} mes" + ("es" if m > 1 else "")
    a = dias // 365
    return f"Hace {a} año" + ("s" if a > 1 else "")


class CentinelaEngine:
    def __init__(self):
        self.base_score = 100

    def analizar(self, fuentes: dict) -> list[Hallazgo]:
        hallazgos = []
        hallazgos += self._analizar_breaches(fuentes.get("breaches", []))
        hallazgos += self._analizar_accesos(fuentes.get("actividad", {}).get("accesos", []))
        hallazgos += self._analizar_movimientos(fuentes.get("actividad", {}).get("movimientos", []))
        hallazgos += self._analizar_fotos(fuentes.get("fotos", []))
        hallazgos += self._analizar_permisos(fuentes.get("permisos", []))
        hallazgos.sort(key=lambda h: h.fecha, reverse=True)
        for i, h in enumerate(hallazgos, start=1):
            h.id = i
        return hallazgos

    def _analizar_breaches(self, breaches):
        res = []
        for b in breaches:
            datos = [d.lower() for d in b["datos"]]
            sev = "alta" if any("contrase" in d or "password" in d for d in datos) else "media"
            res.append(Hallazgo(0, "breach", "Correo hallado en filtración",
                                f"Tu correo aparece en la filtración de {b['nombre']}. "
                                f"Datos expuestos: {', '.join(b['datos'])}.",
                                b["fecha"], sev, PESOS[sev] + 2,
                                extra={"nombre": b["nombre"], "datos": b["datos"]}))
        return res

    def _analizar_accesos(self, accesos):
        accesos = sorted(accesos, key=lambda a: a["fecha"])
        if len(accesos) < MIN_ACCESOS_PATRON:
            return []
        ciudad_habitual = Counter(a["ciudad"] for a in accesos).most_common(1)[0][0]
        res, vistos = [], set()
        for a in accesos:
            nuevo_disp = a.get("dispositivo") not in vistos
            vistos.add(a.get("dispositivo"))
            previos = [p for p in accesos if p["fecha"] < a["fecha"]]
            if len(previos) < MIN_ACCESOS_PATRON:
                continue
            racha = 0
            for p in reversed(previos):
                if p["ciudad"] != ciudad_habitual:
                    break
                racha += 1
            if a["ciudad"] != ciudad_habitual:
                detalle = (f"Se detectó un inicio de sesión el {a['fecha']:%d/%m} desde {a['ciudad']}, "
                           f"cuando tus últimos {racha} accesos fueron desde {ciudad_habitual}.")
                if nuevo_disp:
                    detalle += " Dispositivo no reconocido previamente."
                res.append(Hallazgo(0, "acceso", "Login desde ciudad no habitual", detalle,
                                    a["fecha"], "alta", PESOS["alta"], validable=True,
                                    extra={"habitual": ciudad_habitual, "ciudad": a["ciudad"],
                                           "dispositivo": a.get("dispositivo")}))
            elif not HORA_INICIO_HABITUAL <= a["fecha"].hour < HORA_FIN_HABITUAL:
                res.append(Hallazgo(0, "acceso", "Acceso fuera de tu horario habitual",
                                    f"Inicio de sesión a las {a['fecha']:%H:%M} del {a['fecha']:%d/%m} "
                                    f"desde {a['ciudad']} ({a.get('dispositivo', 'dispositivo desconocido')}).",
                                    a["fecha"], "media", PESOS["media"], validable=True,
                                    extra={"habitual": ciudad_habitual, "ciudad": a["ciudad"]}))
        return res

    def _analizar_movimientos(self, movimientos):
        if len(movimientos) < MIN_ACCESOS_PATRON:
            return []
        mediana = median(m["monto"] for m in movimientos)
        res = []
        for m in movimientos:
            if m["monto"] > FACTOR_GASTO_ATIPICO * mediana:
                res.append(Hallazgo(0, "acceso", "Gasto atípico en tu cuenta",
                                    f"Cobro de ${m['monto']:,.0f} en {m['comercio']} el {m['fecha']:%d/%m}; "
                                    f"tu gasto típico es de ${mediana:,.0f}.",
                                    m["fecha"], "media", PESOS["media"], validable=True,
                                    extra={"comercio": m["comercio"], "monto": m["monto"]}))
        return res

    def _analizar_fotos(self, fotos):
        res = []
        for f in fotos:
            if f["gps"]:
                lat, lon = f["gps"]
                res.append(Hallazgo(0, "foto", "Foto con ubicación GPS visible",
                                    f"La imagen {f['nombre']} guarda sus coordenadas ({lat}, {lon}). "
                                    "Si la compartes, revela dónde fue tomada.",
                                    f["fecha"], "baja", PESOS["baja"] + 2,
                                    extra={"lat": lat, "lon": lon, "nombre": f["nombre"]}))
        return res

    def _analizar_permisos(self, permisos):
        res, ahora = [], datetime.now()
        for p in permisos:
            dias = (ahora - p["ultimo_uso"]).days
            if p["permiso"].lower() in PERMISOS_SENSIBLES and dias >= DIAS_PERMISO_INACTIVO:
                res.append(Hallazgo(0, "permiso", f"App con permiso de {p['permiso'].lower()} sin uso",
                                    f"{p['app']} tiene acceso a {p['permiso'].lower()} y no lo usa hace {dias} días.",
                                    p["ultimo_uso"], "baja", PESOS["baja"],
                                    extra={"app": p["app"], "permiso": p["permiso"]}))
        return res

    @staticmethod
    def validar(h: Hallazgo, fue_el_usuario: bool):
        if fue_el_usuario:
            h.estado, h.peso = "reconocido", 0
        else:
            h.estado, h.severidad, h.peso = "no_reconocido", "crítica", PESOS["crítica"]

    def calculate_risk_score(self, hallazgos: list[Hallazgo]) -> int:
        return max(0, self.base_score - sum(h.peso for h in hallazgos))

    @staticmethod
    def estado_score(score: int) -> str:
        if score >= 80:
            return "Protegido"
        return "Expuesto" if score >= 50 else "Crítico"

    @staticmethod
    def conteos(hallazgos: list[Hallazgo]) -> dict:
        activos = [h for h in hallazgos if h.estado != "reconocido"]
        return {v: sum(1 for h in activos if h.vector == v) for v in VECTORES}

    def generate_case_report(self, case_id: int, hallazgos: list[Hallazgo]) -> dict:
        score = self.calculate_risk_score(hallazgos)
        return {
            "case_id": f"Caso #{case_id}",
            "score": score,
            "status": self.estado_score(score),
            "summary_counts": self.conteos(hallazgos),
            "hallazgos": hallazgos,
        }
