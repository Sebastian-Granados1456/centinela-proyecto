"""
Módulo Engine: Núcleo de razonamiento del Agente Centinela.
Procesa las señales y genera el diagnóstico y recomendaciones.
"""

class CentinelaEngine:
    def __init__(self):
        self.base_score = 100

    def calculate_risk_score(self, findings_count: int) -> int:
        """Calcula una métrica de riesgo cuantitativa basada en los hallazgos."""
        penalty = findings_count * 10
        final_score = max(0, self.base_score - penalty)
        return final_score

    def generate_case_report(self, raw_data: dict) -> dict:
        """
        Simula el razonamiento del LLM para estructurar el expediente
        y redactar recomendaciones en lenguaje claro.
        """
        score = self.calculate_risk_score(len(raw_data.get("logs", [])) + 1)

        report = {
            "case_id": "Caso #192",
            "score": score,
            "status": "Expuesto" if score < 70 else "Seguro",
            "summary_counts": {
                "breaches": 1,
                "suspicious_access": 1,
                "photos_with_gps": 3,
                "permissions_to_review": 2
            },
            "recommendation": "Se recomienda cambiar la contraseña del correo principal y revocar permisos de ubicación en las fotografías recientes."
        }
        return report