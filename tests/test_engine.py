import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from connector import DataConnector  # noqa: E402
from engine import CentinelaEngine  # noqa: E402
from llm import diagnostico_reglas  # noqa: E402


def caso_demo(correo="usuario@example.com", banco=False):
    c = DataConnector(correo)
    act = c.fetch_activity_logs()
    datos = {"breaches": c.fetch_breach_data(), "fotos": c.fetch_photo_metadata(),
             "permisos": c.fetch_permissions(),
             "actividad": {"accesos": act["accesos"], "movimientos": act["movimientos"] if banco else []}}
    return CentinelaEngine().analizar(datos)


class TestCentinela(unittest.TestCase):
    def setUp(self):
        self.engine = CentinelaEngine()

    def test_caso_demo_completo(self):
        hs = caso_demo()
        r = self.engine.generate_case_report(192, hs)
        self.assertEqual(r["summary_counts"], {"breach": 1, "acceso": 1, "foto": 3, "permiso": 2})
        self.assertEqual(r["score"], 62)
        self.assertEqual(r["status"], "Expuesto")
        self.assertEqual(hs[0].titulo, "Login desde ciudad no habitual")

    def test_validacion_si_y_no(self):
        hs = caso_demo()
        acceso = hs[0]
        self.engine.validar(acceso, True)
        self.assertEqual(self.engine.calculate_risk_score(hs), 72)
        hs = caso_demo()
        self.engine.validar(hs[0], False)
        self.assertEqual(self.engine.calculate_risk_score(hs), 52)
        recs = diagnostico_reglas(hs, 52, "Expuesto")["recomendaciones"]
        self.assertIn("cambia la contraseña de la cuenta afectada", recs[0])

    def test_gasto_atipico(self):
        hs = caso_demo(banco=True)
        gastos = [h for h in hs if h.titulo == "Gasto atípico en tu cuenta"]
        self.assertEqual(len(gastos), 1)
        self.assertEqual(gastos[0].extra["monto"], 950000)

    def test_correo_limpio_sin_filtraciones(self):
        self.assertEqual(DataConnector("nadie@limpio.com").fetch_breach_data(), [])

    def test_breach_por_dominio(self):
        self.assertEqual(len(DataConnector("x@correo-viejo.com").fetch_breach_data()), 1)

    def test_pocos_accesos_no_generan_patron(self):
        ahora = datetime.now()
        accesos = [{"fecha": ahora - timedelta(days=1), "ciudad": "Bogotá", "dispositivo": "PC"}]
        self.assertEqual(self.engine.analizar({"actividad": {"accesos": accesos}}), [])

    def test_acceso_de_madrugada(self):
        base = datetime.now().replace(hour=10) - timedelta(days=10)
        accesos = [{"fecha": base + timedelta(days=i), "ciudad": "Cali", "dispositivo": "Cel"} for i in range(5)]
        accesos.append({"fecha": (base + timedelta(days=6)).replace(hour=3), "ciudad": "Cali", "dispositivo": "Cel"})
        hs = self.engine.analizar({"actividad": {"accesos": accesos}})
        self.assertEqual([h.titulo for h in hs], ["Acceso fuera de tu horario habitual"])

    def test_sin_hallazgos(self):
        r = self.engine.generate_case_report(1, [])
        self.assertEqual((r["score"], r["status"]), (100, "Protegido"))


if __name__ == "__main__":
    unittest.main()
