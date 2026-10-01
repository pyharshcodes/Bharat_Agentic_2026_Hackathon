"""
Jan-Sahayak AI - Document Gap & Compliance Verification Agent
Audits citizen's in-hand documentation against requirements of qualified schemes,
generating readiness scores and autonomous remediation steps.
"""

from typing import Dict, Any, List, Set


DOC_ISSUING_GUIDANCE = {
    "Land Ownership Records (Khasra/Khatauni/ROR)": {
        "issuing_authority": "Revenue Department / Tehsil Office",
        "online_portal": "State Bhulekh Portal (e.g., upbhulekh.gov.in)",
        "service_kiosk": "Common Service Centre (CSC) / Jan Seva Kendra",
        "typical_turnaround": "Instant online digital copy (₹15 fee)",
        "action_guide": "Download digitally signed RoR (Khatauni) using your Khasra / Gata number from UP Bhulekh portal."
    },
    "UP Domicile Certificate (Niwas Praman Patra)": {
        "issuing_authority": "Sub-Divisional Magistrate (SDM) / Tehsildar",
        "online_portal": "eDistrict UP Portal (edistrict.up.gov.in)",
        "service_kiosk": "CSC Jan Seva Kendra",
        "typical_turnaround": "7-10 working days",
        "action_guide": "Apply online with electricity bill / ration card and self-declaration affidavit."
    },
    "MP Domicile Certificate": {
        "issuing_authority": "Lok Seva Kendra (MP e-District)",
        "online_portal": "mpedistrict.gov.in",
        "service_kiosk": "Lok Seva Kendra",
        "typical_turnaround": "3-5 days (Public Services Guarantee Act)",
        "action_guide": "Visit nearest Lok Seva Kendra with Samagra ID and ration card."
    },
    "Urban Local Body (ULB) Vending Certificate or Town Vending Committee (TVC) ID": {
        "issuing_authority": "Municipal Corporation / Nagar Nigam (DUDA)",
        "online_portal": "pmsvanidhi.mohua.gov.in / Municipal Portal",
        "service_kiosk": "Zone Office DUDA Cell",
        "typical_turnaround": "15 days",
        "action_guide": "Request a Letter of Recommendation (LoR) from your local Town Vending Committee (TVC) or Municipal Ward Officer."
    },
    "Parent Income Certificate (< ₹3L)": {
        "issuing_authority": "Tehsildar / Revenue Department",
        "online_portal": "State eDistrict Portal",
        "service_kiosk": "CSC Kendra",
        "typical_turnaround": "5-7 days",
        "action_guide": "Submit self-declaration of agricultural/informal income at CSC center."
    },
    "BPL Card or Valid Income Certificate (< ₹1,00,000/yr)": {
        "issuing_authority": "Food & Civil Supplies / Tehsil",
        "online_portal": "State Food Portal / eDistrict",
        "service_kiosk": "Tehsil Office / CSC",
        "typical_turnaround": "10-15 days",
        "action_guide": "Obtain EWS/Income certificate from local Patwari/Lekhpal verification."
    },
    "Birth Certificate of Girl Child": {
        "issuing_authority": "Registrar of Births & Deaths / Nagar Nigam / Gram Panchayat",
        "online_portal": "crsorgi.gov.in",
        "service_kiosk": "PHC Hospital / Gram Panchayat Sachiv",
        "typical_turnaround": "3 days",
        "action_guide": "Collect municipal digital birth record or Gram Panchayat institutional delivery slip."
    }
}


class GapVerifierAgent:
    """Agent that performs compliance verification and missing document gap analysis."""

    def __init__(self):
        self.name = "Document Gap & Verification Agent"

    def audit(self, profile: Dict[str, Any], evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cross-examines in-hand documents against all qualified schemes.
        """
        existing_docs = profile.get("existing_documents", [])
        existing_lower = [d.lower() for d in existing_docs]

        scheme_audits = []
        all_required_docs = set()
        all_missing_docs = set()

        for scheme in evaluation.get("qualified_schemes", []):
            mandatories = scheme.get("mandatory_documents", [])
            verified_for_scheme = []
            missing_for_scheme = []

            for doc in mandatories:
                all_required_docs.add(doc)
                doc_lower = doc.lower()
                
                # Fuzzy match document keyword
                is_held = False
                for ex in existing_lower:
                    if any(term in doc_lower for term in ["aadhaar", "bank", "ration", "khasra", "death", "voter", "samagra"]):
                        if any(term in ex for term in ["aadhaar", "bank", "ration", "khasra", "death", "voter", "samagra"]):
                            if ("aadhaar" in doc_lower and "aadhaar" in ex) or \
                               ("bank" in doc_lower and "bank" in ex) or \
                               ("ration" in doc_lower and "ration" in ex) or \
                               ("khasra" in doc_lower and "khasra" in ex) or \
                               ("death" in doc_lower and "death" in ex) or \
                               ("voter" in doc_lower and "voter" in ex) or \
                               ("samagra" in doc_lower and "samagra" in ex):
                                is_held = True
                                break

                if is_held:
                    verified_for_scheme.append(doc)
                else:
                    missing_for_scheme.append(doc)
                    all_missing_docs.add(doc)

            readiness_pct = int((len(verified_for_scheme) / len(mandatories) * 100)) if mandatories else 100

            scheme_audits.append({
                "scheme_id": scheme["scheme_id"],
                "scheme_name": scheme["scheme_name"],
                "readiness_percentage": readiness_pct,
                "verified_documents": verified_for_scheme,
                "missing_documents": missing_for_scheme,
                "application_ready": len(missing_for_scheme) == 0
            })

        # Calculate overall citizen readiness score
        total_unique_mandatories = len(all_required_docs)
        total_unique_missing = len(all_missing_docs)
        overall_score = 100 if total_unique_mandatories == 0 else int(
            ((total_unique_mandatories - total_unique_missing) / total_unique_mandatories) * 100
        )
        overall_score = max(0, min(100, overall_score))

        # Remediation roadmap
        remediation_actions = []
        for doc in sorted(all_missing_docs):
            guide = DOC_ISSUING_GUIDANCE.get(doc, {
                "issuing_authority": "Local District Administration / CSC",
                "online_portal": "serviceonline.gov.in",
                "service_kiosk": "Jan Seva Kendra / CSC",
                "typical_turnaround": "7 working days",
                "action_guide": f"Apply at nearest CSC Kendra or District portal for {doc}."
            })
            remediation_actions.append({
                "document_name": doc,
                "urgency": "HIGH",
                "guidance": guide
            })

        return {
            "overall_document_readiness_score": overall_score,
            "total_documents_needed": total_unique_mandatories,
            "missing_documents_count": total_unique_missing,
            "scheme_audits": scheme_audits,
            "remediation_actions": remediation_actions,
            "can_apply_instantly": any(s["application_ready"] for s in scheme_audits)
        }
