# app.py - routes Flask. Lancer ce fichier depuis Pydroid 3.
from flask import Flask, render_template, request
from fiscal import fcfa, simuler

app = Flask(__name__)
app.template_filter("f")(fcfa)


@app.route("/", methods=["GET", "POST"])
def index():
    g = request.form
    f = {"associes": g.get("associes", "1"), "activite": g.get("activite", "services"),
         "ca": g.get("ca", ""), "charges": g.get("charges", ""),
         "protection": "protection" in g, "investisseurs": "investisseurs" in g,
         "salaire_gerant": g.get("salaire_gerant", ""), "cadre": "cadre" in g,
         "parts": g.get("parts", "1") or "1", "nb_salaries": g.get("nb_salaries", ""),
         "salaire_staff": g.get("salaire_staff", "")}
    try:
        r = simuler(f) if request.method == "POST" else None
    except ValueError:
        f["parts"], r = "1", None
    return render_template("index.html", f=f, r=r)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
