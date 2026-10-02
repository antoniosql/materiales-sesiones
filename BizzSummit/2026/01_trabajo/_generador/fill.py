"""Rellena el deck de Bizz Summit 2026 sobre base.pptx (estructura ya creada)."""
import copy, json
from pptx import Presentation
from pptx.util import Pt, Inches, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE

NAVY  = RGBColor(0x29, 0x2B, 0x45)
TEAL  = RGBColor(0x11, 0x9F, 0x9A)
PINK  = RGBColor(0xFF, 0x50, 0x9F)
YELL  = RGBColor(0xFF, 0xDA, 0x37)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREY  = RGBColor(0x59, 0x5B, 0x6B)

prs = Presentation("base.pptx")
mapa = json.loads(open("mapa.json").read())
S = {k: prs.slides[i] for i, k in enumerate(mapa["orden"])}


# ---------- helpers ----------
def g(slide, path):
    parts = [int(x) for x in str(path).split(".")]
    sh = slide.shapes[parts[0]]
    for p in parts[1:]:
        sh = sh.shapes[p]
    return sh


def _style(run, size=None, bold=None, color=None):
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color


def setp(shape, i, text, size=None, bold=None, color=None):
    """Reemplaza el texto de un parrafo conservando el formato del primer run."""
    para = shape.text_frame.paragraphs[i]
    runs = para.runs
    if not runs:
        raise ValueError(f"parrafo {i} sin runs en {shape.name}")
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)
    _style(runs[0], size, bold, color)


def setruns(shape, i, texts):
    """Conserva N runs (para titulos bicolor)."""
    para = shape.text_frame.paragraphs[i]
    runs = para.runs
    for r, t in zip(runs, texts):
        r.text = t
    for r in runs[len(texts):]:
        r._r.getparent().remove(r._r)


def addp(shape, text, like=-1, size=None, bold=None, color=None):
    """Duplica un parrafo existente al final y le pone texto."""
    tf = shape.text_frame
    src = tf.paragraphs[like]._p
    new = copy.deepcopy(src)
    src.getparent().append(new)
    setp(shape, len(tf.paragraphs) - 1, text, size, bold, color)


def keep_paras(shape, n):
    tf = shape.text_frame
    for para in list(tf.paragraphs)[n:]:
        para._p.getparent().remove(para._p)


def rm(shape):
    shape._element.getparent().remove(shape._element)


def hide(slide):
    slide._element.set("show", "0")


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def col2(slide, title_a, title_b, left_head, left_paras, right_head, right_paras,
         body=12):
    """Plantilla src12: dos columnas de texto con titulo a dos lineas."""
    t = g(slide, 1)
    setp(t, 0, title_a, size=36)
    setp(t, 1, title_b, size=36)
    for shp, head, paras in ((g(slide, 0), left_head, left_paras),
                             (g(slide, 3), right_head, right_paras)):
        keep_paras(shp, 2)
        setp(shp, 0, head, size=17, bold=True, color=NAVY)
        setp(shp, 1, paras[0], size=body)
        for extra in paras[1:]:
            addp(shp, extra, like=1, size=body)


def col3(slide, title_a, title_b_runs, cols):
    """Plantilla src13: titulo bicolor + tres columnas con cabecera."""
    t = g(slide, 0)
    setp(t, 0, title_a)
    setruns(t, 1, title_b_runs)
    for gi, (head, body) in zip((1, 2, 3), cols):
        setp(g(slide, f"{gi}.1.1"), 0, head, size=17)
        txt = g(slide, f"{gi}.0")
        keep_paras(txt, 2)
        setp(txt, 0, body[0])
        setp(txt, 1, body[1])


def sep(slide, a, b, size_b=48):
    for path, txt, size in (("1.1", a, None), ("0.1", b, size_b)):
        shp = g(slide, path)
        setp(shp, 0, txt, size=size)
        tf = shp.text_frame
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE


def planb(slide, titulo, detalle):
    setp(g(slide, 1), 0, "PLAN B")
    setp(g(slide, 2), 0, titulo)
    setp(g(slide, 5), 0, detalle)
    hide(slide)


def card4(slide, titulo, subtitulo, cards, big_size=None):
    """Plantilla src27: cabecera + cuatro tarjetas (orden visual izq->der)."""
    setp(g(slide, "11.0"), 0, titulo)
    setp(g(slide, "11.1"), 0, subtitulo)
    for pos, (gi, (big, mid, small)) in enumerate(zip((5, 8, 3, 9), cards)):
        c = NAVY if pos == 2 else None          # la 3a tarjeta es amarilla
        setp(g(slide, f"{gi}.0"), 0, big, size=big_size, color=c)
        setp(g(slide, f"{gi}.1"), 0, mid, color=c)
        setp(g(slide, f"{gi}.2"), 0, small, color=c)


def textbox(slide, x, y, w, h, text, size=11, bold=False, color=NAVY,
            align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
        r.font.name = "Open Sans Light"
    return tb


# ====================================================================
# 1 · PORTADA
# ====================================================================
s = S["portada"]
tit = g(s, 5)
tit.left, tit.top, tit.width, tit.height = Inches(1.55), Inches(2.55), Inches(10.2), Inches(2.0)
setp(tit, 0, "De la jungla de agentes al control plane", size=40)
addp(tit, "Gobierno real de Copilot Studio con Agent 365", size=24, bold=False)
sub = g(s, 6)
sub.left, sub.top, sub.width = Inches(1.66), Inches(4.85), Inches(10.2)
setp(sub, 0, "Antonio José Soto Rodríguez  ·  Microsoft MVP", size=24)
notes(s, "0:00–0:00:40. Sponsors a continuación mientras te conectas. No leas la slide.")

# ====================================================================
# 2 · SPONSORS — intacta
# ====================================================================
notes(S["sponsors"], "Slide obligatoria de la organización. No se toca. 20 segundos.")

# ====================================================================
# 3 · GANCHO
# ====================================================================
s = S["gancho"]
setp(g(s, "0.1"), 0, "Manos arriba")
q = g(s, 1)
q.left, q.top, q.width, q.height = Inches(1.19), Inches(2.60), Inches(6.60), Inches(2.20)
setp(q, 0, "¿Cuántos agentes", size=36)
setp(q, 1, "tenéis ahora mismo?", size=36)
setp(g(s, 2), 0, "Y ahora bajad la mano los que no podríais demostrarlo "
                 "con una captura en los próximos dos minutos.")
notes(s, "0:00:40–0:01:30. Dos preguntas seguidas, sin dejar respirar entre ellas. "
         "Si el público no levanta la mano, no insistas: «lo pregunto en todas las "
         "sesiones y el resultado es siempre el mismo».")

# ====================================================================
# 4 · DATO DE CONTRASTE
# ====================================================================
s = S["cifra"]
setp(g(s, 4), 0, "MILLONES", size=110)
for gi, (big, lab) in zip((1, 2, 3), (("Decenas", "de millones"),
                                      ("Meses", "de preview"),
                                      ("Cero", "inventariados"))):
    setp(g(s, f"{gi}.0"), 0, big, size=22)
    setp(g(s, f"{gi}.1"), 0, lab, size=10)
setp(g(s, 0), 0, "En los primeros meses de preview de Agent 365 aparecieron decenas de "
                 "millones de agentes en el registry. No eran proyecciones de adopción: "
                 "eran agentes que ya existían y ya estaban funcionando.")
notes(s, "0:01:30–0:02. La cifra no es el punto: el punto es que ya existían.")

# ====================================================================
# 5 · CONTRATO DE LA SESIÓN
# ====================================================================
col3(S["contrato"], "Lo que te llevas", ["el ", "lunes"], [
    ("Inventario",
     ["Saber cuántos agentes tienes y de quién es cada uno. El inventario ya existe: "
      "lo que falta es que alguien lo mire.",
      "Bloque 3 y demo 1."]),
    ("Cuatro carriles",
     ["Un modelo de preconfiguración que sustituye al comité de aprobación por agente. "
      "El maker no pide permiso: elige carril.",
      "Bloque 4, el núcleo de la sesión."]),
    ("Agentes externos",
     ["Qué hacer con lo que se construye fuera de Copilot Studio y cómo entra en el "
      "mismo control plane.",
      "Bloque 7 y demo 4."]),
])
notes(S["contrato"], "0:02–0:02:20. El contrato de la sesión: qué vas a poder hacer el lunes.")

# ====================================================================
# 6 · FRASOHOME
# ====================================================================
s = S["frasohome"]
setruns(g(s, 3), 0, ["Tres tiendas, e-commerce y fidelización. Hoy no hablamos de sus datos, sino de ",
                     "los agentes que alguien construyó encima",
                     " sin decírselo a nadie."])
setp(g(s, 6), 0, "FraSoHome · retail omnicanal")
notes(s, "0:02:20–0:02:30. Veinte segundos. Se menciona una vez y ya no se vuelve a explicar. "
         "Un solo proceso —devoluciones— atraviesa las cuatro demos.")

# ====================================================================
# 7 · APP VS AGENTE
# ====================================================================
col2(S["app_vs_agente"], "No es Shadow IT", "de siempre",
     "Una app de Power Apps",
     ["Expone datos. Actúa como la aplicación, con el alcance y las credenciales que "
      "alguien le configuró.",
      "El riesgo es de exposición: se resuelve mirando permisos."],
     "Un agente",
     ["Lee datos, decide, ejecuta acciones y gasta dinero. Y lo hace en nombre del usuario.",
      "El riesgo es de agencia. La diferencia con la Shadow IT clásica no es de grado: "
      "es de naturaleza."])
notes(S["app_vs_agente"], "0:02:30–0:04. Si vas tarde, esta slide se resume en una frase y se salta.")

# ====================================================================
# 8 · CUATRO RIESGOS DE RUNTIME
# ====================================================================
card4(S["riesgos"], "Cuatro riesgos de runtime", "Lo que un agente hace y una app no", [
    ("01", "Exposición de datos", "lee lo que el usuario ve, y a veces más"),
    ("02", "Abuso de privilegio", "actúa en nombre del usuario"),
    ("03", "Ejecución autónoma", "sin supervisión humana en el bucle"),
    ("04", "Tráfico saliente", "connectors y MCP sin allowlist"),
])
notes(S["riesgos"], "0:04. Rápido: una línea por riesgo, sin detenerse.")

# ====================================================================
# 9 · LOS CINCO SÍNTOMAS
# ====================================================================
s = S["sintomas"]
tsx = g(s, 0)
tsx.left, tsx.width = Inches(1.19), Inches(10.24)
setp(tsx, 0, "Los cinco síntomas de la jungla")
tsx.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
sintomas = [
    (6, "El Default es el vertedero", "vive todo ahí y nadie lo mira"),
    (4, "Sin autenticación de Entra ID", "agentes publicados en canal abierto"),
    (2, "Knowledge sources abiertos", "sitios de SharePoint sin acotar"),
    (16, "Nadie paga los créditos", "consumo sin centro de coste asignado"),
    (14, "El maker ya no está", "cambió de equipo hace seis meses"),
]
for gi, head, sub_ in sintomas:
    setp(g(s, f"{gi}.0"), 0, head)
    setp(g(s, f"{gi}.1"), 0, sub_)
for path in ("20", "12", "11"):          # sexto hueco + su punto en la línea (orden descendente)
    rm(g(s, path))
notes(s, "0:04–0:05:30. Léelos contando con los dedos, medio segundo entre cada uno. "
         "«Si habéis marcado tres o más, no tenéis un problema de tecnología: tenéis una jungla.» "
         "PRIMERA repetición de la frase ancla en el quinto síntoma.")

# ====================================================================
# 10 · VISIBILIDAD ANTES QUE CONTROL
# ====================================================================
s = S["visibilidad"]
big = g(s, 3)
big.top, big.height = Inches(1.35), Inches(2.75)
setp(big, 0, "Visibilidad", size=52)
setp(big, 1, "antes que", size=52)
addp(big, "control", size=52)
cuerpo = g(s, 4)
cuerpo.top, cuerpo.height = Inches(4.30), Inches(1.30)
setp(cuerpo, 0, "Bloquear connectors y cerrar la creación de entornos funciona seis "
                 "semanas. Luego los makers se van a otras herramientas y el problema "
                 "no desaparece: se vuelve invisible.")
notes(s, "0:05:30–0:07. CHECKPOINT 1: deberías estar en 11:07. "
         "Transición: «si el control sin visibilidad no funciona, ¿por dónde se empieza? "
         "Por saber quién es cada agente».")

# ====================================================================
# 11 · LAS TRES CAPAS  ⭐
# ====================================================================
col3(S["tres_capas"], "Tres capas", ["de ", "gobierno"], [
    ("Identidad",
     ["¿Quién es este agente y de quién es?",
      "Entra Agent ID · Agent 365 Registry · Microsoft 365 Admin Center"]),
    ("Plataforma",
     ["¿Dónde vive, qué puede tocar y cómo se promociona?",
      "Power Platform Admin Center: entornos, environment groups, Managed Environments, "
      "DLP y ACP, pipelines"]),
    ("Datos y runtime",
     ["¿Qué lee, qué devuelve y qué hace mientras corre?",
      "Purview: etiquetas, DLP, DSPM for AI y auditoría · Defender: detección y "
      "protección en runtime"]),
])
notes(S["tres_capas"], "0:07–0:10. LA SLIDE CENTRAL. Déjala puesta y vuelve a ella con el "
                       "puntero en cada demo. Todo lo que viene después cuelga de aquí.")

# ====================================================================
# 12 · TRES MENSAJES + LICENCIAMIENTO
# ====================================================================
s = S["mensajes"]
setp(g(s, "1.0"), 0, "Tres mensajes")
setp(g(s, "1.1.0"), 0, "Antes de seguir")
setp(g(s, 2), 0, "Agent 365 no sustituye al PPAC")
setp(g(s, 4), 0, "La capa de datos ya la tienes con E5")
setp(g(s, 6), 0, "Gobierno ≠ ejecución: dos facturas")
textbox(s, 6.55, 4.15, 5.35, 0.32, "Licenciamiento, sin rodeos",
        size=15, bold=True, color=TEAL)
lic = textbox(s, 6.55, 4.62, 5.35, 1.95,
        "Por usuario: quien interactúa, posee, gestiona o patrocina agentes.\n"
        "Base E5, o Defender + Purview Suite FLW. Incluido en M365 E7.\n"
        "E3 + Copilot no es elegible.\n"
        "Cubre gobierno, no ejecución: los créditos van aparte.",
        size=12)
for _p in lic.text_frame.paragraphs:
    _p.space_after = Pt(7)
notes(s, "0:08:30–0:10. Di el licenciamiento rápido y sin disculparte: es la pregunta "
         "número uno del Q&A. «Apuntad la última línea, que es la que os salva de "
         "prometer algo que luego no podéis entregar.»")

# ====================================================================
# 13 · INVENTARIO E IDENTIDAD
# ====================================================================
col2(S["inventario"], "El inventario", "ya existe",
     "Entra Agent ID",
     ["Desde julio de 2026, Copilot Studio crea automáticamente un Entra Agent ID para "
      "cada agente nuevo, y ya no se puede desactivar a nivel de entorno.",
      "La pregunta no es cómo construir el inventario. Es quién lo mira, y con qué cadencia."],
     "Registry y PPAC",
     ["Registry · Access Control · Visualization · Interoperability · Security. La columna "
      "Risks consolida señales de Defender, Entra y Purview donde estén configuradas.",
      "En el PPAC, Inventory, Usage, Monitor y Actions ya sustituyen al inventario del CoE "
      "Starter Kit. Si lo mantienes solo para inventariar, déjalo.",
      "Lo que no se onboarde solo aparece como detección de Shadow AI: lo detectas y lo "
      "restringes, pero no lo gobiernas como identidad."], body=11)
notes(S["inventario"], "0:10–0:13. La última frase planta la semilla de la demo 4: "
                       "«guardad esa frase, que volvemos a ella en la última demo».")

# ====================================================================
# 14–15 · DEMO 1
# ====================================================================
sep(S["sep_demo1"], "DEMO 1", "¿Quién es?")
notes(S["sep_demo1"], "0:13–0:16:30 · riesgo bajo.\n"
      "Beat 1 (45\"): Álvaro pregunta en Teams por la devolución de un cliente Oro. Responde bien, citado.\n"
      "Beat 2 (1:15\"): All agents, ordenar por Risks, abrir el agente: identidad, propietario VACÍO, permisos, 40 usuarios.\n"
      "Beat 3 (45\"): PPAC Inventory: vive en Default, sin Managed Environment, créditos sin asignar.\n"
      "Beat 4 (45\"): «Lo creó Marta el 17 de marzo de 2026. Marta pasó a e-commerce en julio. "
      "Nadie se lo dijo a este agente.»\n"
      "CHECKPOINT 2: 11:16:30.")
planb(S["planb_demo1"], "Demo 1 — capturas",
      "Sustituir por las capturas anotadas de All agents y del PPAC")

# ====================================================================
# 16 · CARRILES, NO COMITÉS
# ====================================================================
col2(S["comite"], "Carriles,", "no comités",
     "El comité no escala",
     ["Un comité de aprobación por agente no escala a trescientos agentes, y convierte a "
      "IT en el cuello de botella del que luego todos se quejan.",
      "Lo primero que monta todo el mundo, y lo primero que hay que desmontar."],
     "El carril es preconfiguración",
     ["El control ya está aplicado por el entorno donde nace el agente. El maker no pide "
      "permiso: elige carril.",
      "Mapea con las zonas de Microsoft —Citizen, Partnered, Professional— pero con cuatro "
      "escalones, porque el playground merece existir formalmente."])
notes(S["comite"], "0:16:30–0:18. Bloque protegido: si hay que recortar, se recorta de otro sitio.")

# ====================================================================
# 17 · TABLA DE CARRILES  ⭐
# ====================================================================
s = S["carriles"]
setp(g(s, "4.0"), 0, "Los cuatro carriles")
setp(g(s, "4.1"), 0, "El maker no pide permiso: elige carril")
for path in ("11", "10", "9", "8", "7", "6", "5", "3"):
    rm(g(s, path))

FILAS = [
    ("", "Playground", "Equipo", "Producción", "Enterprise"),
    ("Entorno", "Default endurecido", "Dev por área, en group", "Dev/Test/Prod dedicados", "Dev/Test/Prod + DR"),
    ("Datos", "Solo del propio usuario", "Del área, sin sensibles", "De negocio, con etiquetas", "Regulados"),
    ("Connectors", "Allowlist mínima, sin HTTP", "Allowlist de área", "Allowlist + endpoint filtering", "Allowlist explícita"),
    ("Autenticación", "Entra ID, sin canal anónimo", "Entra ID", "Entra ID + Conditional Access", "+ Information Barriers"),
    ("Evaluaciones", "Opcional", "Test set mínimo", "Obligatorio + regresión", "Regresión en CI/CD"),
    ("Agentes externos", "No permitidos", "No permitidos", "Onboarding vía Agent 365 SDK", "SDK + revisión de seguridad"),
    ("Propietario", "El creador", "Maker nombrado", "Owner de negocio + técnico", "Owner + backup + on-call"),
]
COLW = [1.62, 2.33, 2.33, 2.33, 2.33]
gf = s.shapes.add_table(len(FILAS), 5, Inches(1.19), Inches(2.16),
                        Inches(sum(COLW)), Inches(4.30))
tbl = gf.table
tbl.first_row = True
tbl.horz_banding = True
for c, w in zip(tbl.columns, COLW):
    c.width = Inches(w)
tbl.rows[0].height = Inches(0.44)
for r in list(tbl.rows)[1:]:
    r.height = Inches(0.55)
for ri, fila in enumerate(FILAS):
    for ci, val in enumerate(fila):
        cell = tbl.cell(ri, ci)
        cell.margin_left = cell.margin_right = Inches(0.08)
        cell.margin_top = cell.margin_bottom = Inches(0.04)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid()
        if ri == 0:
            cell.fill.fore_color.rgb = NAVY
        elif ci == 0:
            cell.fill.fore_color.rgb = RGBColor(0xEC, 0xF6, 0xF5)
        else:
            cell.fill.fore_color.rgb = WHITE if ri % 2 else RGBColor(0xF7, 0xF7, 0xF9)
        p = cell.text_frame.paragraphs[0]
        run = p.add_run()
        run.text = val
        f = run.font
        f.name = "Open Sans Light"
        f.size = Pt(10.5 if ri else 12)
        f.bold = ri == 0 or ci == 0
        f.color.rgb = WHITE if ri == 0 else (TEAL if ci == 0 else NAVY)
notes(s, "0:18–0:21:30. NO la leas entera: se lee columna a columna. Recorre cinco filas "
         "en voz alta y di «esta slide no es para leerla aquí, es para hacerle una foto». "
         "Deja tres segundos de silencio: lo van a hacer.\n"
         "FraSoHome: los dos agentes van al carril Producción; lo que cambia es la puerta "
         "por la que entran.")

# ====================================================================
# 18 · LAS TRES REGLAS DURAS
# ====================================================================
s = S["reglas"]
setp(g(s, "3.0"), 0, "Las tres reglas duras")
setp(g(s, "3.1"), 0, "No negociables")
setp(g(s, 6), 0, "Default endurecido")
setp(g(s, 5), 0, "Propietario nombrado")
setp(g(s, 7), 0, "Promoción = evento")
for x, txt in ((1.63, "Managed Environment, sin chat anónimo y sin HTTP. Pero no lo apagues: "
                      "cerrar el playground echa la experimentación fuera del tenant."),
               (5.21, "Campo obligatorio, no campo bonito. Un agente sin propietario nombrado "
                      "no es un agente: es una incidencia esperando fecha."),
               (8.80, "Subir de carril exige revisión de datos, connectors, evaluaciones y "
                      "coste. Es lo que automatiza el flujo de aprobación de Agent 365.")):
    textbox(s, x, 5.84, 2.90, 0.95, txt, size=10.5, color=WHITE, align=PP_ALIGN.CENTER)
notes(s, "0:22–0:23:15. SEGUNDA repetición de la frase ancla en la regla 2. "
         "Cierra con environment groups, Settings Enforcer y la verdad incómoda de que "
         "casi todo esto pide Managed Environments, que cuesta licencia.")

# ====================================================================
# 19–21 · CONTROL DE DATOS + DEMO 2
# ====================================================================
col2(S["datos"], "Qué puede leer", "y qué devuelve",
     "DLP y Advanced Connector Policies",
     ["La DLP gobierna autenticación, canales, connectors de Copilot Studio y endpoint "
      "filtering en HTTP, SharePoint y sitios web públicos.",
      "El punto fino que casi nadie aplica: endpoint filtering sobre el connector de "
      "knowledge source de SharePoint.",
      "Las ACP cambian el modelo: allowlist en lugar de clasificación, y bloquean "
      "servidores MCP que la DLP clásica no bloquea. Hoy, solo por environment group."],
     "Purview y Defender",
     ["Etiquetas de confidencialidad con cifrado: el agente no extrae contenido salvo que "
      "el usuario tenga derechos EXTRACT y VIEW. El control que más gente ignora que ya tiene.",
      "DLP de Purview: bloquea la respuesta cuando hay coincidencia de información sensible "
      "en el prompt o en la respuesta.",
      "Prerrequisito que hunde proyectos: auditoría unificada activa y connector de M365 en "
      "Defender for Cloud Apps fluyendo. Sin eso, la protección de runtime no existe."],
     body=11)
notes(S["datos"], "0:24–0:26. Teoría de apoyo. No te enamores de esta parte.")

sep(S["sep_demo2"], "DEMO 2", "¿Qué lee?")
notes(S["sep_demo2"], "0:26–0:29:30 · RIESGO ALTO.\n"
      "En un summit esta demo VA GRABADA salvo que la hayas probado en la sala esa mañana.\n"
      "Beat 1 (1:15\"): endpoint filtering — el sitio de Prevención de Pérdidas no existe "
      "para el agente. No dice «no tienes permiso»: no lo ve.\n"
      "Beat 2 (1:30\"): «¿A qué cuenta se reembolsó DEV-2026-0418?» → IBAN → Purview bloquea. "
      "Deja el bloqueo en pantalla dos segundos antes de hablar.\n"
      "Beat 3 (45\"): «Nadie ha tenido que revisar este agente para que esto pase. "
      "El control estaba en la capa, no en el agente.»")
planb(S["planb_demo2"], "Demo 2 — vídeo de 60″",
      "Se graba por defecto: endpoint filtering y bloqueo por DLP de Purview")

# ====================================================================
# 22–24 · CICLO DE VIDA + DEMO 3
# ====================================================================
col3(S["ciclo_vida"], "Ciclo de vida", ["y ", "calidad"], [
    ("ALM sin ceremonia",
     ["Soluciones, pipelines de Power Platform e integración con Git. Dev → Test → Prod, "
      "gestionadas en Prod y solo gestionadas.",
      "Todo cambio en instrucciones, prompts, tools, knowledge sources o connectors es un "
      "cambio de producción. No es «editar un texto»."]),
    ("Componentes",
     ["No gobiernas trescientos agentes: gobiernas veinte componentes que esos trescientos "
      "reutilizan. Disclaimers, tono, tools autorizadas, escalado a humano.",
      "El maker va más rápido porque usa lo gobernado. Ese es el argumento que convence a "
      "negocio; el de seguridad no ha convencido nunca a nadie que no sea de seguridad."]),
    ("Evaluaciones",
     ["Test sets multi-turno en GA, General Quality Grader en el panel de pruebas y API REST "
      "de Power Platform para regresión en CI/CD.",
      "Miden rendimiento y precisión, no ética ni seguridad. Umbral: 20 casos reales y una "
      "regresión que no baje de línea base antes de Producción."]),
])
notes(S["ciclo_vida"], "0:29:30–0:32. La regla de versionado vive en la component collection. "
                       "«Acordaos, que en cuarenta segundos veis lo que pasa cuando no está "
                       "en el componente sino en el agente.»")

sep(S["sep_demo3"], "DEMO 3", "¿Funciona?")
notes(S["sep_demo3"], "0:32–0:34:30 · riesgo medio.\n"
      "Beat 1 (1:00\"): 20 casos → 19 verde, 1 rojo. Esperado 45 días naturales, devuelto 30. "
      "Cita FS-KB-02 v1.2, obsoleta.\n"
      "Beat 2 (1:00\"): Agent Change Tracker. El 12 de septiembre Marta borró la regla de "
      "versionado. Diff visible. «No hizo nada malo: estaba limpiando instrucciones que le "
      "parecían redundantes.»\n"
      "Beat 3 (30\"): «Sé qué cambió y sé si sigue funcionando. Eso es un servicio. "
      "Lo otro era un piloto.»\n"
      "CHECKPOINT 3: 11:34:30.")
planb(S["planb_demo3"], "Demo 3 — pregrabada",
      "Resultados del test set y diff del Agent Change Tracker")

# ====================================================================
# 25–28 · AGENTE EXTERNO + DEMO 4
# ====================================================================
col2(S["sdk"], "El Agent 365 SDK", "qué es, qué no",
     "Qué es",
     ["Conecta un agente que tú ya tienes y ya ejecutas con Agent 365, cuando necesita "
      "acceso a nivel de código a identidad, observabilidad, tooling o notificaciones.",
      "Cuatro capacidades: identidad en Entra, observabilidad con OpenTelemetry, tooling "
      "con los MCP gobernados de Work IQ y notificaciones. Python, JavaScript y .NET.",
      "Flujo de onboarding en cuatro etapas: Register → Extend → Validate → Operate."],
     "Qué no es",
     ["No construye agentes. No los hospeda. No orquesta pasos. No ejecuta herramientas.",
      "Tú sigues siendo dueño de las tres capas: modelo, framework o runtime, y host.",
      "Ninguna organización real va a construir el cien por cien de sus agentes en Copilot "
      "Studio. La pregunta de gobierno no es cómo evitar que existan: es cómo entran en el "
      "mismo control plane."], body=11)
notes(S["sdk"], "0:34:30–0:36:30. Si vas tarde, sáltate esta slide y explícalo dentro de la demo.")

s = S["blueprint"]
setruns(g(s, 3), 0, ["El blueprint de identidad es una definición aprobada por IT ",
                     "de la que heredan todos los agentes",
                     " creados a partir de ella."])
setp(g(s, 6), 0, "Gobierna la plantilla")
notes(s, "Misma idea que las component collections, aplicada a la capa de identidad. "
         "Un agente externo puede llegar al carril Producción, pero solo con blueprint, "
         "identidad, telemetría y propietario. No hay atajo.")

sep(S["sep_demo4"], "DEMO 4", "El otro agente", size_b=44)
notes(S["sep_demo4"], "0:36:30–0:40:30 · riesgo medio-alto · ES EL CIERRE.\n"
      "Precondición: enseñar fs-triage-devoluciones funcionando y AUSENTE de All agents.\n"
      "Beat 1 (1:00\"): «añade observabilidad a este agente» → instrument-observability. "
      "Enseña el diff: es aditivo.\n"
      "Beat 2 (1:15\"): add-workiq-tools para Mail y Word. AVISO: requiere permisos "
      "delegados; con S2S la skill se salta sola y en silencio.\n"
      "Beat 3 (1:15\"): EN VIVO SÍ O SÍ. All agents con los dos agentes. Silencio.\n"
      "Beat 4 (30\"): «El control plane no pregunta con qué lo construiste. Pregunta quién "
      "eres, qué tocas y quién responde por ti.»")
planb(S["planb_demo4"], "Demo 4 — beats 1 y 2",
      "Terminal pregrabado. El beat 3, los dos agentes en All agents, va en vivo sí o sí")

# ====================================================================
# 29 · CADENCIA OPERATIVA
# ====================================================================
card4(S["cadencia"], "La cadencia operativa", "Sin esto, los carriles son un PowerPoint", [
    ("Semanal", "Admin de plataforma", "columna Risks y agentes sin propietario"),
    ("Mensual", "CoE y finanzas", "consumo por carril y agentes sin uso"),
    ("Trimestral", "Plataforma y seguridad", "regresión de evaluaciones y allowlist"),
    ("Anual", "Owners de negocio", "revalidación de carril y de propietario"),
], big_size=20)
notes(S["cadencia"], "0:40:30–0:42:30. FinOps en tres líneas: créditos aparte, centro de coste "
                     "por agente de Producción, y un agente sin sponsor que pague es un agente "
                     "que se apaga.\n"
                     "L1/L2/L3: ¿quién responde cuando un agente da una respuesta mala a un "
                     "cliente? Casi nadie lo tiene definido y es la PRIMERA crisis real.\n"
                     "TERCERA repetición de la frase ancla.")

# ====================================================================
# 30 · CIERRE
# ====================================================================
s = S["cierre"]
setp(g(s, 3), 0, "Volved")
setp(g(s, 3), 1, "y contad")
setp(g(s, 4), 0, "Abrid All agents y contad. La cifra os va a sorprender, y eso es una "
                 "buena noticia: significa que el inventario ya lo tenéis. Lo que falta "
                 "es decidir los carriles.")
notes(s, "0:42:30–0:43. Volvemos al gancho del minuto uno.")

# ====================================================================
# 31 · RECURSOS
# ====================================================================
col2(S["recursos"], "Recursos", "y checklist",
     "Documentación",
     ["aka.ms/mcs_sg — Copilot Studio Governance and Security Guide",
      "aka.ms/powerplatform/alm — ALM con Power Platform",
      "aka.ms/PowerCAT/AIWebinars — Power CAT AI Webinars",
      "github.com/microsoft/Power-CAT-Copilot-Studio-Kit — Copilot Agent Kit"],
     "Agent 365",
     ["Microsoft Agent 365 — página de producto y Licensing FAQ",
      "Agent 365 SDK overview y Agent 365 Skills — Microsoft Learn",
      "Quickstart: Connect an existing agent to Agent 365",
      "Copilot Studio: automatizar evaluaciones con la API de Power Platform"])
notes(S["recursos"], "0:43–0:44. Aquí va el QR de la checklist 30/60/90. «Es una página; no "
                     "hace falta que apuntéis nada de la tabla de carriles.»\n"
                     "PENDIENTE: insertar el QR de la checklist en el hueco derecho.")

# ====================================================================
# 32 · Q&A
# ====================================================================
s = S["qa"]
setp(g(s, 2), 0, "¿Alguna", size=56)
setp(g(s, 2), 1, "pregunta?", size=56)
setp(g(s, 3), 0, "Y si no las hay, os hago yo la que siempre me hacen")
notes(s, "0:44–0:50. CHECKPOINT 4: a las 11:44 estás aquí, hayas terminado o no.\n"
         "Las que caen: E3+Copilot no es elegible · sustituye al CoE para inventario · "
         "terceros por Registry Sync o SDK · el SDK no obliga a cambiar de framework · "
         "portátil de un dev sí con identidad y telemetría · gobierno por usuario + créditos "
         "aparte · ACP en preview y por environment group · bloquear la creación es el error "
         "más caro.\n"
         "Si nadie pregunta: «¿por dónde empiezo el lunes si solo tengo una hora?» → "
         "exportar All agents y filtrar por sin propietario.")

notes(S["gracias"], "Slide de la organización con el QR de feedback. Pídelo explícitamente.")
notes(S["contacto"], "Cierre institucional.")

prs.save("BizzSummit2026_De_la_jungla_al_control_plane.pptx")
print("OK")
