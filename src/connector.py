"""Conectores de fuentes de riesgo: filtraciones, fotos, actividad y permisos."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import requests
from PIL import Image
from PIL.ExifTags import GPSTAGS

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _cargar_json(nombre: str):
    with open(DATA_DIR / nombre, encoding="utf-8") as f:
        return json.load(f)


def _fecha(dias_atras: float, hora: int = 12) -> datetime:
    base = datetime.now().replace(hour=hora, minute=0, second=0, microsecond=0)
    return base - timedelta(days=dias_atras)


class DataConnector:
    def __init__(self, user_email: str):
        self.user_email = user_email.strip().lower()

    # Correos (Breaches)
    def fetch_breach_data(self) -> list:
        api_key = os.getenv("HIBP_API_KEY")
        if api_key:
            try:
                return self._consultar_hibp(api_key)
            except requests.RequestException:
                pass  # si falla la API se usa la base local
        dominio = self.user_email.split("@")[-1]
        hallados = []
        for b in _cargar_json("breaches.json"):
            if self.user_email in b["correos"] or dominio in b.get("dominios", []):
                hallados.append({
                    "nombre": b["nombre"],
                    "fecha": _fecha(b["dias_atras"]),
                    "datos": b["datos"],
                })
        return hallados

    def _consultar_hibp(self, api_key: str) -> list:
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{self.user_email}"
        r = requests.get(url, headers={"hibp-api-key": api_key, "user-agent": "centinela-ptia"},
                         params={"truncateResponse": "false"}, timeout=8)
        if r.status_code == 404:
            return []
        r.raise_for_status()
        return [{
            "nombre": b["Name"],
            "fecha": datetime.fromisoformat(b["AddedDate"].replace("Z", "")),
            "datos": b.get("DataClasses", []),
        } for b in r.json()]

    # Actividad (accesos y movimientos bancarios)
    def fetch_activity_logs(self, archivo=None) -> dict:
        datos = json.load(archivo) if archivo else _cargar_json("actividad_demo.json")
        accesos = [{**a, "fecha": self._leer_fecha(a)} for a in datos.get("accesos", [])]
        movimientos = [{**m, "fecha": self._leer_fecha(m)} for m in datos.get("movimientos", [])]
        return {"accesos": accesos, "movimientos": movimientos}

    # Fotos recientes (metadatos GPS)
    def fetch_photo_metadata(self, archivos=None) -> list:
        if not archivos:
            carpeta = DATA_DIR / "fotos_demo"
            archivos = sorted(carpeta.glob("*.jpg"))
        fotos = []
        for a in archivos:
            nombre = getattr(a, "name", str(a))
            try:
                with Image.open(a) as img:
                    exif = img.getexif()
            except Exception:
                continue
            gps = self._extraer_gps(exif)
            fecha_txt = exif.get_ifd(0x8769).get(36867) or exif.get(306)
            try:
                fecha = datetime.strptime(fecha_txt, "%Y:%m:%d %H:%M:%S")
            except (TypeError, ValueError):
                fecha = datetime.now()
            fotos.append({"nombre": Path(nombre).name, "gps": gps, "fecha": fecha,
                          "camara": exif.get(272)})
        return fotos

    @staticmethod
    def _extraer_gps(exif):
        gps_ifd = exif.get_ifd(0x8825)
        if not gps_ifd:
            return None
        g = {GPSTAGS.get(k, k): v for k, v in gps_ifd.items()}
        if "GPSLatitude" not in g or "GPSLongitude" not in g:
            return None

        def a_grados(v, ref):
            d, m, s = (float(x) for x in v)
            val = d + m / 60 + s / 3600
            return -val if ref in ("S", "W") else val

        return (round(a_grados(g["GPSLatitude"], g.get("GPSLatitudeRef", "N")), 5),
                round(a_grados(g["GPSLongitude"], g.get("GPSLongitudeRef", "E")), 5))

    # Permisos de apps
    def fetch_permissions(self, archivo=None) -> list:
        datos = json.load(archivo) if archivo else _cargar_json("permisos_demo.json")
        permisos = []
        for p in datos:
            if "ultimo_uso" in p:
                uso = datetime.fromisoformat(p["ultimo_uso"])
            else:
                uso = _fecha(p["dias_sin_uso"])
            permisos.append({**p, "ultimo_uso": uso})
        return permisos

    @staticmethod
    def _leer_fecha(item: dict) -> datetime:
        # el archivo puede traer "fecha" ISO o "dias_atras" (datos demo)
        if "fecha" in item:
            return datetime.fromisoformat(item["fecha"])
        return _fecha(item["dias_atras"], item.get("hora", 12))
