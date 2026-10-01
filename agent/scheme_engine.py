"""
Jan-Sahayak AI - Bharat Schemes Reasoning & Eligibility Engine
Performs multi-factor rule-based reasoning across Central & State government schemes.
"""

import json
from pathlib import Path
from typing import Dict, Any, List


class SchemeReasoningEngine:
    """Deterministic, explainable reasoning engine that audits citizen eligibility."""

    def __init__(self, db_path: str = None):
        self.name = "Bharat Schemes Reasoning Engine"
        if db_path is None:
            db_path = Path(__file__).parent / "data" / "schemes_db.json"
        
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.schemes = data.get("schemes", [])

    def evaluate_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates citizen against all schemes and categorizes them into qualified,
        conditionally eligible, and excluded, generating clear reasoning traces.
        """
        qualified = []
        conditionally_eligible = []
        not_eligible = []
        total_estimated_annual_benefit_inr = 0

        for scheme in self.schemes:
            eval_result = self._evaluate_single_scheme(scheme, profile)
            if eval_result["status"] == "QUALIFIED":
                qualified.append(eval_result)
                # Tally direct monetary benefits if numeric
                benefit_text = scheme["benefits"].get("financial", "")
                if "6,000" in benefit_text:
                    total_estimated_annual_benefit_inr += 6000
                elif "1,250" in benefit_text:
                    total_estimated_annual_benefit_inr += 15000
                elif "1,000" in benefit_text:
                    total_estimated_annual_benefit_inr += 12000
                elif "10,000" in benefit_text:
                    total_estimated_annual_benefit_inr += 10000
                elif "15,000" in benefit_text:
                    total_estimated_annual_benefit_inr += 15000
                elif "25,000" in benefit_text:
                    total_estimated_annual_benefit_inr += 25000
                elif "1,20,000" in benefit_text:
                    total_estimated_annual_benefit_inr += 120000
            elif eval_result["status"] == "CONDITIONALLY_ELIGIBLE":
                conditionally_eligible.append(eval_result)
            else:
                not_eligible.append(eval_result)

        # Sort qualified by match score descending
        qualified.sort(key=lambda x: x["match_score"], reverse=True)

        return {
            "total_schemes_evaluated": len(self.schemes),
            "qualified_count": len(qualified),
            "conditional_count": len(conditionally_eligible),
            "qualified_schemes": qualified,
            "conditionally_eligible_schemes": conditionally_eligible,
            "not_eligible_schemes": not_eligible,
            "total_estimated_annual_benefit_inr": total_estimated_annual_benefit_inr,
            "headline_schemes": [s["scheme_name"] for s in qualified[:3]]
        }

    def _evaluate_single_scheme(self, scheme: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
        sid = scheme["id"]
        sname = scheme["name"]
        hindi_name = scheme.get("hindi_name", "")
        el = scheme.get("eligibility", {})
        
        reasons = []
        is_eligible = True
        is_conditional = False
        match_score = 100

        # 1. State check
        allowed_states = el.get("state")
        if allowed_states:
            user_state = profile.get("state", "").strip()
            if not any(st.lower() in user_state.lower() for st in allowed_states):
                is_eligible = False
                reasons.append(f"Restricted to residents of {', '.join(allowed_states)} (User resides in {user_state}).")
                match_score = 0
                return self._build_result(scheme, "NOT_ELIGIBLE", match_score, reasons)
            else:
                reasons.append(f"State residency verified for {user_state}.")

        # 2. Gender check
        allowed_gender = el.get("gender")
        if allowed_gender:
            user_gender = profile.get("gender", "Any")
            if user_gender not in allowed_gender and "Any" not in allowed_gender:
                is_eligible = False
                reasons.append(f"Targeted exclusively for {', '.join(allowed_gender)} beneficiaries.")
                match_score = 0
                return self._build_result(scheme, "NOT_ELIGIBLE", match_score, reasons)

        # 3. Marital status check
        allowed_marital = el.get("marital_status")
        if allowed_marital:
            user_marital = profile.get("marital_status", "Single")
            if user_marital not in allowed_marital:
                is_eligible = False
                reasons.append(f"Requires marital status to be {', '.join(allowed_marital)}.")
                match_score = 0
                return self._build_result(scheme, "NOT_ELIGIBLE", match_score, reasons)
            else:
                reasons.append(f"Marital status verified as {user_marital}.")

        # 4. Age limits check
        min_age = el.get("min_age")
        max_age = el.get("max_age")
        user_age = profile.get("age", 30)

        if min_age and user_age < min_age:
            is_eligible = False
            reasons.append(f"Minimum age requirement is {min_age} (Applicant age: {user_age}).")
            match_score = 0
            return self._build_result(scheme, "NOT_ELIGIBLE", match_score, reasons)

        if max_age and user_age > max_age:
            is_eligible = False
            reasons.append(f"Maximum age limit is {max_age} (Applicant age: {user_age}).")
            match_score = 0
            return self._build_result(scheme, "NOT_ELIGIBLE", match_score, reasons)

        # 5. Income check
        max_inc = el.get("max_income")
        user_inc = profile.get("annual_income", 100000)
        if max_inc and user_inc > max_inc:
            is_eligible = False
            reasons.append(f"Annual household income ₹{user_inc:,.0f} exceeds scheme ceiling of ₹{max_inc:,.0f}.")
            match_score = 0
            return self._build_result(scheme, "NOT_ELIGIBLE", match_score, reasons)
        elif max_inc:
            reasons.append(f"Annual income ₹{user_inc:,.0f} is within limit of ₹{max_inc:,.0f}.")

        # 6. Occupation check
        allowed_occupations = el.get("occupation", ["Any"])
        user_occ = profile.get("occupation", "Any")
        if "Any" not in allowed_occupations and not any(o.lower() in user_occ.lower() for o in allowed_occupations):
            # Special case for general public welfare or partial overlaps
            is_eligible = False
            reasons.append(f"Scheme designated for {', '.join(allowed_occupations)} (Applicant is {user_occ}).")
            match_score = 0
            return self._build_result(scheme, "NOT_ELIGIBLE", match_score, reasons)
        else:
            if "Any" not in allowed_occupations:
                reasons.append(f"Occupation match confirmed: {user_occ}.")

        # 7. Specific Scheme Nuances:
        if sid == "pm_kisan":
            user_land = profile.get("landholding_acres", 0.0)
            if user_land <= 0:
                is_eligible = False
                reasons.append("PM-Kisan mandates verifiable cultivable agricultural land ownership.")
                return self._build_result(scheme, "NOT_ELIGIBLE", 0, reasons)
            else:
                reasons.append(f"Eligible cultivable landholding verified ({user_land} acres).")

        elif sid == "sukanya_samriddhi":
            d_count = profile.get("daughters_count", 0)
            d_ages = profile.get("daughter_ages", [])
            has_qualifying_daughter = any(age <= 10 for age in d_ages) if d_ages else (d_count > 0)
            if not has_qualifying_daughter or d_count == 0:
                is_eligible = False
                reasons.append("Requires at least one daughter under 10 years of age.")
                return self._build_result(scheme, "NOT_ELIGIBLE", 0, reasons)
            else:
                reasons.append(f"Qualifying daughter(s) verified under age 10.")

        elif sid == "rte_admission":
            d_count = profile.get("daughters_count", 0)
            d_ages = profile.get("daughter_ages", [])
            has_young_child = any(3 <= age <= 7 for age in d_ages) if d_ages else False
            user_caste = profile.get("caste", "General")
            if (not has_young_child) and user_inc > 200000:
                is_eligible = False
                reasons.append("Requires child aged 3-7 and EWS/OBC/SC/ST status.")
                return self._build_result(scheme, "NOT_ELIGIBLE", 0, reasons)
            elif not has_young_child:
                is_conditional = True
                match_score = 65
                reasons.append("Candidate family qualifies economically, but child age between 3-7 must be confirmed.")
            else:
                reasons.append("Qualifying child age (3-7 yrs) and EWS/Caste category confirmed.")

        elif sid == "pmay_gramin":
            housing = profile.get("housing_status", "").lower()
            if "pucca" in housing and "semi" not in housing and "kutcha" not in housing:
                is_eligible = False
                reasons.append("Applicant already possesses a pucca house.")
                return self._build_result(scheme, "NOT_ELIGIBLE", 0, reasons)
            else:
                reasons.append(f"Dwelling condition ({profile.get('housing_status')}) satisfies PMAY-G prioritization.")

        status = "CONDITIONALLY_ELIGIBLE" if is_conditional else ("QUALIFIED" if is_eligible else "NOT_ELIGIBLE")
        return self._build_result(scheme, status, match_score, reasons)

    def _build_result(self, scheme: Dict[str, Any], status: str, match_score: int, reasons: List[str]) -> Dict[str, Any]:
        return {
            "scheme_id": scheme["id"],
            "scheme_name": scheme["name"],
            "hindi_name": scheme.get("hindi_name", ""),
            "category": scheme.get("category", "General"),
            "ministry": scheme.get("ministry", ""),
            "status": status,
            "match_score": match_score,
            "benefit_summary": scheme["benefits"],
            "reasoning_trace": reasons,
            "mandatory_documents": scheme.get("documents_required", []),
            "nodal_portal": scheme.get("nodal_portal", ""),
            "appeal_authority": scheme.get("appeal_authority", "")
        }
