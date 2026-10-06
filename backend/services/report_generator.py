import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)

from backend.config import settings

class ReportGenerator:
    @staticmethod
    def generate_pdf_report(
        capture_meta: Dict[str, Any],
        stats: Dict[str, Any],
        protocol_stats: List[Dict[str, Any]],
        endpoints: List[Dict[str, Any]],
        conversations: List[Dict[str, Any]],
        findings: List[Dict[str, Any]],
        output_filepath: Path = None,
    ) -> Path:
        if output_filepath is None:
            filename = f"Report_{capture_meta.get('id', 'export')}_{int(datetime.utcnow().timestamp())}.pdf"
            output_filepath = settings.REPORTS_DIR / filename
            
        output_filepath.parent.mkdir(parents=True, exist_ok=True)
        
        doc = SimpleDocTemplate(
            str(output_filepath),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        
        # Custom cybersecurity styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0f172a'),
            fontName='Helvetica-Bold',
            spaceAfter=6,
        )
        
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#475569'),
            spaceAfter=14,
        )

        h1_style = ParagraphStyle(
            'SecHeading',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#1e293b'),
            fontName='Helvetica-Bold',
            spaceBefore=14,
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#334155'),
            spaceAfter=6,
        )

        badge_high = ParagraphStyle(
            'BadgeHigh',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#dc2626'),
        )
        badge_med = ParagraphStyle(
            'BadgeMed',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#d97706'),
        )
        badge_low = ParagraphStyle(
            'BadgeLow',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#2563eb'),
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("SECURITY AUDIT & PACKET ANALYSIS REPORT", title_style))
        story.append(Paragraph(
            f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | Defensive Network Protocol Inspector",
            subtitle_style
        ))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))

        # 2. Capture Information Table
        story.append(Paragraph("1. Capture Metadata", h1_style))
        meta_table_data = [
            [Paragraph("<b>Capture File:</b>", body_style), Paragraph(str(capture_meta.get("filename", "N/A")), body_style),
             Paragraph("<b>Capture ID:</b>", body_style), Paragraph(str(capture_meta.get("id", "N/A"))[:18] + "...", body_style)],
            [Paragraph("<b>Total Packets:</b>", body_style), Paragraph(str(stats.get("total_packets", 0)), body_style),
             Paragraph("<b>Total Traffic:</b>", body_style), Paragraph(f"{stats.get('total_bytes', 0):,} bytes", body_style)],
            [Paragraph("<b>Duration:</b>", body_style), Paragraph(f"{stats.get('duration_seconds', 0.0):.2f} seconds", body_style),
             Paragraph("<b>Unique Endpoints:</b>", body_style), Paragraph(str(stats.get("unique_ips", 0)), body_style)],
            [Paragraph("<b>Conversations:</b>", body_style), Paragraph(str(stats.get("unique_conversations", 0)), body_style),
             Paragraph("<b>Security Findings:</b>", body_style), Paragraph(f"<b>{len(findings)} detected</b>", body_style)],
        ]
        t_meta = Table(meta_table_data, colWidths=[100, 170, 110, 160])
        t_meta.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_meta)
        story.append(Spacer(1, 10))

        # 3. Executive Summary
        story.append(Paragraph("2. Executive Summary", h1_style))
        exec_summary_text = (
            f"An automated deep packet inspection was executed on <b>{capture_meta.get('filename')}</b>. "
            f"The capture encompasses <b>{stats.get('total_packets', 0)} frames</b> across a span of "
            f"<b>{stats.get('duration_seconds', 0):.2f} seconds</b>, involving {stats.get('unique_ips', 0)} unique IP endpoints and "
            f"{stats.get('unique_conversations', 0)} discrete network conversations. "
            f"A total of <b>{len(findings)} heuristic security anomalies/indicators</b> were detected during inspection."
        )
        story.append(Paragraph(exec_summary_text, body_style))
        story.append(Spacer(1, 10))

        # 4. Protocol Distribution Table
        story.append(Paragraph("3. Protocol Distribution Breakdown", h1_style))
        proto_header = [Paragraph("<b>Protocol</b>", body_style), Paragraph("<b>Layer</b>", body_style), Paragraph("<b>Packets</b>", body_style), Paragraph("<b>Bytes</b>", body_style), Paragraph("<b>Share (%)</b>", body_style)]
        proto_rows = [proto_header]
        for p in protocol_stats[:8]:
            proto_rows.append([
                Paragraph(p.get("protocol_name", ""), body_style),
                Paragraph(p.get("layer", ""), body_style),
                Paragraph(str(p.get("packet_count", 0)), body_style),
                Paragraph(f"{p.get('byte_count', 0):,}", body_style),
                Paragraph(f"{p.get('percentage', 0):.1f}%", body_style),
            ])
        t_proto = Table(proto_rows, colWidths=[120, 100, 100, 110, 110])
        t_proto.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_proto)
        story.append(Spacer(1, 10))

        # 5. Top Endpoints Table
        story.append(Paragraph("4. Most Active Network Endpoints", h1_style))
        ep_header = [Paragraph("<b>Address</b>", body_style), Paragraph("<b>Type</b>", body_style), Paragraph("<b>Scope</b>", body_style), Paragraph("<b>Tx Pkts</b>", body_style), Paragraph("<b>Rx Pkts</b>", body_style), Paragraph("<b>Total Bytes</b>", body_style)]
        ep_rows = [ep_header]
        for ep in endpoints[:6]:
            scope = "Private / RFC1918" if ep.get("is_private") else "Public Internet"
            ep_rows.append([
                Paragraph(ep.get("address", ""), body_style),
                Paragraph(ep.get("address_type", ""), body_style),
                Paragraph(scope, body_style),
                Paragraph(str(ep.get("packets_sent", 0)), body_style),
                Paragraph(str(ep.get("packets_received", 0)), body_style),
                Paragraph(f"{ep.get('total_bytes', 0):,}", body_style),
            ])
        t_ep = Table(ep_rows, colWidths=[120, 60, 120, 80, 80, 80])
        t_ep.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_ep)
        story.append(Spacer(1, 14))

        # 6. Security Findings
        story.append(Paragraph("5. Security Insights & Anomaly Analysis", h1_style))
        if not findings:
            story.append(Paragraph("No anomalous patterns detected in this capture.", body_style))
        else:
            for idx, f in enumerate(findings, 1):
                sev = f.get("severity", "INFORMATIONAL")
                badge = badge_high if sev == "HIGH" else badge_med if sev == "MEDIUM" else badge_low
                
                f_box = [
                    [Paragraph(f"<b>[{idx}] {f.get('title')}</b>", body_style), Paragraph(f"Severity: <b>{sev}</b>", badge)],
                    [Paragraph(f"<b>Evidence:</b> {f.get('evidence')}", body_style), Paragraph("", body_style)],
                    [Paragraph(f"<b>Why It Matters:</b> {f.get('why_it_matters')}", body_style), Paragraph("", body_style)],
                    [Paragraph(f"<b>Analyst Recommendation:</b> {f.get('recommendation')}", body_style), Paragraph("", body_style)],
                ]
                t_f = Table(f_box, colWidths=[430, 110])
                bg_color = colors.HexColor('#fef2f2') if sev == 'HIGH' else colors.HexColor('#fffbeb') if sev == 'MEDIUM' else colors.HexColor('#f0f9ff')
                border_color = colors.HexColor('#f87171') if sev == 'HIGH' else colors.HexColor('#fcd34d') if sev == 'MEDIUM' else colors.HexColor('#93c5fd')
                
                t_f.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), bg_color),
                    ('BOX', (0,0), (-1,-1), 1, border_color),
                    ('SPAN', (0,1), (1,1)),
                    ('SPAN', (0,2), (1,2)),
                    ('SPAN', (0,3), (1,3)),
                    ('PADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(t_f)
                story.append(Spacer(1, 8))

        # 7. Recommendations & Conclusion
        story.append(Spacer(1, 10))
        story.append(Paragraph("6. Defensive Recommendations & Conclusion", h1_style))
        conclusion_p = (
            "1. Segment internal VLANs and configure switch port access controls to isolate scanning sources.<br/>"
            "2. Enforce encrypted protocols across all internal services (HTTP -> HTTPS, FTP/Telnet -> SSH/SFTP).<br/>"
            "3. Deploy continuous packet telemetry and response policy zones (RPZ) on internal DNS resolvers.<br/>"
            "4. Establish baseline network utilization profiles to rapidly flag unusual deviations in connection volume."
        )
        story.append(Paragraph(conclusion_p, body_style))

        # Build document
        doc.build(story)
        return output_filepath
