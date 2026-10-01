"""
Jan-Sahayak AI - Deterministic Bharat Schemes Reasoning Engine
Audits citizen eligibility across configured schemes using rigorous deterministic rule evaluation.
Calculates: ELIGIBLE | POTENTIALLY ELIGIBLE | INSUFFICIENT DATA | NOT ELIGIBLE.
"""

import json
from pathlib import Path
from typing import Dict, Any, List


class SchemeReasoningEngine:
    """Deterministic, explainable rules engine that evaluates citizen eligibility."""

    def __init__(self, db_path: str = None):
        self.name = "Deterministic Schemes Reasoning Engine"
        if db_path is None:
            db_path = Path(__file__).parent / "data" / "schemes_db.json"
        
        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.schemes = data.get("schemes", [])

    def evaluate_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates citizen against all schemes and categorizes them into standard categories:
        ELIGIBLE, POTENTIALLY ELIGIBLE, INSUFFICIENT DATA, NOT ELIGIBLE.
        """
        eligible = []
        potentially_eligible = []
        insufficient_data = []
        not_eligible = []
        total_estimated_annual_benefit_inr = 0

        for scheme in self.schemes:
            eval_result = self._evaluate_single_scheme(scheme, profile)
            status = eval_result["status"]

            if status == "ELIGIBLE":
                eligible.append(eval_result)
                val = scheme.get("benefits", {}).get("estimated_annual_value_inr", 0)
                total_estimated_annual_benefit_inr += val
            elif status == "POTENTIALLY ELIGIBLE":
                potentially_eligible.append(eval_result)
                val = scheme.get("benefits", {}).get("estimated_annual_value_inr", 0)
                # Count half weight for potential value
                total_estimated_annual_benefit_inr += int(val * 0.5)
            elif status == "INSUFFICIENT DATA":
                insufficient_data.append(eval_result)
            else:
                not_eligible.append(eval_result)

        # Sort by match score
        eligible.sort(key=lambda x: x["match_score"], reverse=True)
        potentially_eligible.sort(key=lambda x: x["match_score"], reverse=True)

        return {
            "total_schemes_configured": len(self.schemes),
            "eligible_count": len(eligible),
            "potential_count": len(potentially_eligible),
            "insufficient_count": len(insufficient_data),
            "not_eligible_count": len(not_eligible),
            "qualified_count": len(eligible) + len(potentially_eligible),
            "eligible_schemes": eligible,
            "potentially_eligible_schemes": potentially_eligible,
            "insufficient_data_schemes": insufficient_data,
            "not_eligible_schemes": not_eligible,
            "qualified_schemes": eligible + potentially_eligible, # backwards compatibility
            "total_estimated_annual_benefit_inr": total_estimated_annual_benefit_inr,
            "headline_schemes": [s["scheme_name"] for s in eligible[:3]]
        }

    def _evaluate_single_scheme(self, scheme: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
        sid = scheme["id"]
        el = scheme.get("eligibility", {})
        existing_docs = profile.get("existing_documents", [])
        existing_lower = [d.lower() for d in existing_docs]

        why_qualify = []
        why_ineligible = []
        missing_info = []

        user_age = profile.get("age")
        user_gender = profile.get("gender", "All")
        user_state = profile.get("state", "").strip()
        user_occ = profile.get("occupation", "General").strip()
        user_inc = profile.get("annual_income")
        user_land = profile.get("landholding_acres", 0.0)
        user_caste = profile.get("social_category", "General")
        specials = profile.get("special_conditions", [])
        has_young_children = profile.get("has_young_children", False)
        housing = profile.get("housing_condition", "").lower()

        # 1. State Criteria
        allowed_states = scheme.get("state", ["All India"])
        if "All India" not in allowed_states:
            if not any(st.lower() in user_state.lower() for st in allowed_states):
                why_ineligible.append(f"Restricted to residents of {', '.join(allowed_states)} (Applicant resides in {user_state}).")
            else:
                why_qualify.append(f"Permanent residency verified for {user_state}.")
        else:
            why_qualify.append("National scheme: All Indian States & UTs supported.")

        # 2. Income Criteria
        max_inc = el.get("max_income")
        if max_inc is not None:
            if user_inc is None:
                missing_info.append("Annual household income information not provided.")
            elif user_inc > max_inc:
                why_ineligible.append(f"Annual household income ₹{user_inc:,.0f} exceeds scheme ceiling of ₹{max_inc:,.0f}.")
            else:
                why_qualify.append(f"Income criteria satisfied: ₹{user_inc:,.0f} is within ceiling of ₹{max_inc:,.0f}.")

        # 3. Age Bounds
        min_age = el.get("min_age")
        max_age = el.get("max_age")
        if min_age is not None:
            if user_age is None:
                missing_info.append("Age information required.")
            elif user_age < min_age:
                why_ineligible.append(f"Age criteria not met: Minimum required is {min_age} years (Applicant: {user_age} years).")
            else:
                why_qualify.append(f"Age criteria satisfied: {user_age} years (Minimum: {min_age}).")

        if max_age is not None:
            if user_age is not None and user_age > max_age:
                why_ineligible.append(f"Age criteria not met: Maximum permissible is {max_age} years (Applicant: {user_age} years).")

        # 4. Gender Check
        allowed_gender = el.get("gender", ["All"])
        if "All" not in allowed_gender:
            if user_gender not in allowed_gender:
                why_ineligible.append(f"Designated exclusively for {', '.join(allowed_gender)} applicants.")
            else:
                why_qualify.append(f"Gender criteria satisfied ({user_gender}).")

        # 5. Rural / Urban Check
        allowed_area = el.get("rural_urban", ["All"])
        user_area = profile.get("rural_urban", "All")
        if "All" not in allowed_area and user_area not in allowed_area and user_area != "All":
            why_ineligible.append(f"Requires residential location to be {', '.join(allowed_area)} (Applicant: {user_area}).")

        # 6. Scheme-Specific Occupation & Nuance Checks
        allowed_occs = el.get("occupations", ["All"])
        if "All" not in allowed_occs:
            occ_matched = any(o.lower() in user_occ.lower() for o in allowed_occs)
            if not occ_matched:
                why_ineligible.append(f"Designated for {', '.join(allowed_occs)} (Applicant: {user_occ}).")
            else:
                why_qualify.append(f"Occupation verified: {user_occ}.")

        # Specific scheme deep rules
        if sid == "pm_kisan":
            if user_land is None or user_land <= 0:
                if any(o.lower() in user_occ.lower() for o in ["farmer", "agri"]):
                    missing_info.append("Cultivable land record information needed.")
                else:
                    why_ineligible.append("Requires cultivable agricultural landholding.")
            elif user_land > el.get("max_land_acres", 5.0):
                why_ineligible.append(f"Landholding {user_land} acres exceeds marginal farmer ceiling of 5.0 acres.")
            else:
                why_qualify.append(f"Cultivable agricultural landholding verified ({user_land} acres).")

        elif sid == "pm_vishwakarma":
            if not any(w in specials for w in ["Artisan Trade", "Artisan"]) and "artisan" not in user_occ.lower():
                why_ineligible.append("Requires engagement in one of the 18 recognized traditional artisan trades.")
            else:
                why_qualify.append("Traditional family trade / artisan practice confirmed.")

        elif sid == "sukanya_samriddhi":
            if not has_young_children:
                why_ineligible.append("Requires having at least one girl child under 10 years of age.")
            else:
                why_qualify.append("Family has qualifying girl child under age 10.")

        elif sid == "ignwps_widow_pension":
            if "Widow" not in specials:
                why_ineligible.append("Designated exclusively for widowed women.")
            else:
                why_qualify.append("Widow status officially attested for pension entitlement.")

        elif sid == "rte_admission":
            if not has_young_children:
                why_ineligible.append("Requires child aged between 3 to 7 years for entry class admission.")
            else:
                why_qualify.append("Qualifying child age criteria satisfied (3-7 years).")
                if user_caste in ["SC", "ST", "OBC", "EWS"]:
                    why_qualify.append(f"Disadvantaged / EWS category criteria satisfied ({user_caste}).")

        elif sid == "pmay_gramin":
            if "pucca" in housing and "semi" not in housing and "kutcha" not in housing:
                why_ineligible.append("Applicant already possesses a durable pucca house.")
            else:
                why_qualify.append("Dwelling status satisfies PMAY-G prioritization (kutcha/semi-pucca).")

        # 7. Document Analysis for this Scheme
        mandatories = scheme.get("documents_required", [])
        verified_docs = []
        missing_docs = []

        for doc in mandatories:
            doc_lower = doc.lower()
            is_held = False
            for ex in existing_lower:
                if any(t in doc_lower and t in ex for t in ["aadhaar", "bank", "ration", "khasra", "death", "voter", "samagra", "birth", "income", "caste"]):
                    is_held = True
                    break
            if is_held:
                verified_docs.append(doc)
            else:
                missing_docs.append(doc)

        # 8. Determine Final Status
        if len(why_ineligible) > 0:
            status = "NOT ELIGIBLE"
            match_score = 0
            next_step = "Explore alternative welfare programs in your demographic category."
        elif len(missing_info) > 0:
            status = "INSUFFICIENT DATA"
            match_score = 40
            next_step = f"Provide missing information: {', '.join(missing_info)}."
        elif len(missing_docs) >= 3:
            status = "POTENTIALLY ELIGIBLE"
            match_score = max(55, 100 - (len(missing_docs) * 10))
            next_step = f"Obtain missing prerequisite documents before submission: {missing_docs[0]}."
        else:
            status = "ELIGIBLE"
            match_score = max(85, 100 - (len(missing_docs) * 5))
            next_step = "Proceed to submit official beneficiary registration dossier."

        return {
            "scheme_id": scheme["id"],
            "scheme_name": scheme["name"],
            "hindi_name": scheme.get("hindi_name", ""),
            "category": scheme.get("category", "General"),
            "government": scheme.get("government", "Central"),
            "ministry": scheme.get("ministry", ""),
            "status": status,
            "match_score": match_score,
            "benefit_summary": scheme.get("benefits", {}),
            "estimated_annual_value_inr": scheme.get("benefits", {}).get("estimated_annual_value_inr", 0),
            "why_qualify": why_qualify,
            "why_ineligible": why_ineligible,
            "missing_info": missing_info,
            "reasoning_trace": why_qualify if status != "NOT ELIGIBLE" else why_ineligible,
            "mandatory_documents": mandatories,
            "verified_documents": verified_docs,
            "missing_documents": missing_docs,
            "application_method": scheme.get("application_method", "Online / CSC Kiosk"),
            "estimated_effort": scheme.get("estimated_effort", "Medium"),
            "official_url": scheme.get("official_url", ""),
            "rule_explanation": scheme.get("rule_explanation", ""),
            "action_plan_steps": scheme.get("action_plan_steps", []),
            "next_step": next_step
        }
