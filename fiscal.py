# fiscal.py - logique métier (aucune dépendance à Flask)
import re
from params import P, FRAIS


def fcfa(n):
    return f"{round(n):,}".replace(",", " ") + " FCFA"


def entier(v, defaut=0):
    chiffres = re.sub(r"\D", "", str(v or ""))
    return int(chiffres) if chiffres else defaut


STATUTS = {
    "EI": ("Entreprise Individuelle (EI)", "Création rapide au BCE (APIX) sans capital minimum. Attention : patrimoine personnel non séparé."),
    "SUARL": ("SARL Unipersonnelle (SUARL)", "Idéal pour entreprendre seul tout en protégeant vos biens personnels. Capital libre."),
    "SARL": ("SARL (Société à Responsabilité Limitée)", "Structure recommandée à plusieurs associés au Sénégal. Protège le patrimoine personnel."),
    "SASU": ("SASU (Société par Actions Simplifiée Unipersonnelle)", "Permet de démarrer seul tout en facilitant l'entrée future d'investisseurs et le passage en SAS. Statuts très librement organisés, responsabilité limitée aux apports."),
    "SAS": ("SAS (Société par Actions Simplifiée)", "Souple pour accueillir des investisseurs : statuts très librement organisés, entrée facilitée de nouveaux associés. Adaptée aussi à un fort chiffre d'affaires."),
}


def recommander_statut(associes, ca, protection, investisseurs):
    if associes == 1:
        if investisseurs:
            return "SASU"
        return "SUARL" if (protection or ca >= P["SEUIL_CGU_TVA"]) else "EI"
    return "SAS" if (investisseurs or ca >= P["SAS_CA"]) else "SARL"


def impot_cgu(ca, activite):
    taux, mini = P["CGU"][activite]
    impot = max(mini, ca * taux)
    nom = "Commerce" if activite == "commerce" else "Services"
    detail = f"(minimum de perception : {fcfa(mini)})" if impot == mini else f"({taux * 100:g} % du chiffre d'affaires)"
    return {"impot": impot, "label": f"CGU {nom}", "detail": detail}


def impot_reel(ca, charges, exo_imf=False):
    benefice = ca - charges
    is_ = max(0, benefice) * P["IS_TAUX"]
    imf_theo = min(max(ca * P["IMF_TAUX"], P["IMF_MIN"]), P["IMF_MAX"])
    imf = 0 if exo_imf else imf_theo
    if imf > is_:
        label, detail = "Impôt dû (IMF minimum)", f"(IS calculé : {fcfa(is_)})"
    else:
        label = f"Impôt dû (IS {P['IS_TAUX'] * 100:g} %)"
        detail = ("(IMF exonéré : entreprise de moins de 3 ans)" if exo_imf
                  else f"(IMF minimum : {fcfa(imf_theo)})")
    return {"benefice": benefice, "impot": max(is_, imf), "label": label, "detail": detail}


def ir_annuel(base, parts):
    reste, prec, total = base / parts, 0, 0.0
    for plafond, taux in P["IR_BAREME"]:
        tranche = reste if plafond is None else min(reste, plafond - prec)
        total += max(0, tranche) * taux
        if plafond is None or reste <= plafond - prec:
            break
        reste -= tranche
        prec = plafond
    return total * parts


def trimf(brut_annuel):
    for plafond, montant in P["TRIMF"]:
        if plafond is None or brut_annuel < plafond:
            return montant


def simuler_salaire(brut_m, cadre, parts, nouvelle=False):
    """Coût et net annuels pour UN salarié (12 mois), avec le détail des cotisations."""
    if brut_m <= 0:
        return None
    rg = min(brut_m, P["IPRES_RG_PLAFOND"])
    rc = max(0, min(brut_m, P["IPRES_RC_PLAFOND"]) - P["IPRES_RG_PLAFOND"]) if cadre else 0
    css = min(brut_m, P["CSS_PLAFOND"])
    cfce_taux = 0 if (nouvelle and P["CFCE_EXO_NOUVELLE"]) else P["CFCE_EMP"]
    ipres_sal = (rg * P["IPRES_RG_SAL"] + rc * P["IPRES_RC_SAL"]) * 12
    ipres_emp = (rg * P["IPRES_RG_EMP"] + rc * P["IPRES_RC_EMP"]) * 12
    css_pf, css_at = css * P["CSS_PF_EMP"] * 12, css * P["CSS_AT_EMP"] * 12
    cfce = brut_m * cfce_taux * 12
    brut_a = brut_m * 12
    base = brut_a - ipres_sal
    base -= min(base * P["IR_FRAIS_PRO"], P["IR_FRAIS_PRO_MAX"])
    ir, tr = ir_annuel(max(0, base), parts), trimf(brut_a)
    charges_emp = ipres_emp + css_pf + css_at + cfce
    return {"brut": brut_a, "cotis_sal": ipres_sal, "ipres_sal": ipres_sal, "ipres_emp": ipres_emp,
            "css_pf": css_pf, "css_at": css_at, "cfce": cfce, "ir": ir, "trimf": tr,
            "net": brut_a - ipres_sal - ir - tr, "charges_emp": charges_emp, "cout": brut_a + charges_emp}


def multiplier(s, n):
    return {k: v * n for k, v in s.items()} if s and n > 1 else s


def frais_creation(statut):
    f = FRAIS[statut]
    return {"officiel": f["officiel"], "notaire": f["notaire"],
            "total": (f["officiel"][0] + f["notaire"][0], f["officiel"][1] + f["notaire"][1])}


def simuler(f):
    associes = 2 if f["associes"] == "2" else 1
    activite = f["activite"] if f["activite"] in P["CGU"] else "services"
    ca, charges = entier(f["ca"]), entier(f["charges"])
    protection, invest, nouvelle = f["protection"], f["investisseurs"], f["nouvelle"]
    parts = max(1.0, min(5.0, float(f["parts"] or 1)))
    nb = entier(f["nb_salaries"])
    brut_gerant, brut_staff = entier(f["salaire_gerant"]), entier(f["salaire_staff"])

    gerant = simuler_salaire(brut_gerant, f["cadre"], parts, nouvelle)
    staff = multiplier(simuler_salaire(brut_staff, False, 1, nouvelle), nb)
    cout_staff = staff["cout"] if staff else 0
    cout_gerant = gerant["cout"] if gerant else 0
    smig = any(0 < v < P["SMIG_MENSUEL"] for v in (brut_gerant, brut_staff))

    statut = recommander_statut(associes, ca, protection, invest)
    regime = "CGU" if statut == "EI" and ca <= P["SEUIL_CGU_TVA"] else "Réel"
    statut_b = statut if statut != "EI" else "SUARL"

    # Colonne A : EI au CGU. Le dirigeant n'est pas salarié : aucun IPRES/CSS/IR/TRIMF sur
    # salaire_gerant, seulement sur les employés. Impossible à plusieurs associés.
    a = {"titre": "EI au CGU", "ok": associes == 1 and ca <= P["SEUIL_CGU_TVA"]}
    if a["ok"]:
        c = impot_cgu(ca, activite)
        a.update(impot=c["impot"], label=c["label"], detail=c["detail"],
                 sociaux=staff["charges_emp"] if staff else 0,
                 perso=(staff["ir"] + staff["trimf"]) if staff else 0,
                 dispo=ca - charges - cout_staff - c["impot"])
    # Colonne B : société au réel (le gérant se verse un salaire)
    r = impot_reel(ca, charges + cout_gerant + cout_staff, exo_imf=nouvelle and P["IMF_EXO_NOUVELLE"])
    net_gerant = gerant["net"] if gerant else 0
    resultat = r["benefice"] - r["impot"]
    b = {"titre": f"{statut_b} au réel", "ok": True, "impot": r["impot"], "label": r["label"], "detail": r["detail"],
         "sociaux": sum(s["charges_emp"] for s in (gerant, staff) if s),
         "perso": sum(s["ir"] + s["trimf"] for s in (gerant, staff) if s),
         "net_gerant": net_gerant, "resultat": resultat, "dispo": net_gerant + resultat}

    principal = a if regime == "CGU" else b
    alerte = None
    if a["ok"]:
        autre = b if principal is a else a
        ecart = principal["impot"] - autre["impot"]
        if ecart >= max(200_000, 0.2 * autre["impot"]):
            alerte = {"reco": principal["titre"], "alt": autre["titre"], "economie": ecart,
                      "raison": "investisseurs" if statut == "SASU" else "protection"}

    societes = None
    if associes == 2:
        societes = {"impot": b["impot"], "SARL": frais_creation("SARL"), "SAS": frais_creation("SAS")}

    partage = "\n".join([
        "SenEntreprise - Mon bilan",
        f"Statut recommandé : {STATUTS[statut][0]}",
        f"Régime fiscal : {'CGU' if regime == 'CGU' else 'Réel (IS / IMF)'}",
        f"CA estimé : {fcfa(ca)}",
        f"Impôt annuel estimé : {fcfa(principal['impot'])}",
        f"Net disponible : {fcfa(principal['dispo'])}",
        "(Estimation indicative)"])

    return {"statut": statut, "statut_nom": STATUTS[statut][0], "desc": STATUTS[statut][1],
            "associes": associes, "regime": regime, "principal": principal, "tva": ca > P["SEUIL_CGU_TVA"],
            "ca": ca, "charges": charges, "benefice": max(0, ca - charges),
            "a": a, "b": b, "gerant": gerant, "staff": staff, "nb": nb, "nouvelle": nouvelle,
            "meilleur": "A" if a["ok"] and a["dispo"] >= b["dispo"] else "B",
            "alerte": alerte, "frais": frais_creation(statut), "smig": smig,
            "smig_valeur": P["SMIG_MENSUEL"], "societes": societes, "partage": partage}
