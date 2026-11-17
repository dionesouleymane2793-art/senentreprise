# params.py - TOUS les taux et seuils (à vérifier avec le CGI / la DGID)

P = {
    "TVA_TAUX": 0.18,
    "SEUIL_CGU_TVA": 50_000_000,
    # CGU : (taux, minimum). Taux 5 % services / 2 % commerce : confirmés (site DGID).
    # Les minimums 25 000 / 30 000 : NON confirmés, à vérifier.
    "CGU": {"commerce": (0.02, 25_000), "services": (0.05, 30_000)},
    "IS_TAUX": 0.30,
    "IMF_TAUX": 0.005, "IMF_MIN": 500_000, "IMF_MAX": 5_000_000,
    "SAS_CA": 200_000_000,  # seuil arbitraire pour suggérer une SAS
    # --- Charges sociales (mensuel) ---
    "IPRES_RG_PLAFOND": 360_000, "IPRES_RG_SAL": 0.056, "IPRES_RG_EMP": 0.084,
    "IPRES_RC_PLAFOND": 1_080_000, "IPRES_RC_SAL": 0.024, "IPRES_RC_EMP": 0.036,  # cadres
    "CSS_PLAFOND": 63_000, "CSS_PF_EMP": 0.07, "CSS_AT_EMP": 0.01,  # AT : 1 %, 3 % ou 5 %
    "CFCE_EMP": 0.03,  # à vérifier : peut avoir évolué avec la réforme du CGI
    # Entreprises de moins de 3 ans : exonération d'IMF et de CFCE (LFI 2020, relayée par la presse
    # économique sénégalaise). Conditions exactes à confirmer auprès de la DGID.
    "IMF_EXO_NOUVELLE": True, "CFCE_EXO_NOUVELLE": True,
    # --- IR sur salaires (barème annuel par part) ---
    "IR_FRAIS_PRO": 0.30, "IR_FRAIS_PRO_MAX": 900_000,
    "IR_BAREME": [(630_000, 0.0), (1_500_000, 0.20), (4_000_000, 0.30),
                  (8_000_000, 0.35), (13_500_000, 0.37), (50_000_000, 0.40), (None, 0.43)],  # 43 % au-delà de 50 M (DGID)
    # TRIMF : (plafond annuel brut, montant). Jusqu'à 7 M : recoupé sur plusieurs sources.
    # Au-delà de 7 M (jusqu'à 36 000) : tranches exactes NON confirmées -> à vérifier.
    "TRIMF": [(600_000, 900), (1_000_000, 3_600), (2_000_000, 4_800),
              (7_000_000, 12_000), (None, 36_000)],
}


# Frais de création (FCFA) : ordres de grandeur issus de sources en ligne non officielles.
# NINEA : gratuit via le guichet unique. A VÉRIFIER auprès du guichet APIX.
FRAIS = {
    "EI":    {"officiel": (10_000, 50_000),  "notaire": (0, 0)},
    "SUARL": {"officiel": (25_000, 100_000), "notaire": (0, 100_000)},
    "SARL":  {"officiel": (25_000, 100_000), "notaire": (50_000, 150_000)},
    "SAS":   {"officiel": (25_000, 100_000), "notaire": (50_000, 150_000)},
}

# Infobulles (?) : explications simples
GLOSSAIRE = {
    "CGU": ("CGU - Contribution Globale Unique",
            "Un impôt simplifié pour les petits entrepreneurs individuels (CA jusqu'à 50 millions FCFA). "
            "Un seul paiement remplace plusieurs impôts : 5 % du CA pour les services, 2 % pour le commerce."),
    "IMF": ("IMF - Impôt Minimum Forfaitaire",
            "Un impôt minimum que paie une société même sans bénéfice : 0,5 % du chiffre d'affaires, "
            "avec un minimum de 500 000 et un maximum de 5 000 000 FCFA. On paie le plus élevé entre l'IS et l'IMF."),
    "IS": ("IS - Impôt sur les Sociétés",
           "L'impôt sur le bénéfice d'une société : 30 % de (chiffre d'affaires - charges)."),
    "TRIMF": ("TRIMF",
              "Une petite taxe annuelle prélevée sur les salaires. Son montant dépend du salaire brut annuel."),
    "FRANCHISE": ("Franchise de TVA",
                  "Sous 50 millions FCFA de chiffre d'affaires, vous ne facturez pas la TVA de 18 % à vos clients "
                  "et vous ne la récupérez pas non plus sur vos achats."),
    "IPRES": ("IPRES",
              "La caisse de retraite des salariés du privé. Le salarié et l'employeur cotisent chacun une part du salaire."),
    "CSS": ("CSS - Caisse de Sécurité Sociale",
            "Elle gère les allocations familiales et les accidents du travail. Seul l'employeur cotise."),
    "CFCE": ("CFCE",
             "Contribution payée par l'employeur sur les salaires versés (3 % dans ce simulateur). "
             "Les entreprises récentes peuvent en être exonérées."),
    "NINEA": ("NINEA", "Le numéro d'identification de votre entreprise, gratuit. Il est délivré avec l'immatriculation au guichet unique de l'APIX."),
    "RCCM": ("RCCM", "Le Registre du Commerce et du Crédit Mobilier : l'immatriculation officielle de votre entreprise."),
}

# Démarches : (id, texte)
CHECKLISTS = [
    ("Entreprise individuelle", [
        ("ei1", "Pièce d'identité valide (CNI ou passeport) + copie"),
        ("ei2", "Extrait de casier judiciaire de moins de 3 mois"),
        ("ei3", "Certificat de résidence ou justificatif de domicile"),
        ("ei4", "Justificatif de l'adresse de l'activité (bail ou attestation)"),
        ("ei5", "Photos d'identité"),
        ("ei6", "Formulaire de déclaration rempli au guichet unique"),
    ]),
    ("SUARL / SARL / SAS", [
        ("so1", "Statuts signés (notaire ou acte sous seing privé)"),
        ("so2", "Pièces d'identité de chaque associé et du gérant"),
        ("so3", "Extrait de casier judiciaire du gérant"),
        ("so4", "Justificatif du siège social (bail ou attestation)"),
        ("so5", "Attestation de dépôt ou de libération du capital"),
        ("so6", "Déclaration de non-condamnation du gérant"),
        ("so7", "Annonce légale de la création"),
    ]),
    ("Après l'immatriculation", [
        ("ap1", "Récupérer le NINEA et l'attestation d'existence fiscale"),
        ("ap2", "Ouvrir un compte bancaire professionnel"),
        ("ap3", "Déclarer vos salariés à l'IPRES et à la CSS (si vous embauchez)"),
    ]),
]

LIENS = [
    ("Création d'entreprise (guichet APIX)", "https://www.creationdentreprise.sn", "NINEA + RCCM en un seul dépôt"),
    ("APIX", "https://www.investinsenegal.com", "Agence de promotion des investissements"),
    ("DER/FJ", "https://www.der.sn", "Financement pour jeunes et femmes entrepreneurs"),
    ("ADEPME", "https://www.adepme.sn", "Accompagnement des PME"),
    ("Sénégal PME", "https://www.google.com/search?q=S%C3%A9n%C3%A9gal+PME+portail+officiel", "Recherche (lien officiel non vérifié)"),
    ("DGID (impôts)", "https://www.dgid.sn", "Code général des impôts et déclarations"),
]
