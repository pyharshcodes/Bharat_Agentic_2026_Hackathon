"""
Jan-Sahayak AI - Master Multi-Agent Orchestrator
Coordinates Profile Parsing, Schemes Reasoning, Gap Verification, PDF Application Packaging, and Grievance Drafting.
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from agent.profile_parser import ProfileParserAgent, DEMO_PERSONAS
from agent.scheme_engine import SchemeReasoningEngine
from agent.gap_verifier import GapVerifierAgent
from agent.form_packager import FormPackagerAgent
from agent.grievance_agent import GrievanceRedressalAgent


class JanSahayakOrchestrator:
    """The master cognitive agent that sequences sub-agents and produces full telemetry traces."""

    def __init__(self, output_dir: Optional[str] = None):
        self.profile_parser = ProfileParserAgent()
        self.scheme_engine = SchemeReasoningEngine()
        self.gap_verifier = GapVerifierAgent()
        self.form_packager = FormPackagerAgent(output_dir)
        self.grievance_agent = GrievanceRedressalAgent()

    def run_agentic_workflow(self, user_input: Any, generate_pdf: bool = True) -> Dict[str, Any]:
        """
        Executes the end-to-end multi-agent workflow with full telemetry tracking.
        """
        telemetry = []
        overall_start = time.time()

        # STEP 1: Citizen Profile Ingestion & Document Intelligence
        t0 = time.time()
        telemetry.append({
            "step": 1,
            "agent": "Profile & Document Intelligence Agent",
            "action": "Ingest and structure demographic and socio-economic attributes",
            "status": "IN_PROGRESS",
            "timestamp": datetime.now().isoformat()
        })
        profile = self.profile_parser.parse(user_input)
        telemetry[-1].update({
            "status": "COMPLETED",
            "duration_ms": int((time.time() - t0) * 1000),
            "output_summary": f"Citizen profile extracted: {profile['name']}, {profile['age']}y ({profile['gender']}), {profile['occupation']} in {profile['state']} ({profile['urban_rural']}), Income: ₹{profile['annual_income']:,.0f}"
        })

        # STEP 2: Bharat Schemes Reasoning Engine
        t0 = time.time()
        telemetry.append({
            "step": 2,
            "agent": "Bharat Schemes Reasoning Engine",
            "action": "Audit 50+ Central & State scheme eligibility criteria against citizen profile",
            "status": "IN_PROGRESS",
            "timestamp": datetime.now().isoformat()
        })
        evaluation = self.scheme_engine.evaluate_profile(profile)
        telemetry[-1].update({
            "status": "COMPLETED",
            "duration_ms": int((time.time() - t0) * 1000),
            "output_summary": f"Evaluated {evaluation['total_schemes_evaluated']} schemes. Found {evaluation['qualified_count']} qualified schemes with ~₹{evaluation['total_estimated_annual_benefit_inr']:,.0f} direct benefits."
        })

        # STEP 3: Compliance & Document Gap Verifier
        t0 = time.time()
        telemetry.append({
            "step": 3,
            "agent": "Document Gap & Compliance Verification Agent",
            "action": "Audit held documents vs mandatory scheme documents and generate remediation actions",
            "status": "IN_PROGRESS",
            "timestamp": datetime.now().isoformat()
        })
        gap_audit = self.gap_verifier.audit(profile, evaluation)
        telemetry[-1].update({
            "status": "COMPLETED",
            "duration_ms": int((time.time() - t0) * 1000),
            "output_summary": f"Document readiness: {gap_audit['overall_document_readiness_score']}%. Missing: {gap_audit['missing_documents_count']} doc(s). Formulated {len(gap_audit['remediation_actions'])} remediation guides."
        })

        # STEP 4: Autonomous Form Packaging & PDF Generation
        pdf_path = None
        pdf_filename = None
        if generate_pdf:
            t0 = time.time()
            telemetry.append({
                "step": 4,
                "agent": "Autonomous Form & Application Packager Agent",
                "action": "Mint official Government Citizen Welfare Application Dossier (PDF)",
                "status": "IN_PROGRESS",
                "timestamp": datetime.now().isoformat()
            })
            try:
                pdf_path = self.form_packager.generate_dossier_pdf(profile, evaluation, gap_audit)
                pdf_filename = Path(pdf_path).name
                telemetry[-1].update({
                    "status": "COMPLETED",
                    "duration_ms": int((time.time() - t0) * 1000),
                    "output_summary": f"Successfully minted Application PDF dossier: {pdf_filename}"
                })
            except Exception as e:
                telemetry[-1].update({
                    "status": "ERROR",
                    "duration_ms": int((time.time() - t0) * 1000),
                    "output_summary": f"PDF Generation note: {str(e)}"
                })

        # STEP 5: Grievance Petition Drafting (if applicable or requested)
        grievance_data = None
        if profile.get("grievance_case") or (isinstance(user_input, dict) and user_input.get("draft_grievance")):
            t0 = time.time()
            telemetry.append({
                "step": 5,
                "agent": "Grievance Redressal & Legal Drafting Agent",
                "action": "Draft statutory CPGRAMS administrative appeal citing Citizen Charter SLAs",
                "status": "IN_PROGRESS",
                "timestamp": datetime.now().isoformat()
            })
            grievance_data = self.grievance_agent.draft_petition(profile)
            telemetry[-1].update({
                "status": "COMPLETED",
                "duration_ms": int((time.time() - t0) * 1000),
                "output_summary": f"Drafted legal petition: '{grievance_data['petition_title']}' for {grievance_data['authority']}"
            })

        # STEP 6: Bilingual Vernacular Synthesis (Hindi + English)
        bilingual_response = self._synthesize_bilingual_response(profile, evaluation, gap_audit, grievance_data, pdf_filename)

        total_runtime_ms = int((time.time() - overall_start) * 1000)

        return {
            "status": "SUCCESS",
            "citizen_name": profile["name"],
            "total_runtime_ms": total_runtime_ms,
            "telemetry": telemetry,
            "profile": profile,
            "evaluation": evaluation,
            "gap_audit": gap_audit,
            "pdf_filename": pdf_filename,
            "pdf_path": pdf_path,
            "grievance": grievance_data,
            "bilingual_response": bilingual_response
        }

    def _synthesize_bilingual_response(
        self, profile: Dict[str, Any], evaluation: Dict[str, Any], gap_audit: Dict[str, Any],
        grievance_data: Optional[Dict[str, Any]], pdf_filename: Optional[str]
    ) -> Dict[str, str]:
        """
        Creates clear, dignified, and actionable text in Hindi and English.
        """
        top_schemes = [f"• {s['scheme_name']} ({s.get('hindi_name', '')}) — {s['benefit_summary'].get('financial', 'Direct Benefits')}" 
                       for s in evaluation.get("qualified_schemes", [])[:4]]
        top_schemes_str = "\n".join(top_schemes)

        hindi_text = f"""नमस्ते {profile['name']} जी! 

जन-सहायक AI एजेंट ने आपकी जानकारी का विश्लेषण कर लिया है। आपके लिए सरकार की निम्नलिखित प्रमुख योजनाएं पूरी तरह उपयुक्त (Eligible) पाई गई हैं:

{top_schemes_str}

💰 अनुमानित प्रत्यक्ष वार्षिक लाभ: लगभग ₹{evaluation.get('total_estimated_annual_benefit_inr', 0):,.0f} प्रति वर्ष

📄 दस्तावेज़ तैयारी स्कोर: {gap_audit.get('overall_document_readiness_score', 0)}%
{'✓ आपके सभी मुख्य दस्तावेज तैयार हैं!' if gap_audit.get('missing_documents_count', 0) == 0 else f'⚠️ आपको {gap_audit.get("missing_documents_count")} अतिरिक्त प्रमाण पत्र (जैसे {", ".join([r["document_name"] for r in gap_audit.get("remediation_actions", [])[:2]])}) बनवाने की सलाह दी जाती है।'}

📌 आपका आधिकारिक आवेदन पैकेज (Application PDF) तैयार कर दिया गया है जिसे आप नीचे दिए गए बटन से सीधे डाउनलोड कर सकते हैं।"""

        english_text = f"""Greetings {profile['name']}!

Jan-Sahayak AI Agent has audited your socio-economic profile across Central and State government registries. You qualify for the following key welfare programs:

{top_schemes_str}

💰 Estimated Direct Annual Financial Benefit: ~₹{evaluation.get('total_estimated_annual_benefit_inr', 0):,.0f} / year

📄 Document Readiness Score: {gap_audit.get('overall_document_readiness_score', 0)}%
{'✓ All mandatory documents are in order!' if gap_audit.get('missing_documents_count', 0) == 0 else f'⚠️ Notice: {gap_audit.get("missing_documents_count")} certificate(s) required to unlock all benefits.'}

📌 Your official Unified Citizen Welfare Application Dossier ({pdf_filename or 'PDF'}) has been minted and is ready for download."""

        return {
            "hindi": hindi_text,
            "english": english_text
        }
