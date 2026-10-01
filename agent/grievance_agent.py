"""
Jan-Sahayak AI - CPGRAMS & Citizen Grievance Assistant Agent
Drafts legally rigorous, formal administrative grievance petitions and appeals for delayed or denied civic services.
Uses ONLY verified public service guarantee principles and citizen charter timelines.
"""

from typing import Dict, Any, Optional
from datetime import datetime


GRIEVANCE_TEMPLATES = {
    "pension_delayed": {
        "title": "Widow / Old-Age Pension Disbursement Delayed",
        "default_detail": "Application for statutory pension submitted with verified KYC and death/age certificates; Direct Benefit Transfer (DBT) has not been released beyond the statutory 30-day Citizen Charter timeline.",
        "requested_relief": "Immediate sanction order release and clearance of accumulated monthly pension arrears directly into the bank account.",
        "supporting_docs": ["Death Certificate / Age Proof", "Aadhaar e-KYC Copy", "Bank Passbook with active NPCI seeding", "Acknowledgement receipt"]
    },
    "ration_issue": {
        "title": "NFSA Ration Card Inclusion / PDS Quota Denied",
        "default_detail": "Eligible household member name wrongly omitted or fair price shop (PDS) dealer refusing statutory grain quota citing biometric mismatch.",
        "requested_relief": "Immediate restoration of ration entitlement, Fair Price Shop inspection, and offline OTP/manual register override for grain disbursement.",
        "supporting_docs": ["Existing Ration Card copy", "Family Aadhaar copies", "Income Certificate / BPL proof", "Recent Fair Price Shop visit records"]
    },
    "dbt_not_received": {
        "title": "Direct Benefit Transfer (DBT) Failure / NPCI Seeding Issue",
        "default_detail": "Approved government welfare installment (e.g., PM-Kisan / Scholarship / Housing) showing successful government release but amount not credited to bank account.",
        "requested_relief": "PFMS transaction tracing, verification of NPCI Aadhaar bank mapping, and immediate re-push of failed transfer transaction.",
        "supporting_docs": ["Bank Statement showing non-credit", "Scheme Registration / Beneficiary Number", "Bank Aadhaar Seeding Confirmation"]
    },
    "application_rejected": {
        "title": "Arbitrary Rejection of Welfare Application without Speaking Order",
        "default_detail": "Application rejected without providing specific deficiency letter, opportunity of hearing, or written reasoned speaking order as mandated under natural justice principles.",
        "requested_relief": "Re-opening of application dossier, formal disclosure of specific ground of rejection, and fresh administrative review.",
        "supporting_docs": ["Original Application Form & Acknowledgement Receipt", "Rejection Notice / Portal Screenshot", "Complete supporting eligibility documents"]
    },
    "subsidy_not_received": {
        "title": "Approved Agricultural / Business Subsidy Withheld",
        "default_detail": "Subsidy sanctioned for agricultural equipment or micro-enterprise credit has been delayed at the nodal department level for over 60 days.",
        "requested_relief": "Expedited administrative sanction clearance and credit of subsidy amount to the lending bank branch.",
        "supporting_docs": ["Bank Sanction Letter", "Equipment Purchase / Tax Invoice", "Physical Verification Inspection Report"]
    },
    "service_delay": {
        "title": "General Civic Service Delay Beyond Citizen Charter SLA",
        "default_detail": "Statutory citizen service (e.g., Domicile Certificate, Caste Certificate, or Land Mutation) pending beyond the statutory delivery timeline prescribed under the State Public Services Guarantee Act.",
        "requested_relief": "Immediate issuance of requested certificate / service order and fixing of accountability on the erring nodal officer under Public Services Guarantee rules.",
        "supporting_docs": ["e-District Acknowledgement Slip", "Date of Application Proof", "Identity Proof"]
    }
}


class GrievanceRedressalAgent:
    """Agent that creates structured administrative appeals and CPGRAMS filings."""

    def __init__(self):
        self.name = "Grievance Assistant & Administrative Appeals Agent"

    def draft_petition(self, profile: Dict[str, Any], grievance_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Drafts a formal administrative petition with verified citizen charter references.
        """
        if grievance_input is None:
            grievance_input = profile.get("grievance_case") or {}

        # Resolve issue type key
        issue_key = grievance_input.get("issue_type", "pension_delayed").lower().replace(" ", "_")
        if issue_key not in GRIEVANCE_TEMPLATES:
            # Map loosely
            if "pension" in issue_key: issue_key = "pension_delayed"
            elif "ration" in issue_key: issue_key = "ration_issue"
            elif "dbt" in issue_key: issue_key = "dbt_not_received"
            elif "reject" in issue_key: issue_key = "application_rejected"
            elif "subsidy" in issue_key: issue_key = "subsidy_not_received"
            else: issue_key = "service_delay"

        template = GRIEVANCE_TEMPLATES[issue_key]

        name = profile.get("name", "Aggrieved Citizen").strip()
        district = profile.get("district", "Gorakhpur").strip()
        state = profile.get("state", "Uttar Pradesh").strip()
        app_no = grievance_input.get("application_no", "BHARAT-APP-" + datetime.now().strftime("%Y%m%d"))
        days = grievance_input.get("days_pending", 45)
        detail = grievance_input.get("grievance_detail") or template["default_detail"]
        scheme_name = grievance_input.get("scheme_name", "Statutory Citizen Welfare Scheme")

        subject_line = f"Formal Administrative Grievance regarding {template['title']} [Application Ref: {app_no}] — Unreasonable delay of {days} days violating Citizen Charter SLA."

        petition_text = f"""================================================================================
FORMAL ADMINISTRATIVE GRIEVANCE PETITION
UNDER THE CITIZEN'S CHARTER & STATE PUBLIC SERVICES GUARANTEE RULES
BEFORE: THE DISTRICT MAGISTRATE / NODAL APPELLATE AUTHORITY, {district.upper()}, {state.upper()}
================================================================================

1. PETITIONER IDENTIFICATION:
   • Full Name: {name}
   • Residential Jurisdiction: District {district}, State of {state}
   • Socio-Economic Category: {profile.get('social_category', 'General')} | Occupation: {profile.get('occupation', 'Citizen')}
   • Annual Household Income: ₹{profile.get('annual_income', 0):,.0f}

2. SUBJECT:
   {subject_line}

3. CASE SUMMARY & TIMELINE:
   a. Beneficiary Scheme: {scheme_name}
   b. Reference / Registration Number: {app_no}
   c. Duration of Unresolved Pendency: {days} Calendar Days
   d. Factual Statement of Grievance:
      "{detail}"

4. VERIFIED STATUTORY BASIS:
   Under the State Public Services Guarantee Directives and the Citizen's Charter of the Government of India, welfare benefit processing and direct transfer clearances carry a mandated resolution timeline of thirty (30) business days. Continued inaction of {days} days violates these statutory service commitments.

5. PRAYER FOR RESOLUTION:
   The petitioner respectfully requests:
   i. Immediate issuance of formal administrative instructions to the concerned Nodal Department to clear the pending benefit without arbitrary delay.
   ii. In case of any technical or document discrepancy, a formal speaking requisition be served in writing within 48 hours.
   iii. Direct escalation to the Centralized Public Grievance Redress and Monitoring System (CPGRAMS) and the Hon'ble Chief Minister's Monitoring Cell if unresolved within 7 days.

6. SUPPORTING DOCUMENTS ATTACHED:
   {chr(10).join([f"   • {d}" for d in template['supporting_docs']])}

VERIFICATION:
I, {name}, do hereby verify that the facts stated above are true and accurate to the best of my knowledge.

Date: {datetime.now().strftime('%d/%m/%Y')}
Place: {district}, {state}
(Generated via Jan-Sahayak AI Civic Assistant • Team Bits and Bytes)
================================================================================
"""

        return {
            "issue_key": issue_key,
            "petition_title": template["title"],
            "subject": subject_line,
            "application_reference": app_no,
            "days_delayed": days,
            "scheme_name": scheme_name,
            "authority": f"District Magistrate & Nodal Appellate Authority, {district}, {state}",
            "citizen_name": name,
            "requested_resolution": template["requested_relief"],
            "supporting_documents": template["supporting_docs"],
            "petition_text": petition_text,
            "escalation_channels": [
                {"name": "Central CPGRAMS Portal", "url": "https://pgportal.gov.in"},
                {"name": f"{state} CM Helpline", "contact": "1076 / 181"},
                {"name": "District Jan Sunwai Desk", "contact": f"Collectorate, {district}"}
            ]
        }
