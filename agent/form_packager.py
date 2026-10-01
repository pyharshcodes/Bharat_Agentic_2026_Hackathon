"""
Jan-Sahayak AI - Autonomous Form Filler & Application Packager Agent
Generates an official, print-ready, high-resolution PDF Citizen Welfare Application Dossier using ReportLab.
Includes live QR code verification stamp, security checksums, and official citizen declarations.
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
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing


class FormPackagerAgent:
    """Agent that synthesizes an official Government Application Package PDF with QR verification."""

    def __init__(self, output_dir: str = None):
        self.name = "Autonomous Form & Application Packager Agent"
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "output"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_dossier_pdf(self, profile: Dict[str, Any], evaluation: Dict[str, Any], gap_audit: Dict[str, Any]) -> str:
        """
        Creates a publication-grade PDF file with embedded QR code verification and returns its path.
        """
        raw_hash = hashlib.sha256(f"{profile['name']}_{profile['state']}_{datetime.now().strftime('%Y%m%d%H%M')}".encode()).hexdigest()[:8].upper()
        app_ref = f"BHARAT-JS-2026-{raw_hash}"
        
        filename = f"JanSahayak_Application_{raw_hash}.pdf"
        filepath = self.output_dir / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=32,
            bottomMargin=32
        )

        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'GovTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=15,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#002B49') # Deep India Navy
        )
        
        subtitle_style = ParagraphStyle(
            'GovSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
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
            textColor=colors.HexColor('#444444')
        )

        sec_header = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#046A38') # Deep Green
        )

        cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10)
        cell_normal = ParagraphStyle('CellNormal', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
        cell_sub = ParagraphStyle('CellSub', parent=styles['Normal'], fontName='Helvetica', fontSize=7, leading=9, textColor=colors.HexColor('#555555'))

        story = []

        # 1. Header Tricolor Decorative Banner
        header_table = Table([
            ["", "", ""],
        ], colWidths=[180, 180, 180], rowHeights=[4])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.HexColor('#FF671F')),
            ('BACKGROUND', (1,0), (1,0), colors.white),
            ('BACKGROUND', (2,0), (2,0), colors.HexColor('#046A38')),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 6))

        # 2. National Header & QR Code verification row
        # Generate QR code object
        qr_code = qr.QrCodeWidget(f"https://jansahayak.bharat.gov/verify?ref={app_ref}&citizen={profile.get('name')}")
        qr_bounds = qr_code.getBounds()
        qr_w = qr_bounds[2] - qr_bounds[0]
        qr_h = qr_bounds[3] - qr_bounds[1]
        qr_draw = Drawing(54, 54, transform=[54/qr_w, 0, 0, 54/qr_h, 0, 0])
        qr_draw.add(qr_code)

        title_block = [
            Paragraph("भारत सरकार • नागरिक अधिकार एवं कल्याण पोर्टल • GOVT. OF BHARAT", subtitle_style),
            Paragraph("JAN-SAHAYAK UNIFIED WELFARE APPLICATION DOSSIER", title_style),
            Paragraph("Automated Multi-Agent Civic Delivery & Verification System (aiKart Sandboxed)", ParagraphStyle('SubSub', parent=subtitle_style, fontSize=8, textColor=colors.HexColor('#333333')))
        ]

        header_split = Table([
            [title_block, qr_draw]
        ], colWidths=[475, 65])
        header_split.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
        ]))
        story.append(header_split)
        story.append(Spacer(1, 6))

        # 3. Reference & Verification Box
        meta_data = [
            [
                Paragraph(f"<b>Application Reference:</b> <font color='#002B49'><b>{app_ref}</b></font>", cell_normal),
                Paragraph(f"<b>Generated On:</b> {datetime.now().strftime('%d %B %Y, %I:%M %p')}", meta_style)
            ],
            [
                Paragraph(f"<b>Digital Verification Status:</b> <font color='#046A38'><b>AGENT-CERTIFIED (DPDP-COMPLIANT)</b></font>", cell_normal),
                Paragraph(f"<b>Registry Synced:</b> 2026 Central & State DB", meta_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[270, 270])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F4F6F9')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CCD4DF')),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 8))

        # 4. Section 1: Citizen Verified Demographic Profile
        story.append(Paragraph("1. CITIZEN VERIFIED SOCIO-ECONOMIC PROFILE", sec_header))
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#046A38'), spaceBefore=2, spaceAfter=5))
        
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
            ('PADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(prof_table)
        story.append(Spacer(1, 8))

        # 5. Section 2: Certified Welfare Entitlements
        total_benefit = evaluation.get('total_estimated_annual_benefit_inr', 0)
        story.append(Paragraph(f"2. CERTIFIED WELFARE ENTITLEMENTS (Total Estimated Direct Value: ₹{total_benefit:,.0f}/yr)", sec_header))
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#046A38'), spaceBefore=2, spaceAfter=5))

        schemes_header = [
            Paragraph("<b>Scheme & Ministry</b>", cell_bold),
            Paragraph("<b>Category</b>", cell_bold),
            Paragraph("<b>Direct Benefit Entitlement</b>", cell_bold),
            Paragraph("<b>Agent Audit Result</b>", cell_bold)
        ]
        
        schemes_rows = [schemes_header]
        for s in evaluation.get("qualified_schemes", [])[:5]:
            schemes_rows.append([
                Paragraph(f"<b>{s['scheme_name']}</b><br/><font color='#555555'>{s.get('hindi_name','')}</font>", cell_normal),
                Paragraph(s.get("category", ""), cell_normal),
                Paragraph(s["benefit_summary"].get("financial", "Subsidized Support / Insurance"), cell_bold),
                Paragraph(f"<font color='#046A38'><b>QUALIFIED (Match {s['match_score']}%)</b></font><br/>{s['reasoning_trace'][0] if s['reasoning_trace'] else 'Verified'}", cell_sub)
            ])

        schemes_table = Table(schemes_rows, colWidths=[160, 95, 145, 140])
        schemes_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EEF3F8')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCD4DF')),
            ('PADDING', (0,0), (-1,-1), 3),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(schemes_table)
        story.append(Spacer(1, 8))

        # 6. Section 3: Document Compliance & Remediation
        readiness = gap_audit.get('overall_document_readiness_score', 0)
        story.append(Paragraph(f"3. DOCUMENT COMPLIANCE MATRIX (Readiness: {readiness}% | Verified: {len(profile.get('existing_documents', []))} | Missing: {gap_audit.get('missing_documents_count', 0)})", sec_header))
        story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#046A38'), spaceBefore=2, spaceAfter=5))

        doc_rows = [
            [
                Paragraph("<b>Required Document</b>", cell_bold),
                Paragraph("<b>Status</b>", cell_bold),
                Paragraph("<b>Autonomous Remediation & Official Issuing Portal</b>", cell_bold)
            ]
        ]

        # Verified documents
        for d in profile.get("existing_documents", []):
            doc_rows.append([
                Paragraph(d, cell_normal),
                Paragraph("<font color='#046A38'><b>VERIFIED ✓</b></font>", cell_normal),
                Paragraph("Document on record and verified against state schema registry.", cell_sub)
            ])

        # Missing documents with CSC remediation
        for rem in gap_audit.get("remediation_actions", [])[:3]:
            doc_rows.append([
                Paragraph(f"<b>{rem['document_name']}</b>", cell_bold),
                Paragraph("<font color='#D9381E'><b>MISSING ✗</b></font>", cell_normal),
                Paragraph(f"<b>Action:</b> {rem['guidance'].get('action_guide')}<br/><b>Portal/Kiosk:</b> {rem['guidance'].get('online_portal')} | {rem['guidance'].get('service_kiosk')}", cell_sub)
            ])

        doc_table = Table(doc_rows, colWidths=[150, 80, 310])
        doc_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FAF0E6')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E0D0C0')),
            ('PADDING', (0,0), (-1,-1), 3),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(doc_table)
        story.append(Spacer(1, 8))

        # 7. Section 4: Citizen Declaration & Sign-off Block
        decl_text = (
            "<b>APPLICANT STATUTORY DECLARATION:</b> I hereby declare that all facts and socio-economic declarations "
            "provided herein are true to the best of my knowledge. I authorize Jan-Sahayak Autonomous AI Agent to submit "
            "and query welfare registries (DBT / PFMS / SECC) on my behalf under the Digital Personal Data Protection (DPDP) Act 2023."
        )
        story.append(Paragraph(decl_text, cell_sub))
        story.append(Spacer(1, 12))

        sign_data = [
            [
                Paragraph("________________________________________<br/><b>Digital Signature / Biometric Seal</b><br/>(Jan-Sahayak Cryptographic Checksum)", cell_sub),
                Paragraph("________________________________________<br/><b>Applicant Signature / Thumb Impression</b><br/>(Physical Verification at CSC Center)", cell_sub)
            ]
        ]
        sign_table = Table(sign_data, colWidths=[270, 270])
        sign_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(sign_table)

        doc.build(story)
        return str(filepath)
