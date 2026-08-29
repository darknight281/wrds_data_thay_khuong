"""Kiem tra subscription WRDS bang cach doc thu 1 dong du lieu that tu bang chinh.

Dung env vars: wrds_id (username) va wrds_password.
Yeu cau: pip install "psycopg[binary]"   (package `wrds` khong cai duoc tren Python 3.14)
Chay:    python check_wrds_subscriptions.py
"""

import os
import sys

try:
    import psycopg
except ImportError:
    sys.exit('Chua cai driver: pip install "psycopg[binary]"')

user = os.environ.get("wrds_id") or os.environ.get("WRDS_USERNAME")
pwd = os.environ.get("wrds_password") or os.environ.get("WRDS_PASSWORD")
if not user or not pwd:
    sys.exit("Thieu env vars wrds_id / wrds_password")

# (mo ta, schema, bang chinh) — bang de thu SELECT 1 dong
CHECKS = [
    ("Calcbench - Income Tax footnotes", "calcbench_income_tax", "tax_fn"),
    ("Calcbench - trial (mien phi)", "calcbench_trial", "normalized_fn"),
    ("ISS Directors (legacy)", "risk_directors", "rmdirectors"),
    ("ISS Directors Global", "iss_directors_global", "committee_detail"),
    ("ISS Governance", "risk_governance", "rmgovernance"),
    ("ISS Incentive Lab", "iss_incentive_lab", "gpbaabs"),
    ("ISS Compensation Analytics", "iss_compensation_analytics", "person_pay"),
    ("ISS Voting Analytics US", "iss_va_vote_us", "vavoteresults"),
    ("ISS Voting Analytics Global", "iss_va_vote_global", "globalvoteresults"),
    ("ISS Mutual Fund Votes", "iss_va_mf", "voteanalysis_npx"),
    ("ISS Climate Core", "iss_climate_core", "climate_core"),
    ("MSCI ESG Ratings", "msci_esg", "msci_esg_ratings"),
    ("MSCI Climate", "msci_climate", "carbon_emiss_n_ener_use"),
    ("KLD (legacy MSCI)", "kld", "history"),
    ("RepRisk v2 - incidents", "reprisk_v2", "v2_risk_incidents"),
    ("RepRisk v2 - company ids", "reprisk_v2", "v2_company_identifiers"),
    ("Compustat funda", "comp", "funda"),
    ("CRSP daily stock", "crsp", "dsf"),
    ("LSEG/Refinitiv ESG", "tr_esg", "wrds_ref_esg"),
    ("Audit Analytics", "audit", "auditfees"),
    ("Sustainalytics", "sustainalytics_all", "esgrr_indicators"),
]

conn = psycopg.connect(
    host="wrds-pgdata.wharton.upenn.edu", port=9737, dbname="wrds",
    user=user, password=pwd, sslmode="require", connect_timeout=30,
)
cur = conn.cursor()
for label, sch, tbl in CHECKS:
    try:
        cur.execute(f'SELECT * FROM "{sch}"."{tbl}" LIMIT 1')
        status = "CO   " if cur.fetchone() else "RONG "
    except Exception:
        conn.rollback()
        status = "KHONG"
    print(f"[{status}] {label}  ({sch}.{tbl})")
conn.close()
