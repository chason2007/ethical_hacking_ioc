import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Palette
    BG_DARK = RGBColor(15, 23, 42)        # Slate 900
    CARD_BG = RGBColor(30, 41, 59)        # Slate 800
    TEXT_MAIN = RGBColor(248, 250, 252)   # Slate 50
    TEXT_MUTED = RGBColor(148, 163, 184)  # Slate 400
    CYAN = RGBColor(34, 211, 238)         # Cyan 400
    EMERALD = RGBColor(52, 211, 153)      # Emerald 400
    AMBER = RGBColor(251, 191, 36)        # Amber 400
    BORDER_COLOR = RGBColor(51, 65, 85)   # Slate 700

    def apply_dark_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text="PACKET ANALYSIS OF COMMON NETWORK PROTOCOLS"):
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = CYAN

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    slide_layout = prs.slide_layouts[6]
    s1 = prs.slides.add_slide(slide_layout)
    apply_dark_bg(s1)

    tbox = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(3.5))
    tf1 = tbox.text_frame
    tf1.word_wrap = True
    
    p_tag = tf1.paragraphs[0]
    p_tag.text = "ACADEMIC NETWORK SECURITY PROJECT"
    p_tag.font.size = Pt(14)
    p_tag.font.bold = True
    p_tag.font.color.rgb = CYAN

    p_main = tf1.add_paragraph()
    p_main.text = "Packet Analysis of Common Network Protocols"
    p_main.font.size = Pt(36)
    p_main.font.bold = True
    p_main.font.color.rgb = TEXT_MAIN

    p_sub = tf1.add_paragraph()
    p_sub.text = "A Modern Defensive Forensics & Educational Network Traffic Analysis Platform"
    p_sub.font.size = Pt(18)
    p_sub.font.color.rgb = TEXT_MUTED

    # Meta card
    card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(5.2), Inches(11.3), Inches(1.4))
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = BORDER_COLOR
    tf_meta = card.text_frame
    p_m1 = tf_meta.paragraphs[0]
    p_m1.text = "Course: Ethical Hacking / Network Security Elective (B.E. / B.Tech CS)"
    p_m1.font.size = Pt(13)
    p_m1.font.bold = True
    p_m1.font.color.rgb = EMERALD
    p_m2 = tf_meta.add_paragraph()
    p_m2.text = "Architecture: React 19 Frontend  •  Python FastAPI Backend  •  Local SQLite Database"
    p_m2.font.size = Pt(12)
    p_m2.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 2: Project Motivation & Goal
    # ==========================================
    s2 = prs.slides.add_slide(slide_layout)
    apply_dark_bg(s2)
    add_header(s2, "Why Build This? The Problem & Our Goal")

    cols = [
        ("The Challenge", [
            "Network security concepts are often taught purely through theory.",
            "Traditional tools like Wireshark are powerful but have a steep learning curve.",
            "Students struggle to connect raw packet hex bytes to real network behavior.",
            "Hard to correlate multi-step port scans and cleartext credential risks manually."
        ], AMBER),
        ("Our Defensive Solution", [
            "A clean, web-based dashboard that requires zero complex setup.",
            "Upload any .pcap or .pcapng file (up to 500MB) or load the 1-click demo.",
            "Visual breakdown of protocols from Layer 2 up to Layer 7.",
            "Defensive-only: Explains what is happening without offensive attacks."
        ], CYAN),
        ("Educational Impact", [
            "Helps students prepare for lab exams and project viva presentations.",
            "Provides contextual 'Why It Matters' explanations for every finding.",
            "Generates downloadable PDF audit reports for submission.",
            "Includes interactive TCP handshakes and viva Q&A cheat sheets."
        ], EMERALD)
    ]

    for i, (col_title, items, accent) in enumerate(cols):
        left = Inches(0.8 + i * 4.0)
        box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(2.0), Inches(3.7), Inches(4.7))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = BORDER_COLOR
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = col_title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = accent
        
        for item in items:
            p_item = tf.add_paragraph()
            p_item.text = f"•  {item}"
            p_item.font.size = Pt(12)
            p_item.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 3: End-to-End Application Flow
    # ==========================================
    s3 = prs.slides.add_slide(slide_layout)
    apply_dark_bg(s3)
    add_header(s3, "How It Works: End-to-End System Flow")

    steps = [
        ("1. Ingestion", "Upload .pcap / .pcapng\n(up to 500MB) or 1-click\nsynthetic demo sample", CYAN),
        ("2. Dissection", "Scapy packet engine\nparses Ethernet, IP,\nTCP, UDP, DNS, TLS", EMERALD),
        ("3. Analytics", "Computes 5-tuple flows,\nendpoints, port mapping\n& size histograms", CYAN),
        ("4. Security", "8 heuristic rules flag\nscans, floods, cleartext\n& DNS exfiltration", AMBER),
        ("5. Local Storage", "Zero Docker needed!\nSaves all results into\nlocal SQLite database", EMERALD),
        ("6. Web Dashboard", "Interactive charts,\nWireshark-style table,\nand 1-click PDF reports", CYAN),
    ]

    for i, (stitle, sdesc, scolor) in enumerate(steps):
        col = i % 3
        row = i // 3
        left = Inches(0.8 + col * 4.0)
        top = Inches(2.0 + row * 2.5)
        
        box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(3.7), Inches(2.2))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = BORDER_COLOR
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = stitle
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = scolor
        
        p_desc = tf.add_paragraph()
        p_desc.text = sdesc
        p_desc.font.size = Pt(12)
        p_desc.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 4: Protocols Analyzed (L2 - L7)
    # ==========================================
    s4 = prs.slides.add_slide(slide_layout)
    apply_dark_bg(s4)
    add_header(s4, "Multi-Layer Protocol Support (L2 to L7)")

    proto_cards = [
        ("Layer 2: Data Link", "Ethernet II & ARP", "Extracts Source & Destination MAC addresses, EtherType frame IDs, and ARP broadcast resolution.", CYAN),
        ("Layer 3: Network", "IPv4 & IPv6", "Analyzes Source/Destination IPs, TTL hop decay, header lengths, and RFC 1918 Private vs Public IPs.", EMERALD),
        ("Layer 4: Transport", "TCP, UDP, ICMP", "Tracks TCP 3-way handshakes, sequence numbers, flag combinations (SYN, ACK, RST, FIN), and ICMP ping types.", CYAN),
        ("Layer 7: Application", "DNS, HTTP, TLS/HTTPS", "Inspects DNS queries & response codes, detects cleartext HTTP methods & URIs, and parses TLS SNI domain names.", AMBER),
    ]

    for i, (layer_title, proto_names, desc, color) in enumerate(proto_cards):
        left = Inches(0.8 + (i % 2) * 6.0)
        top = Inches(2.0 + (i // 2) * 2.5)
        
        box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(5.7), Inches(2.2))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = BORDER_COLOR
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = f"{layer_title}  •  {proto_names}"
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = color
        
        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(12)
        p_desc.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 5: Core Features Overview
    # ==========================================
    s5 = prs.slides.add_slide(slide_layout)
    apply_dark_bg(s5)
    add_header(s5, "Key Features: What You Can Do in the UI")

    features = [
        ("📊 Operations Dashboard", "High-level overview with total packets, bytes, unique IPs, protocol doughnut chart, and MTU packet size histogram."),
        ("🔍 Packet Explorer & Inspector", "Wireshark-style sortable table with instant search, protocol filters, collapsible layer tree, and hex preview."),
        ("💬 5-Tuple Conversations", "Tracks bidirectional communication pairs (IP1 + Port1 <-> IP2 + Port2), bytes transferred, and session durations."),
        ("🌐 Endpoints & Ports", "Host directory showing who sent/received the most data, plus destination ports mapped to IANA services (DNS, HTTP, SSH)."),
        ("🛡️ Defensive Security Insights", "Automated anomaly detection: flags port scans, SYN floods, RST bursts, DNS tunneling, and cleartext credentials."),
        ("📄 Reports & Viva Prep", "1-click professional PDF audit report download, CSV/JSON data exports, and interactive viva Q&A cheat sheets.")
    ]

    for i, (ftitle, fdesc) in enumerate(features):
        left = Inches(0.8 + (i % 2) * 6.0)
        top = Inches(1.8 + (i // 2) * 1.7)
        
        box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(5.7), Inches(1.5))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = BORDER_COLOR
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = ftitle
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = CYAN
        
        p_desc = tf.add_paragraph()
        p_desc.text = fdesc
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 6: Defensive Security Detection Rules
    # ==========================================
    s6 = prs.slides.add_slide(slide_layout)
    apply_dark_bg(s6)
    add_header(s6, "Defensive Security Engine: Built-In Detection Rules")

    rules = [
        ("SYN Port Scanning", "Detects single host probing multiple distinct ports in short order.", "HIGH", AMBER),
        ("SYN Flood / Half-Open", "Detects elevated ratio of SYN requests without completing the 3-way handshake.", "HIGH", AMBER),
        ("Elevated TCP Reset (RST)", "Flags abnormal burst of RST packets indicating closed ports or firewall drops.", "MEDIUM", CYAN),
        ("DNS Tunneling Heuristics", "Identifies unusually long domain queries (>45 chars) or high entropy subdomains.", "MEDIUM", CYAN),
        ("Cleartext Credentials", "Flags unencrypted HTTP forms sending passwords or sensitive auth headers.", "HIGH", AMBER),
        ("Uncommon Port Activity", "Warns about traffic over high-risk or unusual administrative ports.", "LOW", EMERALD)
    ]

    for i, (rtitle, rdesc, rsev, rcolor) in enumerate(rules):
        col = i % 3
        row = i // 3
        left = Inches(0.8 + col * 4.0)
        top = Inches(2.0 + row * 2.5)
        
        box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(3.7), Inches(2.2))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = BORDER_COLOR
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = f"[{rsev}] {rtitle}"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = rcolor
        
        p_desc = tf.add_paragraph()
        p_desc.text = rdesc
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = TEXT_MAIN

        p_note = tf.add_paragraph()
        p_note.text = "\nIncludes 'Why It Matters' & remediation guidance for every alert."
        p_note.font.size = Pt(10)
        p_note.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 7: Technology Stack
    # ==========================================
    s7 = prs.slides.add_slide(slide_layout)
    apply_dark_bg(s7)
    add_header(s7, "Technology Stack & Architecture")

    tech_cards = [
        ("Frontend (User Interface)", [
            "React 19 & TypeScript",
            "Vite 8 build system",
            "Tailwind CSS (dark cybersecurity theme)",
            "Lucide React vector icons",
            "Zero heavy third-party UI templates"
        ], CYAN),
        ("Backend (Analysis Engine)", [
            "Python 3.10 - 3.14 + FastAPI",
            "Scapy for streaming PCAP dissection",
            "Pydantic data validation schemas",
            "ReportLab for PDF report compilation",
            "Uvicorn asynchronous ASGI server"
        ], EMERALD),
        ("Storage & Deployment", [
            "Local SQLite database (network_analysis.db)",
            "Zero Docker or external DB services needed",
            "Sub-millisecond query responses & pagination",
            "Runs natively on Windows, Linux, and macOS",
            "Automated one-click start script provided"
        ], AMBER),
    ]

    for i, (ttitle, titems, tcolor) in enumerate(tech_cards):
        left = Inches(0.8 + i * 4.0)
        box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(2.0), Inches(3.7), Inches(4.7))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = BORDER_COLOR
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = ttitle
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = tcolor
        
        for item in titems:
            p_item = tf.add_paragraph()
            p_item.text = f"•  {item}"
            p_item.font.size = Pt(12)
            p_item.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 8: Summary & Viva Takeaways
    # ==========================================
    s8 = prs.slides.add_slide(slide_layout)
    apply_dark_bg(s8)
    add_header(s8, "Summary & Key Project Takeaways")

    takeaways = [
        ("Real-World Relevance", "Bridges academic networking theory (OSI model, handshakes) with real-world defensive Security Operations Center (SOC) workflows.", CYAN),
        ("Production Quality", "Supports up to 500MB PCAP files with fast asynchronous parsing, responsive search, and clean error handling.", EMERALD),
        ("Defensive & Ethical", "Strictly passive analysis: inspects captured packets without launching attacks or modifying network configurations.", CYAN),
        ("Ready for Review", "Complete documentation, passing unit tests, viva Q&A study guide, and professional PDF deliverable exports included.", AMBER),
    ]

    for i, (title, desc, color) in enumerate(takeaways):
        left = Inches(0.8 + (i % 2) * 6.0)
        top = Inches(2.0 + (i // 2) * 2.5)
        
        box = s8.slides.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(5.7), Inches(2.2))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = BORDER_COLOR
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = f"✔  {title}"
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = color
        
        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(13)
        p_desc.font.color.rgb = TEXT_MAIN

    output_path = Path("Packet_Analysis_Project_Presentation.pptx")
    prs.save(str(output_path))
    print(f"[SUCCESS] Presentation generated: {output_path.resolve()}")

if __name__ == "__main__":
    create_deck()
