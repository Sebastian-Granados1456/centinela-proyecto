"""Estilos e íconos para que Streamlit se vea como una app móvil (basado en los mockups de Figma)."""

_TRAZOS = {
    "correo": "<rect x='3' y='5' width='18' height='14' rx='2'/><path d='m3 7 9 6 9-6'/>",
    "imagen": "<rect x='3' y='3' width='18' height='18' rx='2'/><circle cx='9' cy='9' r='2'/><path d='m21 15-5-5L5 21'/>",
    "ubicacion": "<path d='M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z'/><circle cx='12' cy='10' r='2.5'/>",
    "ajustes": "<path d='M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0'/><circle cx='16' cy='6' r='2'/>"
               "<circle cx='10' cy='12' r='2'/><circle cx='18' cy='18' r='2'/>",
    "banco": "<path d='M3 10h18L12 4 3 10zM5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18'/>",
    "escudo": "<path d='M12 3 5 6v5c0 4.5 3 8.3 7 10 4-1.7 7-5.5 7-10V6l-7-3z'/><path d='m9 12 2 2 4-4'/>",
    "candado": "<rect x='5' y='11' width='14' height='10' rx='2'/><path d='M8 11V7a4 4 0 0 1 8 0v4'/>",
    "info": "<circle cx='12' cy='12' r='9'/><path d='M12 11v5M12 8h.01'/>",
    "alerta": "<path d='M12 4 2.5 20h19L12 4z'/><path d='M12 10v4M12 17h.01'/>",
}


def icono(nombre, tam=22):
    return (f"<svg class='icono' width='{tam}' height='{tam}' viewBox='0 0 24 24' fill='none' stroke='currentColor' "
            f"stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'>{_TRAZOS[nombre]}</svg>")


def barra_estado():
    return ("<div class='barra-estado'><span>09:41</span><span class='derecha'>"
            "<svg width='18' height='12' viewBox='0 0 18 12' fill='currentColor'><rect x='0' y='8' width='3' height='4' rx='1'/>"
            "<rect x='5' y='5' width='3' height='7' rx='1'/><rect x='10' y='2' width='3' height='10' rx='1'/>"
            "<rect x='15' y='0' width='3' height='12' rx='1'/></svg>"
            "<svg width='26' height='12' viewBox='0 0 26 12'><rect x='0.5' y='0.5' width='22' height='11' rx='3' "
            "fill='none' stroke='currentColor'/><rect x='2.5' y='2.5' width='18' height='7' rx='1.5' fill='currentColor'/>"
            "<rect x='24' y='4' width='1.5' height='4' rx='0.7' fill='currentColor'/></svg></span></div>")


CSS = """
<style>
:root {
  --fondo: #0b0b0c; --tarjeta: #141416; --borde: #2a2a2d; --texto: #f2f3f5; --texto-2: #9aa3b2;
  --acento: #5fd6ee; --rojo: #f2959b; --rojo-borde: #6e3a40;
}
#MainMenu, footer, header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {display: none !important;}
.stApp {background: radial-gradient(circle at 50% -10%, #1d2633 0%, #07090c 60%);}

/* Marco del celular */
[data-testid="stMainBlockContainer"] {
  max-width: 410px; margin: 28px auto 40px; padding: 14px 22px 0;
  background: var(--fondo); border: 11px solid #1c1c1e; border-radius: 52px;
  box-shadow: 0 0 0 2px #333, 0 40px 90px rgba(0,0,0,.65); min-height: 860px; flex-shrink: 0 !important;
}
@media (max-width: 520px) {
  [data-testid="stMainBlockContainer"] {margin: 0; border: 0; border-radius: 0; box-shadow: none;
    max-width: 100%; min-height: 100vh; padding: 12px 16px 0;}
  .barra-estado {display: none !important;}
}
.st-key-pantalla {min-height: 690px;}
[data-testid="stHorizontalBlock"] {flex-wrap: nowrap !important;}
[data-testid="stColumn"] {min-width: 0 !important; flex: 1 1 0 !important;}
[class*="st-key-fuente_"] [data-testid="stColumn"]:last-child {flex: 0 0 34px !important;}

.barra-estado {display: flex; justify-content: space-between; align-items: center; color: var(--texto);
  font-weight: 600; font-size: 15px; padding: 4px 8px 10px;}
.barra-estado .derecha {display: flex; gap: 6px; align-items: center;}

/* Tipografía */
.h1 {font-size: 30px; font-weight: 700; color: var(--texto); line-height: 1.15;}
.h2 {font-size: 21px; font-weight: 700; color: var(--texto); margin: 6px 0 2px;}
.h3 {font-size: 17px; font-weight: 600; color: var(--texto);}
.s {font-size: 14px; color: var(--texto-2);}
.t {font-size: 16px; font-weight: 600; color: var(--texto);}
.centrado {text-align: center; margin-top: 8px;}
.fila-entre {display: flex; justify-content: space-between; align-items: center; gap: 8px; margin: 10px 0 6px;}
.fila-entre.arriba {align-items: flex-start; margin-bottom: 14px;}
.chip {background: #1c1c1f; border-radius: 999px; padding: 5px 12px; font-size: 13px; font-weight: 600; white-space: nowrap;}
.icono {color: var(--acento); flex-shrink: 0;}

/* Consulta */
.marca {display: flex; gap: 14px; align-items: center; margin: 4px 0 14px;}
.logo {width: 58px; height: 58px; border-radius: 16px; background: #1a1a1d; display: flex; align-items: center; justify-content: center;}
.fila {display: flex; gap: 14px; align-items: center;}
[class*="st-key-fuente_"] {background: var(--tarjeta); border: 1px solid var(--borde); border-radius: 18px;
  padding: 10px 14px; margin-bottom: 2px;}
[class*="st-key-fuente_"] .icono {color: #6cc9df;}
.stTextInput input, .stTextArea textarea {background: var(--tarjeta) !important; border-radius: 14px !important;}
.st-key-empezar button {height: 54px; border-radius: 16px; font-size: 18px; font-weight: 700; color: #0b0b0c;}
.st-key-empezar button p {font-size: 18px; font-weight: 700;}
.nota {display: flex; gap: 8px; align-items: flex-start; color: var(--texto-2); font-size: 13px; margin: 10px 0;}
.nota .icono {color: var(--texto-2); margin-top: 2px;}
.nota.caja {background: var(--tarjeta); border-radius: 14px; padding: 12px 14px;}

/* Línea de tiempo */
[class*="st-key-hallazgo_"] {background: var(--tarjeta); border: 1px solid var(--borde); border-radius: 18px;
  padding: 14px 16px 8px; gap: 2px !important; position: relative; margin-left: 22px; width: calc(100% - 22px) !important;}
[class*="st-key-hallazgo_"]::before {content: ""; position: absolute; left: -24px; top: 20px; width: 11px; height: 11px;
  border-radius: 50%; background: #7d8799;}
[class*="st-key-hallazgo_"]:has(.tl.alerta) {border-color: var(--rojo-borde);}
[class*="st-key-hallazgo_"]:has(.tl.alerta)::before, [class*="st-key-hallazgo_"]:has(.tl.critica)::before {background: var(--rojo);}
.tl {position: relative; padding-bottom: 2px;}
.tl .cuando {font-size: 14px; color: var(--texto-2);}
.tl.alerta .cuando, .tl.critica .cuando {color: var(--rojo);}
.tl .ico {position: absolute; right: 0; top: 0;}
.tl .ico .icono {color: var(--texto-2);}
.tl.alerta .ico .icono {color: var(--rojo);}
.tl .t {font-size: 17px; margin: 6px 0 0;}
[class*="st-key-hallazgo_"] button {padding: 0 !important; min-height: 0; justify-content: flex-start;}
[class*="st-key-hallazgo_"] button p {font-size: 14px; color: var(--texto-2);}
[class*="st-key-hallazgo_"]:has(.tl.alerta) button p {color: var(--rojo);}

/* Detalle */
.tarjeta {background: var(--tarjeta); border: 1px solid var(--borde); border-radius: 20px; padding: 18px; margin: 14px 0;}
.tarjeta.alerta {border-color: var(--rojo-borde);}
.tarjeta.centrada {text-align: center;}
.estado {display: flex; gap: 10px; align-items: center; color: var(--rojo); font-weight: 600;}
.estado .icono {color: var(--rojo);}
.detalle {color: var(--texto); font-size: 16px; line-height: 1.5; margin: 12px 0 0;}
.comparar {display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--borde);
  margin-top: 16px; padding-top: 14px;}
.comparar .g {font-size: 22px; font-weight: 700; color: var(--texto);}
.comparar .g.rojo, .comparar .flecha {color: var(--rojo);}
.st-key-si button, .st-key-no button {height: 54px; border-radius: 999px;}
.st-key-si button {background: var(--tarjeta);}
.st-key-no button {background: var(--rojo); border-color: var(--rojo); color: #1a0d0f;}
.st-key-si button p, .st-key-no button p {font-size: 18px; font-weight: 700;}
.st-key-volver button p {color: var(--acento); font-size: 17px;}

/* Riesgo */
.anillo {position: relative; width: 180px; height: 180px; margin: 0 auto 10px;}
.anillo .centro {position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center;}
.anillo .num {font-size: 38px; font-weight: 700; color: var(--texto);}
.grilla {display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;}
.metrica {background: var(--tarjeta); border: 1px solid var(--borde); border-radius: 18px; padding: 14px;}
.metrica .num {font-size: 30px; font-weight: 700; color: var(--texto);}
.metrica .fila-entre {margin: 0 0 4px;}
.recs {color: var(--texto); padding-left: 20px; line-height: 1.5;}
.recs li {margin-bottom: 6px;}
[data-testid="stExpander"] details {border-radius: 16px; border-color: var(--borde); background: var(--tarjeta);}
.vacio {text-align: center; padding-top: 180px;}
.vacio .icono {color: var(--texto-2);}

/* Navegación inferior */
.st-key-nav {position: sticky; bottom: 0; z-index: 20; background: var(--fondo); border-top: 1px solid #222;
  margin: 8px -22px 0; padding: 8px 14px 18px;}
.st-key-nav {width: calc(100% + 44px) !important; max-width: none !important;}
.st-key-nav button {border: 0 !important; background: transparent !important; border-radius: 18px; min-height: 60px; padding: 6px 4px !important;}
.st-key-nav button > div > span {display: flex !important; flex-direction: column; align-items: center; gap: 3px;}
.st-key-nav button * {overflow: visible !important; text-overflow: clip !important; white-space: nowrap;}
.st-key-nav [data-testid="stIconMaterial"] {font-size: 24px !important; width: 24px; height: 24px;}
.st-key-nav button p, .st-key-nav button span {color: var(--texto-2) !important; font-size: 13px;}
.st-key-nav [data-testid="stBaseButton-primary"] {background: #1c1c1f !important;}
.st-key-nav [data-testid="stBaseButton-primary"] p, .st-key-nav [data-testid="stBaseButton-primary"] span {color: var(--acento) !important;}
@media (max-width: 520px) {
  .st-key-nav {position: fixed; left: 0; right: 0; bottom: 0; margin: 0; width: 100% !important;}
  .st-key-pantalla {min-height: 0; padding-bottom: 90px;}
}
[class*="st-key-hallazgo_"] [data-testid="stMarkdownContainer"] {margin-bottom: 0 !important;}
</style>
"""
