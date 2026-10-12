"""
Módulo Connector: Encargado de simular o conectar con las fuentes de datos
de riesgo (Breaches, metadatos de fotos, logs de accesos).
"""

class DataConnector:
    def __init__(self, user_email: str):
        self.user_email = user_email

    def fetch_breach_data(self) -> dict:
        """Simula o consulta fuentes de correos filtrados (Breaches)."""
        return {
            "source": "Correos (Breaches)",
            "status": "Exposición detectada",
            "details": "Correo hallado en filtración de credenciales (2027)."
        }

    def fetch_activity_logs(self) -> list:
        """Simula la obtención de registros de actividad y accesos recientes."""
        return [
            {
                "timestamp": "Hace 1 día",
                "event": "Login desde ciudad no habitual (Bogotá)",
                "risk_level": "Alto"
            }
        ]

    def fetch_photo_metadata(self) -> list:
        """Simula la revisión de metadatos en fotos recientes."""
        return [
            {
                "item": "Foto reciente #3",
                "issue": "Ubicación GPS visible incrustada en metadatos."
            }
        ]