# app.py - routes Flask + PWA (manifest, service worker, icônes). Lancer ce fichier dans Pydroid 3.
import struct
import zlib
from functools import lru_cache
from flask import Flask, Response, render_template, request
from fiscal import fcfa, simuler
from params import CHECKLISTS, GLOSSAIRE, LIENS

app = Flask(__name__, template_folder=".")
app.template_filter("f")(fcfa)

SW_VERSION = "v2"


@app.route("/", methods=["GET", "POST"])
def index():
    g = request.form
    f = {"associes": g.get("associes", "1"), "activite": g.get("activite", "services"),
         "ca": g.get("ca", ""), "charges": g.get("charges", ""),
         "protection": "protection" in g, "investisseurs": "investisseurs" in g,
         "nouvelle": "nouvelle" in g,
         "salaire_gerant": g.get("salaire_gerant", ""), "cadre": "cadre" in g,
         "parts": g.get("parts", "1") or "1", "nb_salaries": g.get("nb_salaries", ""),
         "salaire_staff": g.get("salaire_staff", "")}
    try:
        r = simuler(f) if request.method == "POST" else None
    except ValueError:
        f["parts"], r = "1", None
    return render_template("index.html", f=f, r=r, g=GLOSSAIRE, checklists=CHECKLISTS, liens=LIENS)


@app.route("/manifest.json")
def manifest():
    return Response("""{
  "name": "SenEntreprise - Simulateur Sénégal",
  "short_name": "SenEntreprise",
  "description": "Statut juridique OHADA et impôts au Sénégal",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "background_color": "#f1f5f9",
  "theme_color": "#047857",
  "lang": "fr",
  "icons": [
    {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
    {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
    {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]
}""", mimetype="application/manifest+json")


SW_JS = """
const CACHE = 'senentreprise-%s';
const SHELL = ['/', '/manifest.json', '/icon-192.png', 'https://cdn.tailwindcss.com'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(SHELL.map(u =>
    fetch(u, u.startsWith('http') ? {mode: 'no-cors'} : {}).then(r => c.put(u, r)).catch(() => {})))));
  self.skipWaiting();
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(r => {
      const copy = r.clone(); caches.open(CACHE).then(c => c.put('/', copy)); return r;
    }).catch(() => caches.match('/')));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => {
    const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); return r;
  }).catch(() => hit)));
});
""" % SW_VERSION


@app.route("/sw.js")
def service_worker():
    resp = Response(SW_JS, mimetype="application/javascript")
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@lru_cache(maxsize=4)
def icone_png(taille):
    """Icône PNG générée sans dépendance : fond vert, anneau blanc."""
    cx = cy = taille / 2
    r_ext, r_int = taille * 0.32, taille * 0.20
    fond, blanc = bytes((4, 120, 87)), bytes((255, 255, 255))
    lignes = bytearray()
    for y in range(taille):
        lignes.append(0)
        for x in range(taille):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            lignes += blanc if r_int ** 2 <= d2 <= r_ext ** 2 else fond

    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", taille, taille, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(lignes), 9)) + chunk(b"IEND", b""))


@app.route("/icon-<int:taille>.png")
def icone(taille):
    taille = 512 if taille >= 512 else 192
    return Response(icone_png(taille), mimetype="image/png",
                    headers={"Cache-Control": "public, max-age=604800"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
