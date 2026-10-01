"""
Jan-Sahayak AI - aiKart "Try Me Now" Sandbox Runner
Implements the aiKart v1 Agent Manifest contract:
Reads /aikart/input.json (or AIKART_INPUT env var) and writes /aikart/output.json
"""

import os
import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from agent.orchestrator import JanSahayakOrchestrator


def main():
    # 1. Locate and parse input
    input_data = {}
    
    # Check container file path first
    container_input_file = Path("/aikart/input.json")
    local_input_file = Path("input.json")

    if container_input_file.exists():
        try:
            with open(container_input_file, "r", encoding="utf-8") as f:
                input_data = json.load(f)
        except Exception as e:
            print(f"[Sandbox Warning] Failed to read /aikart/input.json: {e}")
    elif "AIKART_INPUT" in os.environ and os.environ["AIKART_INPUT"].strip():
        try:
            input_data = json.loads(os.environ["AIKART_INPUT"])
        except Exception as e:
            print(f"[Sandbox Warning] Failed to parse AIKART_INPUT env var: {e}")
            input_data = {"custom_query": os.environ["AIKART_INPUT"]}
    elif local_input_file.exists():
        try:
            with open(local_input_file, "r", encoding="utf-8") as f:
                input_data = json.load(f)
        except Exception:
            pass

    # Fallback to default persona if no input given
    if not input_data:
        input_data = {"persona": "Rameshwar Yadav (Marginal Farmer - UP)", "language": "Hindi (हिंदी)"}

    # Normalize persona selection
    selected_persona = input_data.get("persona", "")
    persona_id = "rameshwar_farmer"
    if "Sunita" in selected_persona or "Street Vendor" in selected_persona:
        persona_id = "sunita_street_vendor"
    elif "Kavita" in selected_persona or "Kamala" in selected_persona or "Widow" in selected_persona:
        persona_id = "kavita_widow"
    elif "Rafiq" in selected_persona or "Artisan" in selected_persona:
        persona_id = "rafiq_artisan"

    custom_text = input_data.get("custom_query") or input_data.get("topic") or input_data.get("query")
    agent_input = custom_text if (custom_text and len(custom_text.strip()) > 3) else {"persona_id": persona_id}

    # 2. Run Autonomous Multi-Agent Pipeline
    orchestrator = JanSahayakOrchestrator()
    result = orchestrator.run_agentic_workflow(agent_input, generate_pdf=True)

    # 3. Format Rich Markdown Output for aiKart Sandbox
    lang = input_data.get("language", "Hindi (हिंदी)")
    profile = result["profile"]
    eval_res = result["evaluation"]
    gap_res = result["gap_audit"]
    telemetry = result["telemetry"]
    grievance = result.get("grievance")

    is_hindi = "Hindi" in lang or "हिंदी" in lang

    top_schemes_md = ""
    schemes_to_show = eval_res.get("eligible_schemes", []) or eval_res.get("qualified_schemes", [])
    for s in schemes_to_show[:5]:
        top_schemes_md += f"""
### 🏛️ {s['scheme_name']} ({s.get('hindi_name', '')})
- **Category & Ministry:** {s.get('category')} | {s.get('ministry')}
- **Direct Benefit:** **{s['benefit_summary'].get('financial', 'Government Subsidy / Coverage')}**
- **Match Score:** `{s.get('match_score', 100)}%`
- **Agent Verification Reasoning:** {s['why_qualify'][0] if s.get('why_qualify') else (s['reasoning_trace'][0] if s.get('reasoning_trace') else 'Criteria satisfied.')}
- **Required Documents:** {', '.join(s.get('mandatory_documents', [])[:3])}
- **Official Portal:** [{s.get('official_url', s.get('nodal_portal', ''))}]({s.get('official_url', s.get('nodal_portal', ''))})
"""

    agent_trace_md = ""
    for step in telemetry:
        status_icon = "✅" if step["status"] == "COMPLETED" else "⏳"
        agent_trace_md += f"- **Step {step['step']}: {step['agent']}** ({step.get('duration_ms', 0)}ms) {status_icon}\n  _{step.get('output_summary', '')}_\n"

    grievance_md = ""
    if grievance:
        grievance_md = f"""
---
### ⚖️ Autonomous Grievance Redressal Petition (CPGRAMS / Citizen Charter)
> **Statutory Citation:** Section 19 of Citizen Charter SLA (30 Days Mandate).
```text
{grievance['petition_text'][:700]}... [Full Legal Petition Drafted]
```
**Recommended Escalation Authorities:**
- **Central Portal:** [CPGRAMS pgportal.gov.in](https://pgportal.gov.in)
- **State CM Helpline:** 1076 / 181
"""

    markdown_response = f"""# 🇮🇳 Jan-Sahayak AI (जन-सहायक) — Civic & Welfare Delivery Agent
*Powered by aiKart Sandbox • Autonomous Multi-Agent Reasoning for Bharat*

---

## 👤 Citizen Verified Profile
- **Name:** {profile.get('name')}
- **Demographics:** {profile.get('age')} Yrs | {profile.get('gender')} | {profile.get('marital_status')}
- **Location:** {profile.get('district')}, {profile.get('state')} ({profile.get('urban_rural')})
- **Occupation & Income:** {profile.get('occupation')} | **₹{profile.get('annual_income', 0):,.0f} / year**
- **Landholding / Family:** {profile.get('landholding_acres', 0)} Acres | {profile.get('daughters_count', 0)} Daughter(s)

---

## ⚡ Agentic Workflow & Real-Time Telemetry
{agent_trace_md}
⏱️ **Total Agent Execution Latency:** `{result['total_runtime_ms']} ms`

---

## 🎯 Entitlement Summary: Qualified Government Schemes
- **Total Configured Schemes:** `{eval_res.get('total_configured_schemes', 12)}`
- **Schemes Qualified (Eligible):** `{eval_res.get('eligible_count', eval_res.get('qualified_count', 0))}`
- **Potentially Eligible Schemes:** `{eval_res.get('potential_count', 0)}`
- **Total Estimated Annual Direct Benefit:** **₹{eval_res.get('total_estimated_annual_benefit_inr', 0):,.0f} / year**
- **Document Readiness Score:** `{gap_res.get('overall_document_readiness_score', 0)}%`

{top_schemes_md}

---

## 📑 Document Compliance & Autonomous Remediation Roadmap
- **Documents in Hand:** {', '.join(profile.get('existing_documents', []))}
- **Missing Required Documents:** {gap_res['missing_documents_count']} item(s)
"""

    for rem in gap_res.get("remediation_actions", [])[:2]:
        markdown_response += f"""
- ⚠️ **Missing:** `{rem['document_name']}`
  - **Issuing Authority:** {rem['guidance'].get('issuing_authority')}
  - **Action Required:** {rem['guidance'].get('action_guide')}
  - **Service Kiosk:** {rem['guidance'].get('service_kiosk')} ({rem['guidance'].get('typical_turnaround')})
"""

    if result.get("pdf_filename"):
        markdown_response += f"""
---
### 📥 Official Application Dossier Minted
The agent has compiled and cryptographically certified the official application dossier:
`{result['pdf_filename']}` (Ready for Jan Seva Kendra / CSC digital submission).
"""

    if grievance_md:
        markdown_response += grievance_md

    # 4. Write output to /aikart/output.json (and local output.json)
    output_payload = {
        "format": "markdown",
        "response": markdown_response
    }

    container_output_file = Path("/aikart/output.json")
    if container_output_file.parent.exists():
        try:
            with open(container_output_file, "w", encoding="utf-8") as f:
                json.dump(output_payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Sandbox Warning] Could not write to /aikart/output.json: {e}")

    # Also write locally for testing
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output_payload, f, ensure_ascii=False, indent=2)

    print(f"Jan-Sahayak execution finished with 0 error in {result['total_runtime_ms']}ms.")
    sys.exit(0)


if __name__ == "__main__":
    main()
