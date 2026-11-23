#!/usr/bin/env python3
"""Generates the ELCON redesign pages into site/. Content comes from source/*.txt (crawled elcon.si)."""
import json, re, html, pathlib, time
VER = str(int(time.time()))
REF_SNIPPET = """<script>
(function () {
  if (!/[?&]r=/.test(location.search)) return;
  var s = document.createElement('script');
  s.async = true;
  s.referrerPolicy = 'no-referrer';
  s.setAttribute('data-landing', location.href);
  s.src = 'https://phplaravel-758037-6569212.cloudwaysapps.com/v/script.js';
  document.head.appendChild(s);
})();
</script>"""


ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "source"
OUT = ROOT / "site"

def clean(s):
    s = s.replace("—", ", ").replace(" – ", ", ").replace("–", "-")
    s = re.sub(r",\s*,", ",", s)
    fixes = {"Elecrical": "Electrical", "Elelctrical": "Electrical", "calander": "calender", "MAGNESTIA": "MAGNESITA",
             "sIEMENS": "SIEMENS", "Cinkana": "Cinkarna", "SIMAMICS": "SINAMICS", "integratin ": "integration ",
             "chanel drivers": "channel drivers", "Ospitale die Cadore": "Ospitale di Cadore", "DIE CADORE": "DI CADORE"}
    for a, b in fixes.items():
        s = s.replace(a, b)
    return s.strip(" ,")

def years(y):
    y = re.sub(r'\s*·\s*', ' ', y)
    y = re.sub(r'\s*–\s*', '–', y)
    return html.escape(re.sub(r'\s+', ' ', y).strip())

def esc(s):
    return html.escape(clean(s), quote=False)

ON = ' class="on"'
CONTAIN = ' class="contain"'
ACT = ' class="active"'
def avatar(n, im):
    return f'<img src="assets/img/{im}" alt="{n}">' if im else '<span class="ini">' + ''.join(w[0] for w in n.split()) + '</span>'
ARR = '<svg class="arr" viewBox="0 0 18 18" fill="none"><path d="M3 9h12M10 4l5 5-5 5" stroke="currentColor" stroke-width="1.6"/></svg>'
CHEV = '<svg class="chev" viewBox="0 0 10 10" fill="none"><path d="M1 3l4 4 4-4" stroke="currentColor" stroke-width="1.5"/></svg>'
X = '<svg viewBox="0 0 22 22" fill="none"><path d="M6 6l10 10M16 6L6 16" stroke="currentColor" stroke-width="1.6"/></svg>'
CHECK = '<svg viewBox="0 0 22 22" fill="none"><path d="M4 11.5l4.5 4.5L18 6" stroke="#D9CB1E" stroke-width="2"/></svg>'

MARKETS = [
    dict(slug="chemical", file="markets_chemical", name="Chemical", title="Chemical industry", hero="markets_chemical_naslovna.webp",
         imgs=["Chemical1.webp", "Chemical2.webp"], case_imgs=[["Cinkarna_2.webp", "Cinkarna_1.webp", "Chemical1.webp"]],
         short="Higher motor powers and a large number of sensors and actuators, handled both in electrical projects and in software."),
    dict(slug="energy", file="markets_energy", name="Energy", title="Energy, oil and gas", hero="markets_oil_and_gas_naslovna.webp",
         imgs=["Energy.webp", "Energy-2.webp"], case_imgs=[["TurkStream-1.webp", "TurkStream-3.webp", "TurkStream-2.webp", "TurkStream-4.webp"]],
         short="Oil and gas projects demand a high level of operational reliability, from documentation to implementation and testing."),
    dict(slug="papermills", file="markets_papermills", name="Papermills", title="Paper mills", hero="markets_papermills_naslovna.webp",
         imgs=["Papermills-1.webp", "Papermills-2.webp"],
         case_imgs=[["MM-Kolicevo-1.webp", "MM-Kolicevo-3.webp", "MM-Kolicevo-2.webp"], ["Papirnica-Vevce-4.webp", "Papirnica-Vevce-1.webp", "Papirnica-Vevce-3.webp", "Papirnica-Vevce-2.webp"]],
         short="The reliability of the paper or board machine is essential. Downtimes must be as short as possible."),
    dict(slug="cement", file="markets_refractory-and-cement", name="Refractory and Cement", title="Refractory and cement", hero="markets_refractory_and_cement_naslovna.webp",
         imgs=["RefractoryCement1.webp", "RefractoryCement2.webp"], case_imgs=[["RHI-Magnesita-4.webp", "RHI-Magnesita-1.webp", "RHI-Magnesita-3.webp"]],
         short="Robust machines, high motor ratings and large volumes of material, guarded to protect operators and equipment."),
]
REFS = json.load(open(SRC / "refs.json", encoding="utf-8"))
REFKEY = {"chemical": "chemical", "energy": "energy", "papermills": "papermills", "cement": "refractory-and-cement"}

def parse_market(fname):
    lines = (SRC / f"{fname}.txt").read_text(encoding="utf-8").split("\n")
    i = lines.index("What ELCON Does")
    end = lines.index("Quick links")
    L = lines[i:end]
    def between(a, b):
        ia = L.index(a); ib = L.index(b, ia + 1)
        return L[ia + 1:ib]
    d = {}
    d["intro"] = between("What ELCON Does", "Electrical Design")
    d["design"] = between("Electrical Design", "Programming")
    d["prog"] = between("Programming", "Pain Points")
    d["pain"] = between("Pain Points", "Our Solution")
    d["sol"] = between("Our Solution", "CASE STUDY")
    cases, cur = [], None
    k = L.index("CASE STUDY")
    while k < len(L):
        ln = L[k]
        if ln == "CASE STUDY":
            cur = {"title": L[k + 1], "paras": []}; cases.append(cur); k += 2; continue
        if ln == "REFERENCES":
            break
        cur["paras"].append(ln); k += 1
    d["cases"] = cases
    b = L.index("Book a Free Call")
    d["cta"] = " ".join(L[b + 1:]).replace(" .", ".")
    return d

def mega():
    mk = "".join(f'<a href="market-{m["slug"]}.html">{m["name"]}<span>{esc(m["short"][:60].rsplit(" ",1)[0])}</span></a>' for m in MARKETS)
    mki = "".join(f'<img src="assets/img/{m["hero"]}" alt=""{ON if i == 0 else ""}>' for i, m in enumerate(MARKETS))
    sv = [("service-package.html", "Complete electrical package", "From plans to commissioning and As Built documentation", "eletrical_design_naslovna.webp"),
          ("service-design.html", "Electrical design", "Plans in ePlan or WSCAD, for new builds and retrofits", "procedure_phase_2.webp"),
          ("service-software.html", "Software development", "Siemens PCS7, SIMATIC Batch, TIA Portal and SIMIT", "Software-development_naslovna.webp")]
    svl = "".join(f'<a href="{h}">{t}<span>{s}</span></a>' for h, t, s, _ in sv)
    svi = "".join(f'<img src="assets/img/{im}" alt=""{ON if i == 0 else ""}>' for i, (_, _, _, im) in enumerate(sv))
    return f'''<div class="mega" id="mega-services"><div class="mega-list">{svl}</div><div class="mega-media">{svi}</div></div>
<div class="mega" id="mega-markets"><div class="mega-list">{mk}</div><div class="mega-media">{mki}</div></div>
<div class="mega-scrim"></div>'''

def page(fname, title, body, active="", home=False, desc="ELCON d.o.o., automation company for the process industry. Siemens Solution Partner since 2009."):
    def a(href, label, key):
        return f'<a href="{href}"{ACT if active == key else ""}>{label}</a>'
    mm_markets = "".join(f'<a class="sub" href="market-{m["slug"]}.html">{m["name"]}</a>' for m in MARKETS)
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="noindex">
<link rel="icon" href="assets/img/favicon.png">
<link rel="preload" href="assets/fonts/ABCWhyteInktrap-Medium-Trial.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/ABCWhyte-Regular-Trial.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/site.css?v={VER}">
{REF_SNIPPET}
</head>
<body>
{'<div class="loader"><img src="assets/img/elcon_logo.webp" alt="ELCON"><div class="bar"><i></i></div></div>' if home else ''}
<header class="nav">
  <a class="logo" href="index.html" aria-label="ELCON home"><img src="assets/img/elcon_logo.webp" alt="ELCON, Company for Automation" width="237" height="58"></a>
  <nav class="nav-links">
    {a("about.html","About us","about")}
    <div class="has-mega" data-mega="mega-services"><a href="services.html"{' class="active"' if active=="services" else ''}>Services {CHEV}</a></div>
    <div class="has-mega" data-mega="mega-markets"><a href="markets.html"{' class="active"' if active=="markets" else ''}>Markets {CHEV}</a></div>
    {a("about.html#team","Team","team")}
    {a("contact.html","Contact","contact")}
  </nav>
  <div class="nav-cta"><a class="nav-tel" href="tel:+38617240040">+386 1 724 00 40</a><a class="btn" href="contact.html#call">Book a free call {ARR}</a>
  <button class="burger" aria-label="Menu"><span></span><span></span></button></div>
</header>
{mega()}
<div class="mmenu">
  <div class="grp"><a href="index.html">Home</a></div>
  <div class="grp"><a href="about.html">About us</a></div>
  <div class="grp"><a href="services.html">Services</a><a class="sub" href="service-package.html">Complete electrical package</a><a class="sub" href="service-design.html">Electrical design</a><a class="sub" href="service-software.html">Software development</a></div>
  <div class="grp"><a href="markets.html">Markets</a>{mm_markets}</div>
  <div class="grp"><a href="contact.html">Contact</a></div>
  <a class="btn" href="contact.html#call">Book a free call {ARR}</a>
</div>
<main>
{body}
</main>
{footer()}
<script src="assets/vendor/gsap.min.js"></script>
<script src="assets/vendor/ScrollTrigger.min.js"></script>
<script src="assets/vendor/lenis.min.js"></script>
<script src="assets/js/site.js?v={VER}"></script>
</body>
</html>'''
    (OUT / fname).write_text(doc, encoding="utf-8")

def cta(heading="Let’s talk about your plant.", text="Retrofit, new line or a system nobody can maintain anymore. Tell us what you are running and we will tell you how we would approach it."):
    paths = "".join(f'<path d="M{-100+i*90} 900 C {200+i*60} {500-i*20}, {700+i*40} {700-i*30}, {1700+i*30} {80+i*40}"/>' for i in range(14))
    return f'''<section class="cta sec" id="talk">
  <svg class="cta-lines" viewBox="0 0 1600 900" preserveAspectRatio="none">{paths}</svg>
  <div class="wrap" style="position:relative">
    <h2 class="d1" data-split>{heading}</h2>
    <div class="cta-row">
      <p class="lead" data-reveal>{text}</p>
      <div class="hero-actions" data-reveal><a class="btn light" href="contact.html#call">Book a free call {ARR}</a></div>
    </div>
  </div>
</section>'''

def footer():
    return f'''<footer class="foot">
  <div class="foot-top">
    <div>
      <a class="logo" href="index.html"><img src="assets/img/elcon_logo.webp" alt="ELCON"></a>
      <div class="foot-contact">
        <span>Ljubljanska cesta 80, 1230 Domžale, Slovenia</span>
        <a href="tel:+38617240040">+386 1 724 00 40</a>
        <a href="mailto:info@elcon.si">info@elcon.si</a>
      </div>
      <div class="foot-badges"><img src="assets/img/siemens-solution-partner-logo.webp" alt="Siemens Solution Partner"><img src="assets/img/ISO_9001_logo.webp" alt="ISO 9001"></div>
    </div>
    <div><h4>Services</h4><ul><li><a href="service-package.html">Complete electrical package</a></li><li><a href="service-design.html">Electrical design</a></li><li><a href="service-software.html">Software development</a></li></ul></div>
    <div><h4>Markets</h4><ul>{"".join(f'<li><a href="market-{m["slug"]}.html">{m["name"]}</a></li>' for m in MARKETS)}</ul></div>
    <div><h4>Company</h4><ul><li><a href="about.html">About us</a></li><li><a href="about.html#team">Team</a></li><li><a href="contact.html">Contact</a></li><li><a href="https://maps.google.com/?q=Ljubljanska+cesta+80,+1230+Domžale" target="_blank" rel="noopener">How to reach us</a></li></ul></div>
  </div>
  <div class="foot-bot"><span>© ELCON d.o.o. All rights reserved 2026</span><span><a href="#">Cookies</a> · <a href="#">Authors</a></span></div>
</footer>'''

# ---------------- shared blocks ----------------
PROCESS = [
    ("Requirements analysis", "Reviewing project input data, including technical meetings, P&I diagrams, functional expectations and client process requirements.", "procedure_phase_1b.webp", True),
    ("Project documentation", "Preparation of basic and detailed design documentation, including functional descriptions, design specifications and other technical documents.", "procedure_phase_1a.webp", True),
    ("Electrical design and software development", "Complete electrical design and development of software logic, including PLC, HMI and SCADA programming according to approved specifications.", "pcs7_applications.webp", True),
    ("Cabinet assembly", "Assembly of the electrical cabinet, installation of all components, wiring and labeling.", "eletrical_design_naslovna.webp", False),
    ("Testing of cabinets and software", "Execution of FAT, testing of the electrical cabinet and control program using a digital twin.", "digital_twin.webp", True),
    ("Installation and technical acceptance", "Installation of equipment, commissioning, SAT (Site Acceptance Test), operator training and final project handover.", "procedure_phase_3.webp", False),
    ("After-sales support and upgrades", "Post-delivery technical support, troubleshooting, maintenance services and implementation of future upgrades or system improvements.", "workers-control-room.webp", False),
]

def process_block(title="Seven steps from P&ID to a running plant."):
    steps = "".join(f'<div class="proc-step"><div class="big">{i+1:02d}</div><h3>{t}</h3><p>{p}</p></div>' for i, (t, p, _, _) in enumerate(PROCESS))
    imgs = "".join(f'<img src="assets/img/{im}" alt=""{CONTAIN if c else ""}>' for (_, _, im, c) in PROCESS)
    bars = "".join("<i><b></b></i>" for _ in PROCESS)
    lst = "".join(f'<div class="phase"><div class="k">{i+1:02d}</div><div class="t"><h3 class="d4">{t}</h3><p class="body">{p}</p></div><div class="im"><img src="assets/img/{im}" alt=""{CONTAIN if c else ""}></div></div>' for i, (t, p, im, c) in enumerate(PROCESS))
    return f'''<section class="proc" id="process">
  <div class="proc-l">
    <div><h2 class="d3">{title}</h2><div class="proc-bar">{bars}</div></div>
    <div class="proc-steps proc-steps-h">{steps}</div>
  </div>
  <div class="proc-r">{imgs}</div>
</section>
<section class="proc-list wrap sec-s"><h2 class="d2" data-split style="margin-bottom:40px">{title}</h2><div class="phases">{lst}</div></section>'''

TESTI = [
    ("Aleš Zierer", "Vevče Paper Mill", "Ales_Zierer.jpg",
     "This rebuild gave us confidence in ELCON’s knowledge of drives and we decided to rebuild other machines in cooperation with them.",
     "The calender now runs at full speed, whereas before this was not possible due to vibrations."),
    ("Filip Kveder", "MM Količevo", None,
     "The new dispersers have increased production and the new DCS system makes it easier for operators to operate.",
     "Now the system is up-to-date, the supplier ELCON is supporting us and we also make some changes to the system ourselves."),
    ("Dušan Mestnišek", "Cinkarna Celje", "dusan_mestinsek.webp",
     "The new control and monitoring system is modern and ready for further expansion.",
     "The production shutdown was carried out within the planned timeframe, quite quickly for such a volume."),
]

def testimonials(title="What plant managers say after the shutdown."):
    qs = "".join(f'<blockquote>“{a}” <span class="gray">{b}</span></blockquote>' for (_, _, _, a, b) in TESTI)
    def av(n, img):
        if img: return f'<img src="assets/img/{img}" alt="{n}">'
        return f'<span class="ini">{"".join(w[0] for w in n.split())}</span>'
    ps = "".join(f'<button class="person">{av(n,img)}<span><span class="nm">{n}</span><br><span class="role">{c}</span></span><span class="prog"></span></button>' for (n, c, img, _, _) in TESTI)
    return f'''<section class="sec wrap">
  <div class="testi"><div class="testi-q">{qs}</div><div class="testi-people" data-reveal>{ps}</div></div>
</section>'''

CASES = [
    ("Chemical", "market-chemical.html", "Cinkarna Celje, Surface Treatment 2", "Cinkarna_2.webp",
     "A TiO2 finishing plant on Siemens S5 and Factory Link SCADA, 30 years of undocumented changes and no spare parts. Rebuilt on Siemens PCS7 with PROFINET and tested on a SIMIT plant simulation before commissioning.",
     [("2018 to 2021", "Delivery"), ("PCS7, APL, SIMIT", "Technology")]),
    ("Energy", "market-energy.html", "TurkStream reception terminal, Kıyıköy", "TurkStream-1.webp",
     "Integrated Control and Safety System for the gas reception terminal of the TurkStream pipeline: process control, safeguarding, fire and gas, on redundant S7-400H controllers with WinCC Open Architecture.",
     [("2018 to 2020", "Delivery"), ("ICSS, S7-400H", "Technology")]),
    ("Papermills", "market-papermills.html", "MM Količevo, coating kitchen upgrade", "MM-Kolicevo-1.webp",
     "Legacy Step 7 tank logic migrated into PCS7 and SIMATIC Batch, the system upgraded to PCS7 V9.0, and the whole coating kitchen simulated in SIMIT for FAT.",
     [("2013 to 2021", "Delivery"), ("PCS7, SIMATIC Batch", "Technology")]),
    ("Papermills", "market-papermills.html", "Papirnica Vevče, SK5 super calender", "Papirnica-Vevce-4.webp",
     "Obsolete 6RA70 drives with T400 cards replaced by SINAMICS DCM 6RA80, tension control moved into the PLC and a targeted stop added. The calender now runs at full speed.",
     [("2021", "Delivery"), ("SINAMICS DCM", "Technology")]),
    ("Refractory and Cement", "market-cement.html", "RHI Magnesita, Radenthein", "RHI-Magnesita-4.webp",
     "The crushing area of a refractory plant in Carinthia moved from SIMATIC S5 to a modern DCS integrated with MES, feeding production lines through more than 120 silos.",
     [("2021 to 2023", "Delivery"), ("DCS, MES, APF", "Technology")]),
]

def cases_block():
    items = "".join(f'''<article class="case"><a class="ph" href="{h}"><img src="assets/img/{im}" alt="{t}"></a><div class="info"><div><div class="mkt">{m}</div><h3>{t}</h3></div><p>{p}</p><div><div class="facts">{"".join(f"<div><b>{a}</b><span>{b}</span></div>" for a,b in f)}</div><a class="link" href="{h}" style="margin-top:26px">Read the case study {ARR}</a></div></div></article>''' for (m, h, t, im, p, f) in CASES)
    return f'''<section class="sec-s cases"><div class="cases-pin">
  <div class="wrap cases-head"><h2 class="d2" data-split>Plants we have rebuilt.</h2><div class="cases-count"><b>01</b> / {len(CASES):02d}</div></div>
  <div class="cases-track">{items}</div></div>
</section>'''

# ---------------- HOME ----------------
def build_home():
    slides = [("elcon_naslovna.webp", "Automation for chemical, energy, paper and cement plants"),
              ("workers-control-room.webp", "Siemens control systems, from the very beginning"),
              ("eletrical_design_naslovna.webp", "Cabinets tested in our workshop before they ship"),
              ("Papermills-1.webp", "Retrofits with downtime kept to a minimum"),
              ("TurkStream-1.webp", "Redundant control and safety for critical infrastructure")]
    sl = "".join(f'<div class="slide" data-cap="{c}"><img src="assets/img/{im}" alt=""></div>' for im, c in slides)
    dots = "".join("<button aria-label='slide'><i></i></button>" for _ in slides)
    acc = ""
    for i, m in enumerate(MARKETS):
        n = len(REFS[REFKEY[m["slug"]]])
        acc += f'''<a class="acc{' on' if i==0 else ''}" href="market-{m["slug"]}.html"><img src="assets/img/{m["hero"]}" alt="{m["name"]}">
<div class="acc-in"><div class="acc-top"><span class="acc-title">{m["name"]}</span><span class="acc-num">{n} references</span></div>
<div class="acc-body"><p>{HOME_MK[m["slug"]]}</p><span class="btn light">Explore {m["name"].split()[0].lower() if m["slug"]!="cement" else "cement"} {ARR}</span></div></div></a>'''
    svc = [("01", "Complete electrical package", "Electrical plans, cabinets, installation, programming, FAT, commissioning, SAT and As Built documentation. One partner for the whole package.", "service-package.html", "procedure_phase_2.webp"),
           ("02", "Electrical design", "Plans in ePlan or WSCAD for power distribution, motor, instrumentation and network cabinets, for new lines and for reconstructions.", "service-design.html", "eletrical_design_naslovna.webp"),
           ("03", "Software development", "Control software in Siemens PCS7 and TIA Portal, SIMATIC Batch recipes and SIMIT digital twins for testing before start-up.", "service-software.html", "Software-development_naslovna.webp")]
    sv = "".join(f'''<a class="svc-card" href="{h}" data-reveal data-delay="{i*.08}"><div class="txt"><span class="num">{n}</span><h3 class="d4">{t}</h3><p class="body">{p}</p><span class="link go">Learn more {ARR}</span></div><div class="media"><img src="assets/img/{im}" alt="" data-parallax></div></a>''' for i, (n, t, p, h, im) in enumerate(svc))
    body = f'''
<section class="hero">
  <div class="wrap">
    <h1 class="d1" data-split data-now data-delay=".1">Smart, reliable <span data-c>automation</span> for the process industry.</h1>
    <div class="hero-row">
      <p class="lead" data-reveal data-now data-delay=".45">Since 1990 we design the electrical systems and write the control software that keep chemical plants, power stations, paper mills and cement works running.</p>
      <div class="hero-actions" data-reveal data-now data-delay=".55"><a class="btn" href="contact.html#call">Book a free call {ARR}</a><a class="btn ghost" href="#markets">Our markets</a></div>
    </div>
  </div>
  <div class="stage">{sl}<div class="stage-ui"><div class="stage-cap" style="transition:opacity .35s">{slides[0][1]}</div><div class="stage-dots">{dots}</div></div></div>
</section>

<section class="sec wrap">
  <div class="intro">
    <p class="scrub">ELCON started in 1990 as a system integrator. Today we are a certified Siemens Solution Partner for PCS7, SIMATIC and WinCC, with our own electrical designers and programmers. We plan, retrofit and commission large systems, and we stay with the plant long after start-up.</p>
    <div class="intro-foot"><div class="partners" data-reveal><img src="assets/img/siemens-solution-partner-logo.webp" alt="Siemens Solution Partner, Automation Drives"><img src="assets/img/ISO_9001_logo.webp" alt="ISO 9001 certified"></div><a class="link" href="about.html" data-reveal>More about us {ARR}</a></div>
  </div>
</section>

<section id="markets" class="sec-s" style="padding-top:0">
  <div class="wrap mk-head"><h2 class="d2" data-split>Four industries. Decades in each.</h2><p class="lead" data-reveal>We know their production, their expectations and how short a shutdown has to be.</p></div>
  <div class="accordion" data-reveal>{acc}</div>
</section>

<section class="sec">
  <div class="wrap mk-head"><h2 class="d2" data-split>What we deliver.</h2><p class="lead" data-reveal>Smaller projects are carried out by our own engineers. On larger ones we take over project management.</p></div>
  <div class="svc">{sv}</div>
</section>

{process_block()}

<section class="sec wrap">
  <h2 class="d2" data-split style="max-width:16ch;margin-bottom:clamp(56px,6vw,120px)">Small team. Big plants.</h2>
  <div class="stats">
    <div class="stat" data-reveal><div class="n" data-count="1990" data-from="1950" data-fmt="plain">1990</div><div class="l">Founded in Domžale</div></div>
    <div class="stat" data-reveal data-delay=".08"><div class="n" data-count="1388">1,388</div><div class="l">Projects delivered</div></div>
    <div class="stat" data-reveal data-delay=".16"><div class="n" data-count="23">23</div><div class="l">Countries</div></div>
    <div class="stat" data-reveal data-delay=".24"><div class="n" data-count="11">11</div><div class="l">Engineers</div></div>
  </div>
</section>

{cases_block()}

{testimonials()}

<section class="sec-s wrap" style="padding-top:0">
  <div class="letter">
    <div class="por" data-reveal><img src="assets/img/bor_kosmac.webp" alt="Bor Kosmač, CEO"></div>
    <div class="txt">
      <h2 class="d3" data-split>Dear visitors and partners,</h2>
      <p class="lead" data-reveal>Welcome to ELCON, your trusted automation company specializing in the process industry. From retrofitting old machines to becoming a Siemens Solution Partner in 2009, we have continuously evolved to serve the chemical industry, energy, oil and gas, cement and refractories.</p>
      <p class="body" data-reveal>We are proud of our ISO 9001:2015 certification, obtained in 2022, which validates our commitment to quality and customer satisfaction. Moving forward, ELCON aims to expand its project portfolio internationally, offering expertise in planning and retrofitting large systems or implementing new production lines.</p>
      <p class="body" data-reveal>Count on ELCON as your dedicated partner, providing customized solutions and support throughout the project lifecycle. Thank you for your continued trust.</p>
      <div class="sig" data-reveal><b>Bor Kosmač</b><span class="small">CEO, ELCON d.o.o.</span></div>
    </div>
  </div>
</section>

{cta()}
'''
    page("index.html", "ELCON | Automation for the process industry", body, home=True)

HOME_MK = {
    "chemical": "Higher motor powers and a large number of sensors and actuators, handled both in electrical projects and in software. Batch processes with SIMATIC Batch.",
    "energy": "Oil and gas projects need a high level of operational reliability. Documentation, implementation and testing done to the same standard, on redundant architecture.",
    "papermills": "We know paper and board machines. Downtimes must be as short as possible, so we upgrade drives and control systems with minimal interruption.",
    "cement": "Large volumes of material, robust machines and high motor ratings. Conveyor routing with Siemens CEMAT, guarded to protect operators and machines.",
}

# ---------------- MARKET PAGES ----------------
def build_market(m):
    d = parse_market(m["file"])
    intro = d["intro"]
    lead = clean(intro[0]).split(". ")[0] + "."
    paras = "".join(f'<p class="body">{esc(p)}</p>' for p in intro)
    li = lambda arr: "".join(f'<li><b>{i+1:02d}</b><span>{esc(x)}</span></li>' for i, x in enumerate(arr))
    pain = "".join(f"<li>{X}<span>{esc(x)}</span></li>" for x in d["pain"])
    sol = "".join(f"<li>{CHECK}<span>{esc(x)}</span></li>" for x in d["sol"])
    stories = ""
    for ci, c in enumerate(d["cases"]):
        imgs = m["case_imgs"][ci] if ci < len(m["case_imgs"]) else m["case_imgs"][0]
        title = clean(c["title"]).replace(" , ", ", ")
        client = title.split(",")[0].split(" ")[0:3]
        cls = ["a", "b", "c", "c"]
        gal = "".join(f'<figure class="{cls[i]}" data-reveal><img src="assets/img/{im}" alt="" data-parallax style="height:114%;margin-top:-7%"></figure>' for i, im in enumerate(imgs))
        txt = "".join(f'<p class="{"lead" if i==0 else "body"}" data-reveal>{esc(p)}</p>' for i, p in enumerate(c["paras"]))
        stories += f'''<section class="sec-s">
  <div class="wrap story" style="margin-bottom:clamp(40px,4vw,72px)"><h2 class="d2 h" data-split>{esc(title)}</h2><div class="meta" data-reveal><span class="small">Case study, {m["name"]}</span></div></div>
  <div class="gal" style="margin-bottom:clamp(48px,5vw,96px)">{gal}</div>
  <div class="wrap story"><div class="txt">{txt}</div></div>
</section>'''
    rows = REFS[REFKEY[m["slug"]]]
    trs = "".join(f"<tr><td>{esc(r[0].title() if r[0].isupper() else r[0])}</td><td>{years(r[1])}</td><td>{esc(r[2])}</td><td>{esc(r[3].replace(' · ', ', ').replace('and,', 'and'))}</td></tr>" for r in rows if len(r) >= 4)
    others = "".join(f'<a href="market-{o["slug"]}.html"><img src="assets/img/{o["hero"]}" alt=""><div class="in"><div><h3 class="d4">{o["name"]}</h3></div><span class="btn light">{ARR}</span></div></a>' for o in MARKETS if o is not m)
    body = f'''
<section class="phero">
  <div class="wrap">
    <div class="crumbs" data-reveal data-now><a href="index.html">Home</a><span>/</span><a href="markets.html">Markets</a><span>/</span><span>{m["name"]}</span></div>
    <div class="phero-row"><h1 class="d1" data-split data-now>{m["title"]}</h1><p class="lead" data-reveal data-now data-delay=".4">{esc(lead)}</p></div>
  </div>
  <div class="pimg"><img src="assets/img/{m["hero"]}" alt="{m["title"]}"></div>
</section>
<section class="sec wrap"><div class="cols"><h2 class="d3 h" data-split>What ELCON does.</h2><div class="c" data-reveal>{paras}</div></div></section>
<section class="sec-s wrap" style="padding-top:0"><div class="cols">
  <div class="h" style="grid-column:1/span 6"><h3 class="d4" style="margin-bottom:28px" data-reveal>Electrical design</h3><ul class="list" data-reveal>{li(d["design"])}</ul></div>
  <div class="c" style="grid-column:7/span 6"><h3 class="d4" style="margin-bottom:28px" data-reveal>Programming</h3><ul class="list" data-reveal>{li(d["prog"])}</ul></div>
</div></section>
<section class="sec-s"><div class="vs">
  <div class="pain" data-reveal><h2 class="d3">The pain points.</h2><ul>{pain}</ul></div>
  <div class="sol" data-reveal data-delay=".1"><h2 class="d3">Our solution.</h2><ul>{sol}</ul></div>
</div></section>
{stories}
<section class="sec wrap">
  <div class="refs-top"><h2 class="d2" data-split>References.</h2><input class="refs-search" type="search" placeholder="Search client, year or project" aria-label="Search references"></div>
  <table class="refs" data-reveal><thead><tr><th>Customer</th><th>Year</th><th>Project</th><th>Goods and services</th></tr></thead><tbody>{trs}</tbody></table>
</section>
{cta("Book a free call.", esc(d["cta"]))}
<section class="sec-s"><div class="wrap" style="margin-bottom:40px"><h2 class="d3" data-reveal>Other markets.</h2></div><div class="ov three">{others}</div></section>
'''
    page(f"market-{m['slug']}.html", f"{m['title']} | ELCON", body, active="markets")

def build_markets_index():
    cards = "".join(f'<a href="market-{m["slug"]}.html" data-reveal><img src="assets/img/{m["hero"]}" alt=""><div class="in"><div><h3 class="d3">{m["name"]}</h3><p>{HOME_MK[m["slug"]]}</p></div><span class="btn light">{ARR}</span></div></a>' for m in MARKETS)
    body = f'''<section class="phero"><div class="wrap">
<div class="crumbs" data-reveal data-now><a href="index.html">Home</a><span>/</span><span>Markets</span></div>
<div class="phero-row"><h1 class="d1" data-split data-now>Markets.</h1><p class="lead" data-reveal data-now data-delay=".4">Chemical, Oil and Gas, Pulp and Paper, Cement and Refractories. We have worked in each for decades.</p></div></div></section>
<section class="sec-s" style="padding-top:0"><div class="ov">{cards}</div></section>
{cta()}'''
    page("markets.html", "Markets | ELCON", body, active="markets")

# ---------------- SERVICES ----------------
def svc_hero(title, lead, img, crumb, cur):
    tabs = "".join(f'<a href="{h}"{ON if h==cur else ""}>{t}</a>' for h, t in [("service-package.html", "Complete electrical package"), ("service-design.html", "Electrical design"), ("service-software.html", "Software development")])
    return f'''<section class="phero"><div class="wrap">
<div class="crumbs" data-reveal data-now><a href="index.html">Home</a><span>/</span><a href="services.html">Services</a><span>/</span><span>{crumb}</span></div>
<div class="subnav" data-reveal data-now>{tabs}</div>
<div class="phero-row"><h1 class="d1" data-split data-now>{title}</h1><p class="lead" data-reveal data-now data-delay=".4">{lead}</p></div></div>
<div class="pimg"><img src="assets/img/{img}" alt=""></div></section>'''

def build_package():
    inc = ["Drawing up electrical plans", "Manufacture of electrical cabinets", "Electrical installation", "Program development", "Testing (FAT)", "Commissioning and SAT", "Documentation (As Built)"]
    phases = [
        ("1a", "Electrical design and supply of materials", ["Our engineers prepare electrical designs based on information from mechanical designers. If necessary, these are sent to the customer for preview and approval.", "On the basis of these projects, our purchasing department orders the necessary materials. Often, due to short deadlines, materials are ordered before the electrical plans are finalised."], "procedure_phase_1a.webp", True),
        ("1b", "Developing the program", ["A functional specification is drawn up before the program is developed, prepared in cooperation with the client. This is the basis for starting the programming.", "The programmer also works from the electrical project and the P&I diagrams. If necessary, a digital twin is prepared to test the program in the FAT test."], "procedure_phase_1b.webp", True),
        ("2", "Cabinet manufacture and testing", ["The material is sent to one of our partners who assembles the electrical cabinets. At their premises, our engineers configure the equipment in the cabinets, for example network settings and drive settings. The cabinets are then tested."], "procedure_phase_2.webp", False),
        ("3", "Installation on site, electrical installation and testing", ["The cabinets are transported to the facility. There, our partner carries out the electrical installations based on our plans: cable racks, penetrations, laying and connecting the cables.", "The programmers then configure the equipment and carry out the SATs together with the electrical installers, verifying the electrical connection and the proper functioning of the program. During commissioning, the parameters that could not be set during programming are set, especially controller parameters."], "procedure_phase_3.webp", False),
    ]
    ph = "".join(f'<div class="phase" data-reveal><div class="k">Phase {k}</div><div class="t"><h3 class="d4">{t}</h3>{"".join(f"<p class=body>{p}</p>" for p in ps)}</div><div class="im"><img src="assets/img/{im}" alt=""{" class=contain" if c else ""}></div></div>' for k, t, ps, im, c in phases)
    chips = "".join(f"<span>{x}</span>" for x in inc)
    body = svc_hero("Complete electrical package.", "One partner from the first electrical plan to the As Built documentation.", "eletrical_design_naslovna.webp", "Complete electrical package", "service-package.html") + f'''
<section class="sec wrap"><div class="cols"><h2 class="d3 h" data-split>Everything the plant needs, in one package.</h2><div class="c"><div class="chips" data-reveal>{chips}</div></div></div></section>
<section class="sec-s wrap" style="padding-top:0"><h2 class="d2" data-split style="margin-bottom:clamp(40px,4vw,80px)">The procedure.</h2><div class="phases">{ph}</div></section>
{cta()}'''
    page("service-package.html", "Complete electrical package | ELCON", body, active="services")

def build_design():
    areas = ["Power distribution cabinets", "Motor cabinets", "Instrumentation control cabinets", "Junction boxes", "Pneumatic cabinets", "Telecommunications cabinets", "Computer cabinets", "Security and access control equipment", "Control room equipment", "CCTV", "PAGA"]
    cabs = [("Power distribution cabinets", "Main switch, taps and energy analysers, connected via wired or bus connections such as Rittal RiLine or EATON SASY. Usually designed with Siemens Sentron and linked to the PLC over PROFINET or MODBUS TCP/IP.", "Power-distribution-cabinet.jpg"),
            ("Motor cabinets", "Motor protections, contactors, SIMOCODE smart relays, soft starters and frequency converters, dimensioned for motor power, intermittency and cable length.", "Motor-cabinet-2.webp"),
            ("Instrument control cabinets", "Where more safety is required: safety PLC IO modules, the right number of contactors, and SIL2 safety functions built into Siemens inverters over PROFISAFE.", "Instrument-control-cabinet.webp"),
            ("Network cabinets", "Switches, patch panels and servers installed to the required IP protection level, with climate control if needed, every component labeled with electrical and computer names.", "Network-cabinet.webp")]
    cc = "".join(f'<div class="cab-card" data-reveal data-delay="{i*.06}"><div class="im"><img src="assets/img/{im}" alt="{t}"></div><div class="tx"><h3>{t}</h3><p class="body" style="font-size:16px">{p}</p></div></div>' for i, (t, p, im) in enumerate(cabs))
    chips = "".join(f"<span>{x}</span>" for x in areas)
    body = svc_hero("Electrical design.", "Electrical plans in ePlan or WSCAD, delivered on paper and in electronic format.", "procedure_phase_2.webp", "Electrical design", "service-design.html") + f'''
<section class="sec wrap"><div class="cols"><h2 class="d3 h" data-split>New builds and reconstructions.</h2><div class="c" data-reveal>
<p class="lead">ELCON draws up electrical plans for its clients, typically based on machine drawings.</p>
<p class="body" style="margin-top:20px">We also produce plans for conversions and reconstructions. Here we often start from old plans that are not yet in electronic format. These are either redrawn or simply supplemented with additional pages.</p></div></div></section>
<section class="sec-s" style="padding-top:0"><div class="wrap" style="margin-bottom:clamp(40px,4vw,72px)"><h2 class="d2" data-split>Cabinets we design.</h2></div><div class="cab">{cc}</div></section>
<section class="sec-s wrap"><div class="cols"><div class="h"><h2 class="d3" data-split>Every area of the plant.</h2><p class="body" data-reveal style="margin-top:24px">Most often with equipment from SIEMENS and EATON for motor protection and contactors, SIEMENS, ABB and DANFOSS for frequency converters, and SIEMENS and SOLCON for soft starters.</p></div><div class="c"><div class="chips" data-reveal>{chips}</div></div></div></section>
{cta()}'''
    page("service-design.html", "Electrical design | ELCON", body, active="services")

def build_software():
    feats = [
        ("PCS7 applications", ["PCS7 is a Siemens DCS. Unlike conventional PLC and SCADA, the two are tightly integrated, with block libraries for sensors and actuators and automatic generation of alarms, tags, archive tags and block icons.",
                                "We build PCS7 systems from a single AS with a combined OS and ES station up to client-server structures with redundancy at AS and OS level, with F-Systems for safety. Computers usually run virtualised on VMware ESXi. Libraries: standard APL, Pulp and Paper APL and CEMAT."], "pcs7_applications.webp"),
        ("SIMATIC Batch", ["In chemistry and food, processes are often batchwise. Recipes change parameters like step times and dosing quantities. When the order of steps must change too, we use SIMATIC Batch.",
                           "Recipes can have any number of steps with sequential, parallel or alternative branches. The programmer prepares the phases at AS level, the operator only builds the recipe."], "pcs7_applications_batch.webp"),
        ("Digital twin", ["Process applications are hard to test on site, and the customer wants production back as soon as possible. So we test on digital twins built in Siemens SIMIT, first internally in FAT and then with the customer."], "digital_twin.webp"),
        ("TIA Portal applications", ["The TIA Portal is primarily for machines: a Siemens S7-1200 or S7-1500 PLC with a touch panel or SCADA. Speed matters, so servo positioning and high-speed counters are common, with safety integrated in the controller.",
                                    "Smaller third-party devices are linked to PCS7 over S7 links, or through PN/PN couplers when the controllers are not Siemens."], "tia_portal_applications.webp"),
    ]
    fb = ""
    for i, (t, ps, im) in enumerate(feats):
        fb += f'''<section class="sec-s wrap"><div class="feature{' flip' if i%2 else ''}"><div class="m" data-reveal><img src="assets/img/{im}" alt="{t}" class="contain"></div><div class="t"><h2 class="d3" data-split>{t}</h2>{"".join(f'<p class="body" data-reveal>{p}</p>' for p in ps)}</div></div></section>'''
    body = svc_hero("Software development.", "Control software in the Siemens PCS7 and Siemens TIA Portal environments.", "Software-development_naslovna.webp", "Software development", "service-software.html") + f'''
<section class="sec wrap"><div class="cols"><h2 class="d3 h" data-split>Original Siemens blocks, wherever possible.</h2><div class="c" data-reveal><p class="lead">We stay as close as possible to the rules of the PCS7 system: original Siemens blocks, channel drivers linked automatically to module drivers, tags and block icons generated automatically.</p><p class="body" style="margin-top:20px">Where the user’s requirements cannot be met with Siemens functionality, we program our own blocks in Siemens SCL.</p></div></div></section>
{fb}
{cta()}'''
    page("service-software.html", "Software development | ELCON", body, active="services")

def build_services_index():
    cards = [("service-package.html", "Complete electrical package", "Plans, cabinets, installation, programming, FAT, SAT and As Built documentation.", "procedure_phase_2.webp"),
             ("service-design.html", "Electrical design", "Plans in ePlan or WSCAD for every cabinet in the plant.", "eletrical_design_naslovna.webp"),
             ("service-software.html", "Software development", "Siemens PCS7, SIMATIC Batch, TIA Portal and SIMIT digital twins.", "Software-development_naslovna.webp")]
    c = "".join(f'<a href="{h}" data-reveal><img src="assets/img/{im}" alt=""><div class="in"><div><h3 class="d4">{t}</h3><p>{p}</p></div><span class="btn light">{ARR}</span></div></a>' for h, t, p, im in cards)
    body = f'''<section class="phero"><div class="wrap">
<div class="crumbs" data-reveal data-now><a href="index.html">Home</a><span>/</span><span>Services</span></div>
<div class="phero-row"><h1 class="d1" data-split data-now>Services.</h1><p class="lead" data-reveal data-now data-delay=".4">From design and engineering to programming of control and supervision systems. We also supply the complete electrical package.</p></div></div></section>
<section class="sec-s" style="padding-top:0"><div class="ov three">{c}</div></section>
{process_block()}
{cta()}'''
    page("services.html", "Services | ELCON", body, active="services")

# ---------------- ABOUT ----------------
TEAM = [("Bor Kosmač", "CEO", "+386 1 724 00 56", "+386 41 313 413", "bor_kosmac.webp"),
        ("Andrej Simon", "Designer", "+386 1 724 00 41", "+386 41 313 415", None),
        ("Marjan Bojanc", "Designer", "+386 1 724 00 40", "+386 41 313 416", None),
        ("Luka Breška", "Designer", "+386 1 724 00 52", "+386 41 313 437", None),
        ("Borut Medved", "Designer", "+386 1 724 00 54", "+386 41 313 419", None),
        ("Andrej Zajc", "Programmer", "+386 1 724 00 40", "+386 41 313 417", None),
        ("Andi Smole", "Programmer", "+386 1 724 00 32", "+386 41 313 411", None),
        ("Lovro Volčini", "Programmer", "+386 1 724 00 31", "+386 41 313 420", None),
        ("Alen Čauševič", "Programmer", "+386 1 724 00 49", "+386 41 313 412", None),
        ("Borut Jeras", "Programmer", "+386 1 724 00 36", "+386 41 313 972", None),
        ("Blaž Mavec", "Programmer", "+386 1 724 00 37", None, None),
        ("Staša Horvat", "Secretariat", "+386 1 724 00 40", "+386 31 270 151", None)]

def team_block():
    def tel(n): return f'<a href="tel:{n.replace(" ","")}">{n}</a>' if n else ""
    t = "".join(f'<div class="tm" data-reveal data-delay="{(i%4)*.05}">{avatar(n, im)}<div><div class="nm">{n}</div><div class="r">{r}</div></div><div class="ph">{tel(a)}{tel(b)}</div></div>' for i, (n, r, a, b, im) in enumerate(TEAM))
    return f'<section class="sec-s" id="team"><div class="wrap mk-head"><h2 class="d2" data-split>The people.</h2><p class="lead" data-reveal>Electrical designers and programmers. Call the person who works on your plant directly.</p></div><div class="team">{t}</div></section>'

def build_about():
    info = [("Company name", "ELCON podjetje za avtomatizacijo, razvoj in inženiring d.o.o."), ("Short company name", "ELCON d.o.o."), ("Company headquarters", "Ljubljanska cesta 80, 1230 Domžale, Slovenia"),
            ("Year of establishment", "1990"), ("Number of employees", "12"), ("Company registration number", "5405556"), ("Identification number", "SI28367014"), ("Taxpayer", "Yes"),
            ("Business account", "SI56 0400 0027 6589 621"), ("SWIFT code", "KBMASI2X")]
    it = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in info)
    body = f'''<section class="phero"><div class="wrap">
<div class="crumbs" data-reveal data-now><a href="index.html">Home</a><span>/</span><span>About us</span></div>
<div class="phero-row"><h1 class="d1" data-split data-now>30 years on Siemens.</h1><p class="lead" data-reveal data-now data-delay=".4">ELCON was established in 1990 as a system integrator. From the very beginning we have used control equipment from the world leader in industrial control systems, SIEMENS.</p></div></div>
<div class="pimg"><img src="assets/img/workers-control-room.webp" alt=""></div></section>
<section class="sec wrap"><div class="intro"><p class="scrub">We are a certified Siemens Solution Partner for PCS7, SIMATIC and WinCC, active in chemical, oil and gas, pulp and paper, cement and refractories. Our work runs from design and engineering to programming of control and supervision systems, and we also supply the complete electrical package.</p>
<div class="intro-foot"><div class="partners" data-reveal><img src="assets/img/siemens-solution-partner-logo.webp" alt="Siemens Solution Partner"><img src="assets/img/ISO_9001_logo.webp" alt="ISO 9001"></div><a class="btn" href="contact.html#call" data-reveal>Contact us {ARR}</a></div></div></section>
<section class="sec-s wrap" style="padding-top:0"><div class="stats">
<div class="stat" data-reveal><div class="n" data-count="1990" data-from="1950" data-fmt="plain">1990</div><div class="l">Year of establishment</div></div>
<div class="stat" data-reveal><div class="n" data-count="1388">1,388</div><div class="l">Projects</div></div>
<div class="stat" data-reveal><div class="n" data-count="23">23</div><div class="l">Countries</div></div>
<div class="stat" data-reveal><div class="n" data-count="11">11</div><div class="l">Engineers</div></div></div></section>
{process_block("Our project procedure.")}
{team_block()}
{testimonials()}
<section class="sec-s wrap"><div class="cols"><h2 class="d3 h" data-split>Company information.</h2><div class="c"><table class="info-table" data-reveal>{it}</table></div></div></section>
{cta()}'''
    page("about.html", "About us | ELCON", body, active="about")

def build_contact():
    opts = "".join(f'<label><input type="radio" name="Market" value="{m["name"]}"><span>{m["name"]}</span></label>' for m in MARKETS) + '<label><input type="radio" name="Market" value="Other"><span>Other</span></label>'
    body = f'''<section class="phero"><div class="wrap">
<div class="crumbs" data-reveal data-now><a href="index.html">Home</a><span>/</span><span>Contact</span></div>
<div class="phero-row"><h1 class="d1" data-split data-now>Let’s talk about your plant.</h1><p class="lead" data-reveal data-now data-delay=".4">Book a free call with our engineers. Tell us what you are running and where it hurts.</p></div></div></section>
<section class="sec-s wrap" id="call" style="padding-top:0"><div class="contact-grid">
  <div class="l" data-reveal>
    <div><p class="small" style="margin-bottom:8px">Phone</p><a class="big-link" href="tel:+38617240040">+386 1 724 00 40</a></div>
    <div><p class="small" style="margin-bottom:8px">Email</p><a class="big-link" href="mailto:info@elcon.si">info@elcon.si</a></div>
    <div><p class="small" style="margin-bottom:8px">Office</p><p class="lead" style="color:var(--ink)">Ljubljanska cesta 80<br>1230 Domžale, Slovenia</p><a class="link" style="margin-top:14px" href="https://maps.google.com/?q=Ljubljanska+cesta+80,+1230+Domžale" target="_blank" rel="noopener">How to reach us {ARR}</a></div>
  </div>
  <div class="r" data-reveal data-delay=".1">
    <form class="f">
      <label class="full">Your market<div class="opts">{opts}</div></label>
      <label>Name<input name="Name" required autocomplete="name"></label>
      <label>Company<input name="Company" required autocomplete="organization"></label>
      <label>Email<input name="Email" type="email" required autocomplete="email"></label>
      <label>Phone<input name="Phone" type="tel" autocomplete="tel"></label>
      <label class="full">What are you running, and what should change?<textarea name="Message"></textarea></label>
      <div class="full"><button class="btn" type="submit">Book a free call {ARR}</button></div>
    </form>
    <p class="f-done">Thank you. Your email app has opened with the request, just press send.</p>
  </div>
</div></section>
<div class="map" data-reveal><iframe title="ELCON location" loading="lazy" src="https://www.openstreetmap.org/export/embed.html?bbox=14.582%2C46.128%2C14.622%2C46.148&amp;layer=mapnik&amp;marker=46.1378%2C14.6018"></iframe></div>
{team_block()}'''
    page("contact.html", "Contact | ELCON", body, active="contact")

if __name__ == "__main__":
    build_home(); build_markets_index(); build_services_index()
    for m in MARKETS: build_market(m)
    build_package(); build_design(); build_software(); build_about(); build_contact()
    print("built", sorted(p.name for p in OUT.glob("*.html")))
