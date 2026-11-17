# fiscal.py - logique métier (aucune dépendance à Flask)
from params import P


def fcfa(n):
    return f"{round(n):,}".replace(",", " ") + " FCFA"


def entier(v, defaut=0):
    try:
        return max(0, int(float(str(v).replace(" ", "").replace(",", "."))))
    except (ValueError, TypeError):
        return defaut


STATUTS = {
    "EI": ("Entreprise Individuelle (EI)", "Création rapide au BCE (APIX) sans capital minimum. Attention : patrimoine personnel non séparé."),
    "SUARL": ("SARL Unipersonnelle (SUARL)", "Idéal pour entreprendre seul tout en protégeant vos biens personnels. Capital libre."),
    "SARL": ("SARL (Société à Responsabilité Limitée)", "Structure recommandée à plusieurs associés au Sénégal. Protège le patrimoine personnel."),
    "SAS": ("SAS (Société par Actions Simplifiée)", "Souple et adaptée à l'entrée d'investisseurs ou à un fort CA. Statuts très librement organisés."),
}


def recommander_statut(associes, ca, protection, investisseurs):
    if associes == 1:
        return "SUARL" if (protection or ca >= P["SEUIL_CGU_TVA"]) else "EI"
    return "SAS" if (investisseurs or ca >= P["SAS_CA"]) else "SARL"


def impot_cgu(ca, activite):
    taux, mini = P["CGU"][activite]
    return max(mini, ca * taux)


def impot_reel(ca, charges_deductibles):
    benefice = ca - charges_deductibles
    is_ = max(0, benefice) * P["IS_TAUX"]
    imf = min(max(ca * P["IMF_TAUX"], P["IMF_MIN"]), P["IMF_MAX"])
    return {"benefice": benefice, "is": is_, "imf": imf,
            "impot": max(is_, imf), "base": "IS" if is_ >= imf else "IMF"}


def ir_annuel(base, parts):
    par_part, reste, prec, total = base / parts, base / parts, 0, 0.0
    for plafond, taux in P["IR_BAREME"]:
        tranche = reste if plafond is None else min(reste, plafond - prec)
        total += max(0, tranche) * taux
        if plafond is None or par_part <= plafond:
            break
        reste -= tranche
        prec = plafond
    return total * parts


def trimf(brut_annuel):
    for plafond, montant in P["TRIMF"]:
        if plafond is None or brut_annuel < plafond:
            return montant


def simuler_salaire(brut_m, cadre, parts):
    """Coût et net annuels pour UN salarié (12 mois)."""
    if brut_m <= 0:
        return None
    rg = min(brut_m, P["IPRES_RG_PLAFOND"])
    rc = max(0, min(brut_m, P["IPRES_RC_PLAFOND"]) - P["IPRES_RG_PLAFOND"]) if cadre else 0
    css = min(brut_m, P["CSS_PLAFOND"])
    sal_m = rg * P["IPRES_RG_SAL"] + rc * P["IPRES_RC_SAL"]
    emp_m = (rg * P["IPRES_RG_EMP"] + rc * P["IPRES_RC_EMP"]
             + css * (P["CSS_PF_EMP"] + P["CSS_AT_EMP"]) + brut_m * P["CFCE_EMP"])
    brut_a, cotis_sal = brut_m * 12, sal_m * 12
    base = brut_a - cotis_sal
    base -= min(base * P["IR_FRAIS_PRO"], P["IR_FRAIS_PRO_MAX"])
    ir, tr = ir_annuel(max(0, base), parts), trimf(brut_a)
    return {"brut": brut_a, "cotis_sal": cotis_sal, "ir": ir, "trimf": tr,
            "net": brut_a - cotis_sal - ir - tr, "charges_emp": emp_m * 12,
            "cout": brut_a + emp_m * 12}


def multiplier(s, n):
    return {k: v * n for k, v in s.items()} if s and n > 1 else s


def simuler(f):
    associes = 2 if f["associes"] == "2" else 1
    activite = f["activite"] if f["activite"] in P["CGU"] else "services"
    ca, charges = entier(f["ca"]), entier(f["charges"])
    protection, invest = f["protection"], f["investisseurs"]
    parts = max(1.0, min(5.0, float(f["parts"] or 1)))
    nb = entier(f["nb_salaries"])

    gerant = simuler_salaire(entier(f["salaire_gerant"]), f["cadre"], parts)
    staff = multiplier(simuler_salaire(entier(f["salaire_staff"]), False, 1), nb)
    cout_staff = staff["cout"] if staff else 0
    cout_gerant = gerant["cout"] if gerant else 0

    statut = recommander_statut(associes, ca, protection, invest)
    regime = "CGU" if statut == "EI" and ca <= P["SEUIL_CGU_TVA"] else "Réel"

    # Scénario A : EI + CGU (le gérant n'est pas salarié)
    a = {"titre": "EI au CGU", "ok": ca <= P["SEUIL_CGU_TVA"]}
    if a["ok"]:
        a["impot"] = impot_cgu(ca, activite)
        a["label_impot"] = "CGU " + ("Commerce" if activite == "commerce" else "Services")
        a["sociaux"] = (staff["charges_emp"] if staff else 0)
        a["perso"] = (staff["ir"] + staff["trimf"]) if staff else 0
        a["dispo"] = ca - charges - cout_staff - a["impot"]
    # Scénario B : SUARL / SARL au réel (le gérant se verse un salaire)
    r = impot_reel(ca, charges + cout_gerant + cout_staff)
    b = {"titre": "SUARL au réel", "ok": True, "impot": r["impot"],
         "label_impot": f"{r['base']} (IS {fcfa(r['is'])} / IMF {fcfa(r['imf'])})",
         "label_court": r['base'],
         "sociaux": (gerant["charges_emp"] if gerant else 0) + (staff["charges_emp"] if staff else 0),
         "perso": sum((s["ir"] + s["trimf"]) for s in (gerant, staff) if s)}
    b["dispo"] = (gerant["net"] if gerant else 0) + r["benefice"] - r["impot"]

    principal = a if regime == "CGU" else b
    return {"statut": statut, "statut_nom": STATUTS[statut][0], "desc": STATUTS[statut][1],
            "principal": principal, "benefice": max(0, ca - charges), "regime": regime, "tva": ca > P["SEUIL_CGU_TVA"],
            "ca": ca, "charges": charges, "a": a, "b": b,
            "gerant": gerant, "staff": staff, "nb": nb,
            "meilleur": ("A" if a["ok"] and a["dispo"] >= b["dispo"] else "B")}
