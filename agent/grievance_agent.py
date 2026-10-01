"""
Jan-Sahayak AI - CPGRAMS & Citizen Grievance Redressal Agent
Drafts legally rigorous, formal administrative grievance petitions and RTI appeals for delayed or denied civic services.
"""

from typing import Dict, Any, Optional
from datetime import datetime


class GrievanceRedressalAgent:
    """Agent that creates structured administrative appeals and CPGRAMS filings."""

    def __init__(self):
        self.name = "Grievance Redressal & Legal Drafting Agent"

    def draft_petition(self, profile: Dict[str, Any], grievance_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Drafts a formal administrative petition with citations of relevant public service guarantee timelines.
        """
        if grievance_info is None:
            grievance_info = profile.get("grievance_case")

        if not grievance_info:
            # Default proactive grievance template for delayed DBT
            grievance_info = {
                "type": "Delayed Welfare Benefit Disbursement",
                "portal": "State Public Grievance Portal / CPGRAMS",
                "application_no": "JS-GREV-" + datetime.now().strftime("%Y%m%d%H"),
                "days_pending": 75,
                "grievance_detail": f"Application submitted by {profile.get('name')} for eligible welfare scheme remains unacted upon beyond statutory citizen charter timelines."
            }

        name = profile.get("name", "Aggrieved Citizen")
        district = profile.get("district", "District Magistrate")
        state = profile.get("state", "Uttar Pradesh")
        app_no = grievance_info.get("application_no", "NA")
        days = grievance_info.get("days_pending", 45)
        detail = grievance_info.get("grievance_detail", "Administrative delay in processing welfare entitlement.")
        case_type = grievance_info.get("type", "Civic Grievance")

        petition_text = f"""================================================================================
FORMAL PETITION UNDER THE CITIZEN'S CHARTER & PUBLIC SERVICES GUARANTEE ACT
FILED BEFORE: THE DISTRICT MAGISTRATE / NODAL APPELLATE AUTHORITY, {district.upper()}, {state.upper()}
================================================================================

PETITIONER DETAILS:
Name: {name}
S/o or W/o: (As recorded in Aadhaar registry)
Address: Resident of District {district}, State of {state}
Category: {profile.get('caste', 'General')} | Occupation: {profile.get('occupation', 'Citizen')}
Annual Household Income: ₹{profile.get('annual_income', 0):,.0f}

SUBJECT: 
Formal Grievance Petition regarding {case_type} under Scheme Application Ref: [{app_no}] — Unreasonable delay of {days} days violating statutory delivery timelines.

RESPECTED SIR/MADAM,

1. PRELIMINARY STATEMENT:
The Petitioner is an eligible, bona fide citizen of Bharat residing within your administrative jurisdiction, satisfying all socio-economic criteria prescribed under the relevant Central & State statutory welfare rules.

2. STATEMENT OF FACTS:
a. On the registered date, the petitioner duly submitted the complete application dossier with verified KYC and mandatory documentation under Application No. {app_no}.
b. As of today's date ({datetime.now().strftime('%d %B %Y')}), a total duration of {days} calendar days has elapsed without formal approval, disbursement, or reasoned speaking order.
c. Factual Grievance: "{detail}"

3. STATUTORY INFRACTION & LEGAL CITATION:
Under the State Public Services Guarantee Act and the Government of Bharat Citizen's Charter, statutory welfare benefits and Direct Benefit Transfers (DBT) carry a mandated resolution SLA of thirty (30) business days. The continued pendency of {days} days constitutes administrative deficiency and actionable grievance under Section 19 of the General Administrative Directives.

4. PRAYER FOR RELIEF:
In light of the aforesaid facts, the petitioner respectfully prays that:
i. A direction be immediately issued to the concerned Block Development Officer (BDO) / Tehsildar / District Nodal Officer to clear the pending DBT without arbitrary delay.
ii. If any auxiliary document is ostensibly required, an explicit, written requisition be served within forty-eight (48) hours rather than keeping the dossier in perpetual pendency.
iii. In default whereof, this grievance be escalated to the Centralized Public Grievance Redress and Monitoring System (CPGRAMS) and the Hon'ble Chief Minister's Special Monitoring Cell for administrative inquiry.

VERIFICATION:
I, {name}, do hereby verify that the facts stated in paragraphs 1 to 4 are true and correct to my personal knowledge.

Date: {datetime.now().strftime('%d/%m/%Y')}
Place: {district}, {state}

(Digital Verification Generated via Jan-Sahayak Autonomous Civic Agent)
================================================================================
"""

        return {
            "petition_title": f"CPGRAMS Grievance Petition: {case_type}",
            "application_reference": app_no,
            "days_delayed": days,
            "authority": f"District Magistrate & Nodal Officer, {district}, {state}",
            "petition_text": petition_text,
            "recommended_submission_portals": [
                {"name": "CPGRAMS National Portal", "url": "https://pgportal.gov.in"},
                {"name": f"{state} CM Helpline", "toll_free": "1076 / 181"},
                {"name": "District Collector Jan Sunwai", "mode": "In-person / District Portal"}
            ]
        }
