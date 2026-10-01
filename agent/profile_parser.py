"""
Jan-Sahayak AI - Citizen Profile & Document Intelligence Agent
Extracts demographic, socio-economic, and documentation attributes from raw text, voice, or structured inputs.
"""

from typing import Dict, Any, List, Optional
import re

DEMO_PERSONAS = {
    "rameshwar_farmer": {
        "name": "Rameshwar Prasad Yadav",
        "age": 42,
        "gender": "Male",
        "state": "Uttar Pradesh",
        "district": "Gorakhpur",
        "urban_rural": "Rural",
        "occupation": "Farmer",
        "annual_income": 140000,
        "caste": "OBC",
        "landholding_acres": 1.2,
        "marital_status": "Married",
        "daughters_count": 2,
        "daughter_ages": [6, 9],
        "housing_status": "Semi-pucca",
        "existing_documents": [
            "Aadhaar Card",
            "Bank Passbook (SBI Gorakhpur)",
            "Land Khasra/Khatauni Copy",
            "Ration Card (PHH)"
        ],
        "specific_need": "Financial support for agriculture, daughter education, and health security",
        "grievance_case": None
    },
    "sunita_street_vendor": {
        "name": "Sunita Devi",
        "age": 34,
        "gender": "Female",
        "state": "Delhi",
        "district": "Central Delhi",
        "urban_rural": "Urban",
        "occupation": "Street Vendor",
        "annual_income": 95000,
        "caste": "SC",
        "landholding_acres": 0.0,
        "marital_status": "Married",
        "daughters_count": 1,
        "daughter_ages": [5],
        "housing_status": "Rented single room",
        "existing_documents": [
            "Aadhaar Card",
            "Voter ID Card",
            "Bank Account (PNB Chandni Chowk)",
            "Delhi Town Vending Committee (TVC) Receipt"
        ],
        "specific_need": "Working capital loan for fruit cart and free private school admission for daughter under RTE",
        "grievance_case": None
    },
    "kavita_widow": {
        "name": "Kavita Bai",
        "age": 62,
        "gender": "Female",
        "state": "Madhya Pradesh",
        "district": "Jabalpur",
        "urban_rural": "Rural",
        "occupation": "Unorganized Agricultural Laborer",
        "annual_income": 45000,
        "caste": "SC",
        "landholding_acres": 0.0,
        "marital_status": "Widow",
        "daughters_count": 0,
        "daughter_ages": [],
        "housing_status": "Kutcha mud house (damaged roof)",
        "existing_documents": [
            "Aadhaar Card",
            "Husband's Death Certificate",
            "BPL Ration Card",
            "Post Office Savings Passbook"
        ],
        "specific_need": "Widow monthly pension, pucca housing grant, and free medical insurance card",
        "grievance_case": {
            "type": "Pension Approval Delayed",
            "portal": "Samagra / NSAP Jabalpur",
            "application_no": "MP-NSAP-2024-88912",
            "days_pending": 114,
            "grievance_detail": "Submitted widow pension file 4 months ago at Tehsil office, no DBT received, officer asking for redundant affidavit."
        }
    },
    "kamala_widow": {
        "name": "Kavita Bai",
        "age": 62,
        "gender": "Female",
        "state": "Madhya Pradesh",
        "district": "Jabalpur",
        "urban_rural": "Rural",
        "occupation": "Unorganized Agricultural Laborer",
        "annual_income": 45000,
        "caste": "SC",
        "landholding_acres": 0.0,
        "marital_status": "Widow",
        "daughters_count": 0,
        "daughter_ages": [],
        "housing_status": "Kutcha mud house (damaged roof)",
        "existing_documents": [
            "Aadhaar Card",
            "Husband's Death Certificate",
            "BPL Ration Card",
            "Post Office Savings Passbook"
        ],
        "specific_need": "Widow monthly pension, pucca housing grant, and free medical insurance card",
        "grievance_case": {
            "type": "Pension Approval Delayed",
            "portal": "Samagra / NSAP Jabalpur",
            "application_no": "MP-NSAP-2024-88912",
            "days_pending": 114,
            "grievance_detail": "Submitted widow pension file 4 months ago at Tehsil office, no DBT received, officer asking for redundant affidavit."
        }
    },
    "rafiq_artisan": {
        "name": "Mohammad Rafiq",
        "age": 39,
        "gender": "Male",
        "state": "Uttar Pradesh",
        "district": "Saharanpur",
        "urban_rural": "Semi-Urban",
        "occupation": "Artisan",
        "trade_specialization": "Traditional Woodcarver (Carpenter/Woodwork)",
        "annual_income": 120000,
        "caste": "OBC",
        "landholding_acres": 0.0,
        "marital_status": "Married",
        "daughters_count": 1,
        "daughter_ages": [8],
        "housing_status": "Own small house",
        "existing_documents": [
            "Aadhaar Card",
            "Bank Passbook (Bank of Baroda)",
            "Artisan Guild Identity Slip"
        ],
        "specific_need": "Artisan tool kit grant, 5% low-interest business loan, and daughter education scheme",
        "grievance_case": None
    }
}


class ProfileParserAgent:
    """Agent responsible for digesting conversational input and synthesizing a canonical citizen profile."""

    def __init__(self):
        self.name = "Profile & Document Intelligence Agent"

    def parse(self, raw_input: Any) -> Dict[str, Any]:
        """
        Parses dictionary input, pre-selected persona, or raw text input into a standard citizen profile.
        """
        # 1. If raw_input references a preset persona
        if isinstance(raw_input, dict):
            persona_key = raw_input.get("persona_id") or raw_input.get("persona")
            if persona_key and persona_key in DEMO_PERSONAS:
                profile = dict(DEMO_PERSONAS[persona_key])
                # Overlay any specific overrides
                for k, v in raw_input.items():
                    if k not in ["persona_id", "persona"] and v is not None and v != "":
                        profile[k] = v
                return profile

            # If it's already a full profile dict, ensure defaults
            return self._normalize_profile_dict(raw_input)

        # 2. If raw string input
        if isinstance(raw_input, str):
            # Check if mentions persona by name
            for key, p in DEMO_PERSONAS.items():
                if key in raw_input.lower() or p["name"].lower() in raw_input.lower():
                    return dict(p)
            return self._extract_from_text(raw_input)

        # Default fallback persona
        return dict(DEMO_PERSONAS["rameshwar_farmer"])

    def _normalize_profile_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        profile = {
            "name": str(data.get("name", "Bharat Citizen")),
            "age": int(data.get("age", 35)),
            "gender": str(data.get("gender", "Male")),
            "state": str(data.get("state", "Uttar Pradesh")),
            "district": str(data.get("district", "Varanasi")),
            "urban_rural": str(data.get("urban_rural", "Rural")),
            "occupation": str(data.get("occupation", "Farmer")),
            "annual_income": float(data.get("annual_income", 120000)),
            "caste": str(data.get("caste", "OBC")),
            "landholding_acres": float(data.get("landholding_acres", 1.0)),
            "marital_status": str(data.get("marital_status", "Married")),
            "daughters_count": int(data.get("daughters_count", 0)),
            "daughter_ages": data.get("daughter_ages", []),
            "housing_status": str(data.get("housing_status", "Semi-pucca")),
            "existing_documents": data.get("existing_documents", ["Aadhaar Card", "Bank Account"]),
            "specific_need": str(data.get("specific_need", "Welfare benefits matching and official form generation")),
            "grievance_case": data.get("grievance_case", None)
        }
        return profile

    def _extract_from_text(self, text: str) -> Dict[str, Any]:
        """
        Deterministic NLP extractor for vernacular / English queries.
        """
        profile = dict(DEMO_PERSONAS["rameshwar_farmer"]) # baseline template
        lower = text.lower()

        # Extract name if present
        name_match = re.search(r"(?:name is|mera naam|naam)\s+([a-zA-Z\s]+?)(?:hai|\.|,|\n|$)", text, re.IGNORECASE)
        if name_match:
            profile["name"] = name_match.group(1).strip()

        # Extract Age
        age_match = re.search(r"(\d{2})\s*(?:years|saal|umar|yr|yo)", lower)
        if age_match:
            profile["age"] = int(age_match.group(1))

        # Extract Gender
        if any(w in lower for w in ["female", "aurat", "mahila", "lady", "widow", "stri"]):
            profile["gender"] = "Female"
        elif any(w in lower for w in ["male", "purush", "aadmi", "man"]):
            profile["gender"] = "Male"

        # Extract Marital Status
        if any(w in lower for w in ["widow", "vidhwa", "vidva", "husband passed"]):
            profile["marital_status"] = "Widow"
            profile["gender"] = "Female"

        # Occupation
        if any(w in lower for w in ["farmer", "kisan", "farming", "kheti"]):
            profile["occupation"] = "Farmer"
            profile["urban_rural"] = "Rural"
        elif any(w in lower for w in ["vendor", "thela", "hawker", "street", "feri", "dukaan"]):
            profile["occupation"] = "Street Vendor"
            profile["urban_rural"] = "Urban"
            profile["landholding_acres"] = 0.0
        elif any(w in lower for w in ["artisan", "carpenter", "mistri", "lohar", "badhai", "karigar"]):
            profile["occupation"] = "Artisan"
        elif any(w in lower for w in ["labor", "majdoor", "shramik", "daily wage"]):
            profile["occupation"] = "Daily Earner"

        # State
        for s in ["Uttar Pradesh", "UP", "Madhya Pradesh", "MP", "Delhi", "Bihar", "Maharashtra", "Rajasthan"]:
            if s.lower() in lower:
                profile["state"] = "Uttar Pradesh" if s.upper() == "UP" else ("Madhya Pradesh" if s.upper() == "MP" else s)
                break

        # Income
        inc_match = re.search(r"(?:income|kamai|aamdani|earn).*?(\d+)\s*(?:lakh|lac|k|thousand|hazar)?", lower)
        if inc_match:
            num = float(inc_match.group(1))
            if "lakh" in lower or "lac" in lower:
                profile["annual_income"] = num * 100000
            elif "k" in lower or "thousand" in lower or "hazar" in lower:
                profile["annual_income"] = num * 1000
            else:
                profile["annual_income"] = num if num > 1000 else num * 1000

        # Daughters
        if "daughter" in lower or "beti" in lower or "ladki" in lower:
            profile["daughters_count"] = 1
            profile["daughter_ages"] = [7]

        # Grievance detection
        if any(w in lower for w in ["grievance", "shikayat", "pending", "atka", "pension nahi aayi", "complaint", "delayed", "bribe"]):
            profile["grievance_case"] = {
                "type": "General Service Grievance",
                "portal": "CPGRAMS / State Portal",
                "application_no": "COMP-2026-9921",
                "days_pending": 60,
                "grievance_detail": text
            }

        return profile
