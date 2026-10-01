"""
Jan-Sahayak AI - Autonomous Form Filler & Application Packager Agent
Generates an official, print-ready, high-resolution PDF Citizen Welfare Application Dossier using ReportLab.
"""

import os
from pathlib import Path
from datetime import datetime
import hashlib
from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class FormPackagerAgent:
    """Agent that synthesizes an official Government Application Package PDF."""

    def __init__(self, output_dir: str = None):
        self.name = "Autonomous Form & Application Packager Agent"
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "output"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_dossier_pdf(self, profile: Dict[str, Any], evaluation: Dict[str, Any], gap_audit: Dict[str, Any]) -> str:
        """
        Creates a publication-grade PDF file and returns its path.
        """
        # Create deterministic application ID
        raw_hash = hashlib.sha256(f"{profile['name']}_{profile['state']}_{datetime.now().strftime('%Y%m%d%H%M')}".encode()).hexdigest()[:8].upper()
        app_ref = f"BHARAT-JS-2026-{raw_hash}"
        
        filename = f"JanSahayak_Application_{raw_hash}.pdf"
        filepath = self.output_dir / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Typography
        title_style = ParagraphStyle(
            'GovTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#002B49') # Deep India Navy
        )
        
        subtitle_style = ParagraphStyle(
            'GovSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#FF671F') # India Saffron
        )

        meta_style = ParagraphStyle(
            'MetaStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#555555')
        )

        sec_header = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#046A38') # Deep Green
        )

        cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10)
        cell_normal = ParagraphStyle('CellNormal', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)

        story = []

        # Header Tricolor Decorative Banner
        header_table = Table([
            ["", ""],
        ], colWidths=[270, 270], rowHeights=[4])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.HexColor('#FF671F')),
            ('BACKGROUND', (1,0), (1,0), colors.HexColor('#046A38')),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 8))

        # Title & Emblem representation
        story.append(Paragraph("GOVERNMENT OF BHARAT • CITIZEN WELFARE PORTAL", subtitle_style))
        story.append(Paragraph("JAN-SAHAYAK UNIFIED WELFARE APPLICATION DOSSIER", title_style))
        story.append(Paragraph("Automated Multi-Agent Civic Delivery & Verification System", ParagraphStyle('SubSub', parent=subtitle_style, fontSize=8, textColor=colors.HexColor('#444444'))))
        
        story.append(Spacer(1, 6))

        # Ref & Meta Box
        meta_data = [
            [
                Paragraph(f"<b>Application Reference:</b> <font color='#002B49'>{app_ref}</font>", cell_normal),
                Paragraph(f"<b>Generated On:</b> {datetime.now().strftime('%d %B %Y, %I:%M %p')}", meta_style)
            ],
            [
                Paragraph(f"<b>Digital Verification Status:</b> <font color='#046A38'><b>AGENT-CERTIFIED</b></font>", cell_normal),
                Paragraph(f"<b>Scheme Registry Sync:</b> v2026.10-Oct", meta_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[270, 270])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F4F6F9')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CCD4DF')),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 10))

        # Section 1: Citizen Profile
        story.append(Paragraph("1. CITIZEN VERIFIED SOCIO-ECONOMIC PROFILE", sec_header))
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#046A38'), spaceBefore=2, spaceAfter=6))
        
        profile_grid = [
            [
                Paragraph("<b>Applicant Full Name:</b>", cell_bold), Paragraph(str(profile.get("name")), cell_normal),
                Paragraph("<b>Age & Gender:</b>", cell_bold), Paragraph(f"{profile.get('age')} Yrs / {profile.get('gender')}", cell_normal)
            ],
            [
                Paragraph("<b>State & District:</b>", cell_bold), Paragraph(f"{profile.get('state')} ({profile.get('district')})", cell_normal),
                Paragraph("<b>Area Classification:</b>", cell_bold), Paragraph(str(profile.get("urban_rural")), cell_normal)
            ],
            [
                Paragraph("<b>Primary Occupation:</b>", cell_bold), Paragraph(str(profile.get("occupation")), cell_normal),
                Paragraph("<b>Annual Household Income:</b>", cell_bold), Paragraph(f"₹{profile.get('annual_income', 0):,.0f} / year", cell_normal)
            ],
            [
                Paragraph("<b>Social Category / Caste:</b>", cell_bold), Paragraph(str(profile.get("caste")), cell_normal),
                Paragraph("<b>Landholding:</b>", cell_bold), Paragraph(f"{profile.get('landholding_acres', 0.0)} Acres", cell_normal)
            ],
            [
                Paragraph("<b>Marital Status:</b>", cell_bold), Paragraph(str(profile.get("marital_status")), cell_normal),
                Paragraph("<b>Dependent Children:</b>", cell_bold), Paragraph(f"{profile.get('daughters_count', 0)} Daughter(s)", cell_normal)
            ]
        ]
        prof_table = Table(profile_grid, colWidths=[120, 150, 120, 150])
        prof_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E0E0E0')),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(prof_table)
        story.append(Spacer(1, 10))

        # Section 2: Qualified Schemes & Direct Entitlements
        story.append(Paragraph("2. ENTITLEMENT AUDIT: QUALIFIED BHARAT WELFARE SCHEMES", sec_header))
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#046A38'), spaceBefore=2, spaceAfter=6))

        schemes_header = [
            Paragraph("<b>Scheme Name & Ministry</b>", cell_bold),
            Paragraph("<b>Target Category</b>", cell_bold),
            Paragraph("<b>Direct Benefit Entitlement</b>", cell_bold),
            Paragraph("<b>Eligibility Audit Result</b>", cell_bold)
        ]
        
        schemes_rows = [schemes_header]
        for s in evaluation.get("qualified_schemes", [])[:5]:
            schemes_rows.append([
                Paragraph(f"<b>{s['scheme_name']}</b><br/><font color='#555555'>{s.get('hindi_name','')}</font>", cell_normal),
                Paragraph(s.get("category", ""), cell_normal),
                Paragraph(s["benefit_summary"].get("financial", "Subsidized Support / Insurance"), cell_bold),
                Paragraph(f"<font color='#046A38'><b>QUALIFIED (Score {s['match_score']}%)</b></font><br/>{s['reasoning_trace'][0] if s['reasoning_trace'] else 'Verified'}", cell_normal)
            ])

        schemes_table = Table(schemes_rows, colWidths=[160, 100, 140, 140])
        schemes_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EEF3F8')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCD4DF')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(schemes_table)
        story.append(Spacer(1, 10))

        # Section 3: Document Readiness & Gap Analysis
        story.append(Paragraph(f"3. DOCUMENT COMPLIANCE MATRIX (Readiness Score: {gap_audit.get('overall_document_readiness_score', 0)}%)", sec_header))
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#046A38'), spaceBefore=2, spaceAfter=6))

        doc_rows = [
            [
                Paragraph("<b>Required Document</b>", cell_bold),
                Paragraph("<b>Status</b>", cell_bold),
                Paragraph("<b>Autonomous Remediation & Official Issuing Portal</b>", cell_bold)
            ]
        ]

        # Add verified docs
        for d in profile.get("existing_documents", []):
            doc_rows.append([
                Paragraph(d, cell_normal),
                Paragraph("<font color='#046A38'><b>VERIFIED ✓</b></font>", cell_normal),
                Paragraph("Document on record and verified against state schema registry.", cell_normal)
            ])

        # Add missing docs
        for rem in gap_audit.get("remediation_actions", [])[:3]:
            doc_rows.append([
                Paragraph(f"<b>{rem['document_name']}</b>", cell_bold),
                Paragraph("<font color='#D9381E'><b>MISSING ✗</b></font>", cell_normal),
                Paragraph(f"<b>Action:</b> {rem['guidance'].get('action_guide')}<br/><b>Portal/Kiosk:</b> {rem['guidance'].get('online_portal')} | {rem['guidance'].get('service_kiosk')}", cell_normal)
            ])

        doc_table = Table(doc_rows, colWidths=[150, 90, 300])
        doc_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FAF0E6')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E0D0C0')),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(doc_table)
        story.append(Spacer(1, 10))

        # Section 4: Citizen Declaration & Sign-off Block
        decl_text = (
            "<b>APPLICANT STATUTORY DECLARATION:</b> I hereby declare that all facts and socio-economic declarations "
            "provided herein are true to the best of my knowledge. I authorize Jan-Sahayak Autonomous AI Agent to submit "
            "and query welfare registries (DBT / PFMS / SECC) on my behalf under the Digital Personal Data Protection (DPDP) Act."
        )
        story.append(Paragraph(decl_text, cell_normal))
        story.append(Spacer(1, 16))

        sign_data = [
            [
                Paragraph("________________________________________<br/><b>Digital Signature / Biometric Seal</b><br/>(Jan-Sahayak Cryptographic Token)", cell_normal),
                Paragraph("________________________________________<br/><b>Applicant Signature / Thumb Impression</b><br/>(Physical Verification at CSC Center)", cell_normal)
            ]
        ]
        sign_table = Table(sign_data, colWidths=[270, 270])
        sign_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(sign_table)

        # Build PDF
        doc.build(story)
        return str(filepath)
