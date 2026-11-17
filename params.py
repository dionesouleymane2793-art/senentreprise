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
    # --- IR sur salaires (barème annuel par part) ---
    "IR_FRAIS_PRO": 0.30, "IR_FRAIS_PRO_MAX": 900_000,
    "IR_BAREME": [(630_000, 0.0), (1_500_000, 0.20), (4_000_000, 0.30),
                  (8_000_000, 0.35), (13_500_000, 0.37), (50_000_000, 0.40), (None, 0.43)],  # 43 % au-delà de 50 M (DGID)
    # TRIMF : (plafond annuel brut, montant). Jusqu'à 7 M : recoupé sur plusieurs sources.
    # Au-delà de 7 M (jusqu'à 36 000) : tranches exactes NON confirmées -> à vérifier.
    "TRIMF": [(600_000, 900), (1_000_000, 3_600), (2_000_000, 4_800),
              (7_000_000, 12_000), (None, 36_000)],
}
