"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 2: Business Engine 2 — Finance Engine (finance_engine.py)
=====================================================================
Motor Financiero Oficial (VAN, TIR, ROI, Payback, Costo por Casa Pasada)
"""

import sqlite3
import os

DB_FILE = "somos_network.db"

class FinanceEngine:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), DB_FILE)
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    @staticmethod
    def calculate_van(capex, annual_cash_flows, discount_rate=0.075):
        """
        Calcula el Valor Actual Neto (VAN / NPV).
        Fórmula: VAN = sum(CF_t / (1 + r)^t) - CAPEX_0
        """
        van = -capex
        for t, cf in enumerate(annual_cash_flows, start=1):
            van += cf / ((1 + discount_rate) ** t)
        return round(van, 2)

    @staticmethod
    def calculate_tir(capex, annual_cash_flows):
        """
        Calcula la Tasa Interna de Retorno (TIR / IRR) mediante el método de bisección.
        """
        def npv_at_r(r):
            val = -capex
            for t, cf in enumerate(annual_cash_flows, start=1):
                val += cf / ((1 + r) ** t)
            return val

        low, high = -0.5, 2.0
        for _ in range(60):
            mid = (low + high) / 2.0
            val = npv_at_r(mid)
            if abs(val) < 1e-4:
                break
            if val > 0:
                low = mid
            else:
                high = mid
        return round(mid * 100.0, 2)

    @staticmethod
    def calculate_roi(capex, total_net_income):
        """
        Calcula el Retorno de Inversión acumulado (ROI %).
        """
        if capex <= 0:
            return 0.0
        return round(((total_net_income - capex) / capex) * 100.0, 2)

    @staticmethod
    def calculate_payback(capex, opex_annual, arpu_monthly, initial_subs, growth_rate, years=5):
        """
        Calcula el tiempo de recuperación (Payback) en meses.
        """
        cumulative = -capex
        for month in range(1, years * 12 + 1):
            monthly_subs = initial_subs * ((1 + growth_rate) ** (month / 12.0))
            monthly_net = (monthly_subs * arpu_monthly) - (opex_annual / 12.0)
            cumulative += monthly_net
            if cumulative >= 0:
                return round(month, 1)
        return round(years * 12.0, 1)

    @staticmethod
    def validate_cphp(capex_access, homes_passed, limit=500.0):
        """
        Valida que el Costo por Casa Pasada (CPHP) sea <= $500 MXN.
        """
        if homes_passed <= 0:
            return 0.0, False
        cphp = capex_access / homes_passed
        return round(cphp, 2), (cphp <= limit)

    def run_full_financial_analysis(self, discount_rate=0.075, arpu_multiplier=1.0, opex_multiplier=1.0):
        """
        Ejecuta el análisis financiero completo para todas las ciudades conectadas.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT f.city_id, c.name, c.tier_category, f.capex_initial_mxn, f.opex_annual_mxn,
                   f.arpu_monthly_mxn, f.subscriber_growth_rate, f.projection_years
            FROM financial_projections f
            JOIN cities c ON f.city_id = c.city_id
        """)
        rows = cursor.fetchall()

        results = []
        total_capex = 0.0
        total_van = 0.0

        for city_id, name, tier, capex, opex, arpu, growth, years in rows:
            adj_arpu = arpu * arpu_multiplier
            adj_opex = opex * opex_multiplier

            # Obtener suscriptores base
            cursor.execute("SELECT SUM(active_subscribers) FROM access_clusters WHERE city_id = ?", (city_id,))
            subs_row = cursor.fetchone()
            initial_subs = subs_row[0] if (subs_row and subs_row[0]) else 3000

            # Flujos anuales
            cash_flows = []
            total_net = 0.0
            curr_subs = initial_subs
            for t in range(1, years + 1):
                curr_subs = curr_subs * (1 + growth)
                annual_rev = curr_subs * adj_arpu * 12.0
                net_cf = annual_rev - adj_opex
                cash_flows.append(net_cf)
                total_net += net_cf

            van = self.calculate_van(capex, cash_flows, discount_rate)
            tir = self.calculate_tir(capex, cash_flows)
            roi = self.calculate_roi(capex, total_net)
            payback = self.calculate_payback(capex, adj_opex, adj_arpu, initial_subs, growth, years)

            total_capex += capex
            total_van += van

            results.append({
                "city_id": city_id,
                "city_name": name,
                "tier_category": tier,
                "capex_initial_mxn": capex,
                "opex_annual_mxn": adj_opex,
                "arpu_monthly_mxn": adj_arpu,
                "van_mxn": van,
                "tir_percent": tir,
                "roi_percent": roi,
                "payback_months": payback
            })

        conn.close()

        summary = {
            "discount_rate_used": discount_rate,
            "total_capex_national_mxn": round(total_capex, 2),
            "total_van_national_mxn": round(total_van, 2),
            "national_roi_percent": round(((sum(r["van_mxn"] for r in results) / total_capex) * 100.0), 2) if total_capex > 0 else 0.0,
            "city_breakdown": results
        }
        return summary

if __name__ == "__main__":
    engine = FinanceEngine()
    analysis = engine.run_full_financial_analysis(discount_rate=0.075)
    print(f"--- MOTOR FINANCIERO OFICIAL (VAN / TIR / ROI) ---")
    print(f"CAPEX Nacional Total: ${analysis['total_capex_national_mxn']:,.2f} MXN")
    print(f"VAN Nacional Acumulado (7.5%): ${analysis['total_van_national_mxn']:,.2f} MXN")
    for r in analysis["city_breakdown"]:
        print(f"  {r['city_name']} ({r['tier_category']}): VAN=${r['van_mxn']:,.2f} | TIR={r['tir_percent']}% | ROI={r['roi_percent']}% | Payback={r['payback_months']}m")
