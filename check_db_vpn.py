import sqlite3

conn = sqlite3.connect("somos_network.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cursor.fetchall()]
vpn_found = False

for t in tables:
    cursor.execute(f"PRAGMA table_info({t});")
    cols = [c[1] for c in cursor.fetchall()]
    for c in cols:
        if "vpn" in c.lower():
            print(f"DB Column VPN found in {t}.{c}")
            vpn_found = True
    cursor.execute(f"SELECT * FROM {t}")
    for row in cursor.fetchall():
        for val in row:
            if isinstance(val, str) and "vpn" in val.lower():
                print(f"DB String VPN found in {t}: {val}")
                vpn_found = True

if not vpn_found:
    print("DB is 100% clean of VPN terminology!")
