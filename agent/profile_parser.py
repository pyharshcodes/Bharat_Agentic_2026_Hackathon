"""
Jan-Sahayak AI - Citizen Profile & Progressive Disclosure Agent
Extracts demographic, socio-economic, and documentation attributes based on the Minimum Necessary Data principle.
"""

from typing import Dict, Any, List, Optional
import re

DEMO_PERSONAS = {
    "rameshwar_farmer": {
        "name": "Ramesh",
        "age": 42,
        "gender": "Male",
        "state": "Uttar Pradesh",
        "district": "Gorakhpur",
        "rural_urban": "Rural",
        "occupation": "Farmer",
        "annual_income": 140000,
        "social_category": "OBC",
        "landholding_acres": 1.2,
        "special_conditions": [],
        "has_young_children": True,
        "housing_condition": "Semi-pucca",
        "existing_documents": [
            "Aadhaar Card",
            "Bank Account details (Aadhaar linked NPCI seeded)",
            "Active Mobile Number"
        ],
        "grievance_case": None
    },
    "sunita_street_vendor": {
        "name": "Sunita",
        "age": 34,
        "gender": "Female",
        "state": "Delhi",
        "district": "Central Delhi",
        "rural_urban": "Urban",
        "occupation": "Street Vendor",
        "annual_income": 95000,
        "social_category": "SC",
        "landholding_acres": 0.0,
        "special_conditions": [],
        "has_young_children": True,
        "housing_condition": "Rented single room",
        "existing_documents": [
            "Aadhaar Card",
            "Voter ID / Identity Proof",
            "Active Mobile Number"
        ],
        "grievance_case": None
    },
    "kavita_widow": {
        "name": "Kavita",
        "age": 62,
        "gender": "Female",
        "state": "Madhya Pradesh",
        "district": "Jabalpur",
        "rural_urban": "Rural",
        "occupation": "Agricultural Laborer",
        "annual_income": 45000,
        "social_category": "SC",
        "landholding_acres": 0.0,
        "special_conditions": ["Widow"],
        "has_young_children": False,
        "housing_condition": "Kutcha mud house (damaged roof)",
        "existing_documents": [
            "Aadhaar Card",
            "Husband's Death Certificate",
            "Ration Card (NFSA or State BPL Card)"
        ],
        "grievance_case": {
            "issue_type": "Pension Delayed",
            "scheme_name": "Indira Gandhi National Widow Pension Scheme (IGNWPS)",
            "portal": "Samagra / NSAP Jabalpur",
            "application_no": "MP-NSAP-2024-88912",
            "days_pending": 114,
            "grievance_detail": "Submitted widow pension application 4 months ago at Tehsil office with verified death certificate; no DBT received yet beyond statutory 30-day timeline."
        }
    },
    "rafiq_artisan": {
        "name": "Mohammad Rafiq",
        "age": 39,
        "gender": "Male",
        "state": "Uttar Pradesh",
        "district": "Saharanpur",
        "rural_urban": "Urban",
        "occupation": "Artisan",
        "artisan_trade": "Carpenter (Woodcarver)",
        "annual_income": 120000,
        "social_category": "OBC",
        "landholding_acres": 0.0,
        "special_conditions": ["Artisan Trade"],
        "has_young_children": True,
        "housing_condition": "Own small dwelling",
        "existing_documents": [
            "Aadhaar Card",
            "Mobile Number linked with Aadhaar",
            "Self-declaration of traditional artisan trade"
        ],
        "grievance_case": None
    }
}


class ProfileParserAgent:
    """Agent that handles progressive profile validation and intake."""

    def __init__(self):
        self.name = "Citizen Intake & Profile Validation Agent"

    def parse(self, raw_input: Any) -> Dict[str, Any]:
        """
        Parses structured input dictionary, predefined persona, or raw text into a canonical citizen profile.
        """
        if isinstance(raw_input, dict):
            persona_key = raw_input.get("persona_id") or raw_input.get("persona")
            if persona_key and persona_key in DEMO_PERSONAS:
                profile = dict(DEMO_PERSONAS[persona_key])
                # Overlay specific overrides
                for k, v in raw_input.items():
                    if k not in ["persona_id", "persona"] and v is not None and v != "":
                        profile[k] = v
                return self._normalize_profile_dict(profile)

            return self._normalize_profile_dict(raw_input)

        if isinstance(raw_input, str):
            for key, p in DEMO_PERSONAS.items():
                if key in raw_input.lower() or p["name"].lower() in raw_input.lower():
                    return dict(p)
            return self._extract_from_text(raw_input)

        return dict(DEMO_PERSONAS["rameshwar_farmer"])

    def _normalize_profile_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures all fields follow progressive disclosure and minimum necessary data standards."""
        occupation = str(data.get("occupation", "General")).strip()

        # Handle landholding progressively (only meaningful if agricultural)
        landholding = float(data.get("landholding_acres", 0.0))
        if "farmer" not in occupation.lower() and "agri" not in occupation.lower():
            if data.get("landholding_acres") is None:
                landholding = 0.0

        # Handle special conditions list
        specials = data.get("special_conditions", [])
        if isinstance(specials, str):
            specials = [specials] if specials else []

        # If widow is indicated in text or special conditions
        if str(data.get("marital_status", "")).lower() == "widow" and "Widow" not in specials:
            specials.append("Widow")

        profile = {
            "name": str(data.get("name", "Citizen of Bharat")).strip(),
            "age": int(data.get("age", 35)),
            "gender": str(data.get("gender", "All")).strip(),
            "state": str(data.get("state", "Uttar Pradesh")).strip(),
            "district": str(data.get("district", "Gorakhpur")).strip(),
            "rural_urban": str(data.get("rural_urban", "Rural")).strip(),
            "occupation": occupation,
            "annual_income": float(data.get("annual_income", 120000)),
            "social_category": str(data.get("social_category", data.get("caste", "General"))).strip(),
            "landholding_acres": landholding,
            "artisan_trade": data.get("artisan_trade", "None"),
            "special_conditions": specials,
            "has_young_children": bool(data.get("has_young_children", False) or (int(data.get("daughters_count", 0)) > 0)),
            "housing_condition": str(data.get("housing_condition", data.get("housing_status", "Normal"))).strip(),
            "existing_documents": data.get("existing_documents", ["Aadhaar Card", "Bank Account details (Aadhaar linked NPCI seeded)"]),
            "grievance_case": data.get("grievance_case", None)
        }
        return profile

    def _extract_from_text(self, text: str) -> Dict[str, Any]:
        """Deterministic extractor for conversational vernacular text."""
        profile = dict(DEMO_PERSONAS["rameshwar_farmer"])
        lower = text.lower()

        name_match = re.search(r"(?:name is|naam hai|naam)\s+([a-zA-Z\s]+?)(?:hai|\.|,|\n|$)", text, re.IGNORECASE)
        if name_match:
            profile["name"] = name_match.group(1).strip()

        age_match = re.search(r"(\d{2})\s*(?:years|saal|umar|yr|yo)", lower)
        if age_match:
            profile["age"] = int(age_match.group(1))

        if any(w in lower for w in ["female", "mahila", "aurat", "lady", "widow", "vidhwa"]):
            profile["gender"] = "Female"
            if "widow" in lower or "vidhwa" in lower:
                profile["special_conditions"] = ["Widow"]
        elif any(w in lower for w in ["male", "purush", "man"]):
            profile["gender"] = "Male"

        if any(w in lower for w in ["farmer", "kisan", "kheti"]):
            profile["occupation"] = "Farmer"
            profile["rural_urban"] = "Rural"
        elif any(w in lower for w in ["vendor", "thela", "hawker", "street"]):
            profile["occupation"] = "Street Vendor"
            profile["rural_urban"] = "Urban"
            profile["landholding_acres"] = 0.0
        elif any(w in lower for w in ["artisan", "carpenter", "mistri", "badhai", "karigar"]):
            profile["occupation"] = "Artisan"
            profile["special_conditions"] = ["Artisan Trade"]
        elif any(w in lower for w in ["labor", "majdoor", "shramik", "daily wage"]):
            profile["occupation"] = "Daily Laborer"

        for s in ["Uttar Pradesh", "Madhya Pradesh", "Delhi", "Bihar", "Maharashtra", "Rajasthan"]:
            if s.lower() in lower:
                profile["state"] = s
                break

        inc_match = re.search(r"(?:income|kamai|aamdani).*?(\d+)\s*(?:lakh|lac|k|thousand|hazar)?", lower)
        if inc_match:
            num = float(inc_match.group(1))
            if "lakh" in lower or "lac" in lower:
                profile["annual_income"] = num * 100000
            elif "k" in lower or "thousand" in lower or "hazar" in lower:
                profile["annual_income"] = num * 1000
            else:
                profile["annual_income"] = num if num > 1000 else num * 1000

        if any(w in lower for w in ["child", "beti", "bachha", "daughter", "school"]):
            profile["has_young_children"] = True

        if any(w in lower for w in ["delay", "pending", "atka", "pension nahi aayi", "complaint", "grievance"]):
            profile["grievance_case"] = {
                "issue_type": "Service Delay",
                "scheme_name": "Government Citizen Welfare Benefit",
                "portal": "CPGRAMS / State Portal",
                "application_no": "COMP-2026-9921",
                "days_pending": 60,
                "grievance_detail": text
            }

        return self._normalize_profile_dict(profile)
