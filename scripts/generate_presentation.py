from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Modern High-End Palette
    BG_DARK = RGBColor(10, 15, 29)         # Deep Navy (#0A0F1D)
    CARD_BG = RGBColor(21, 30, 50)         # Soft Slate Navy (#151E32)
    CARD_BORDER = RGBColor(38, 52, 78)     # Muted Outline (#26344E)
    TEXT_MAIN = RGBColor(248, 250, 252)    # Pure Crisp White (#F8FAFC)
    TEXT_MUTED = RGBColor(148, 163, 184)   # Slate 400 (#94A3B8)
    CYAN = RGBColor(6, 182, 212)           # Electric Cyan (#06B6D4)
    EMERALD = RGBColor(16, 185, 129)       # Neon Mint (#10B981)
    AMBER = RGBColor(245, 158, 11)         # Soft Amber (#F59E0B)
    PURPLE = RGBColor(168, 85, 247)        # Accent Purple (#A855F7)

    def apply_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def add_clean_header(slide, title, category="NETWORK PROTOCOL INSPECTOR"):
        # Category Pill
        cat_box = slide.shapes.add_textbox(Inches(0.9), Inches(0.55), Inches(11.5), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_c = tf_cat.paragraphs[0]
        p_c.text = category.upper()
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = CYAN

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.9), Inches(0.85), Inches(11.5), Inches(0.75))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_t = tf_title.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(24)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 1: Title Slide (Minimalist & Punchy)
    # ==========================================
    s1 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(s1)

    # Accent decorative top bar
    bar = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), Inches(1.2), Inches(1.2), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = CYAN
    bar.line.fill.background()

    # Title box
    tbox = s1.shapes.add_textbox(Inches(0.9), Inches(1.5), Inches(11.5), Inches(3.2))
    tf1 = tbox.text_frame
    tf1.word_wrap = True
    
    p_badge = tf1.paragraphs[0]
    p_badge.text = "DEFENSIVE CYBERSECURITY & TRAFFIC ANALYSIS"
    p_badge.font.size = Pt(12)
    p_badge.font.bold = True
    p_badge.font.color.rgb = CYAN

    p_main = tf1.add_paragraph()
    p_main.text = "Packet Analysis of\nCommon Network Protocols"
    p_main.font.size = Pt(38)
    p_main.font.bold = True
    p_main.font.color.rgb = TEXT_MAIN

    p_sub = tf1.add_paragraph()
    p_sub.text = "A simple, web-based platform to dissect packets, visualize traffic, and spot anomalies."
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = TEXT_MUTED

    # Bottom Pill Cards
    pills = [
        ("Course", "Ethical Hacking / Network Security", EMERALD),
        ("Mode", "Strictly Defensive & Passive", CYAN),
        ("Setup", "100% Local (Zero Docker)", AMBER),
    ]
    for i, (tag, val, clr) in enumerate(pills):
        box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9 + i * 3.8), Inches(5.4), Inches(3.5), Inches(1.2))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = CARD_BORDER
        tf = box.text_frame
        tf.word_wrap = True
        
        p1 = tf.paragraphs[0]
        p1.text = tag.upper()
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = clr

        p2 = tf.add_paragraph()
        p2.text = val
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 2: The Core Idea (3 Words: Ingest, Decode, Defend)
    # ==========================================
    s2 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(s2)
    add_clean_header(s2, "The Core Mission: Ingest. Decode. Defend.")

    cards_s2 = [
        ("01", "INGEST", "Drop any .pcap or .pcapng file up to 500MB, or load the instant 1-click demo.", CYAN),
        ("02", "DECODE", "Automatically unpack every layer from Ethernet to IP, TCP, DNS, and TLS.", EMERALD),
        ("03", "DEFEND", "Spot port scans, SYN floods, cleartext passwords, and DNS anomalies in seconds.", AMBER),
    ]

    for i, (num, heading, blurb, accent) in enumerate(cards_s2):
        left = Inches(0.9 + i * 3.9)
        box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(2.0), Inches(3.6), Inches(4.5))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = CARD_BORDER
        tf = box.text_frame
        tf.word_wrap = True

        p_num = tf.paragraphs[0]
        p_num.text = num
        p_num.font.size = Pt(28)
        p_num.font.bold = True
        p_num.font.color.rgb = accent

        p_h = tf.add_paragraph()
        p_h.text = heading
        p_h.font.size = Pt(18)
        p_h.font.bold = True
        p_h.font.color.rgb = TEXT_MAIN

        p_b = tf.add_paragraph()
        p_b.text = f"\n{blurb}"
        p_b.font.size = Pt(13)
        p_b.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 3: System Flow (Clean 4-Step Pipeline)
    # ==========================================
    s3 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(s3)
    add_clean_header(s3, "How It Works: Clean 4-Stage Pipeline")

    pipeline = [
        ("STEP 1", "Upload Capture", "Accepts standard .pcap / .pcapng files up to 500MB.", CYAN),
        ("STEP 2", "Multi-Layer Parser", "Dissects Ethernet, IP, TCP, UDP, ICMP, DNS & TLS.", EMERALD),
        ("STEP 3", "Rule-Based Defense", "Evaluates 8 heuristic checks for scans and leaks.", AMBER),
        ("STEP 4", "Interactive UI", "Live charts, Wireshark grid, and 1-click PDF reports.", CYAN),
    ]

    for i, (step, name, desc, clr) in enumerate(pipeline):
        left = Inches(0.9 + i * 2.9)
        box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(2.2), Inches(2.7), Inches(3.8))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = CARD_BORDER
        tf = box.text_frame
        tf.word_wrap = True

        p_s = tf.paragraphs[0]
        p_s.text = step
        p_s.font.size = Pt(11)
        p_s.font.bold = True
        p_s.font.color.rgb = clr

        p_n = tf.add_paragraph()
        p_n.text = name
        p_n.font.size = Pt(16)
        p_n.font.bold = True
        p_n.font.color.rgb = TEXT_MAIN

        p_d = tf.add_paragraph()
        p_d.text = f"\n{desc}"
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 4: Protocols Analyzed (L2 - L7 Stack)
    # ==========================================
    s4 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(s4)
    add_clean_header(s4, "Full-Stack Protocol Coverage (L2 to L7)")

    layers = [
        ("L7 Application", "DNS, HTTP, TLS", "Domain queries, cleartext URLs/methods, and TLS SNI domain handshakes.", CYAN),
        ("L4 Transport", "TCP, UDP, ICMP", "3-way handshakes, all 6 TCP flags (SYN, ACK, RST), and ICMP ping echoes.", EMERALD),
        ("L3 Network", "IPv4, IPv6", "Source/Destination addresses, TTL hop limits, and Private vs Public IP tags.", AMBER),
        ("L2 Data Link", "Ethernet II, ARP", "Physical MAC addresses, EtherType frame IDs, and ARP address resolution.", PURPLE),
    ]

    for i, (layer_name, protos, detail, clr) in enumerate(layers):
        top = Inches(1.9 + i * 1.25)
        box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), top, Inches(11.5), Inches(1.05))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = CARD_BORDER
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = f"{layer_name}   •   {protos}"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = clr

        p_sub = tf.add_paragraph()
        p_sub.text = detail
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 5: Key Features (The Experience)
    # ==========================================
    s5 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(s5)
    add_clean_header(s5, "What You See & Do in the Application")

    feats = [
        ("📊 Operations Dashboard", "High-level overview: total packets, bytes, unique IPs, protocol doughnut chart, and MTU packet size histogram.", CYAN),
        ("🔍 Packet Explorer & Inspector", "Wireshark-style sortable table with instant search, protocol filters, collapsible layer tree, and hex dump.", EMERALD),
        ("💬 5-Tuple Conversations", "Tracks bidirectional communication pairs (Host A <-> Host B), bytes transferred, and session durations.", AMBER),
        ("🌐 Endpoints & Port Mapping", "Host directory showing top talkers, plus destination ports mapped to recognized services (443->HTTPS, 53->DNS).", PURPLE),
    ]

    for i, (ftitle, fdesc, clr) in enumerate(feats):
        col = i % 2
        row = i // 2
        left = Inches(0.9 + col * 5.9)
        top = Inches(2.0 + row * 2.4)

        box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(5.6), Inches(2.1))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = CARD_BORDER
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = ftitle
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = clr

        p_d = tf.add_paragraph()
        p_d.text = f"\n{fdesc}"
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = TEXT_MAIN

    # ==========================================
    # SLIDE 6: Defensive Security Engine
    # ==========================================
    s6 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(s6)
    add_clean_header(s6, "Defensive Security Engine: What We Detect")

    threats = [
        ("🔍 Port Scans", "Flags single hosts probing multiple ports within short time windows.", "HIGH SEVERITY", AMBER),
        ("⚠️ SYN Half-Open Floods", "Identifies abnormal bursts of SYN packets with no completed handshakes.", "HIGH SEVERITY", AMBER),
        ("🕵️ DNS Tunneling Indicators", "Catches unusually long domain queries (>45 chars) or high entropy names.", "MEDIUM SEVERITY", CYAN),
        ("🔓 Cleartext Password Leaks", "Flags unencrypted HTTP forms sending authentication credentials in the clear.", "HIGH SEVERITY", AMBER),
    ]

    for i, (ttitle, tdesc, tsev, tclr) in enumerate(threats):
        col = i % 2
        row = i // 2
        left = Inches(0.9 + col * 5.9)
        top = Inches(2.0 + row * 2.4)

        box = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(5.6), Inches(2.1))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = CARD_BORDER
        tf = box.text_frame
        tf.word_wrap = True

        p_s = tf.paragraphs[0]
        p_s.text = tsev
        p_s.font.size = Pt(10)
        p_s.font.bold = True
        p_s.font.color.rgb = tclr

        p_t = tf.add_paragraph()
        p_t.text = ttitle
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_MAIN

        p_d = tf.add_paragraph()
        p_d.text = f"\n{tdesc}"
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 7: Architecture (100% Local & Clean)
    # ==========================================
    s7 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(s7)
    add_clean_header(s7, "System Architecture: Fast, Simple & 100% Local")

    arch_cards = [
        ("Frontend", "React 19 + Vite", "Modern cybersecurity dark theme using Tailwind CSS and Lucide icons.", CYAN),
        ("Backend", "Python FastAPI", "Streaming packet parser using Scapy with asynchronous REST APIs.", EMERALD),
        ("Database", "Local SQLite", "Zero Docker needed. All capture data stored locally in network_analysis.db.", AMBER),
    ]

    for i, (comp, tech, detail, clr) in enumerate(arch_cards):
        left = Inches(0.9 + i * 3.9)
        box = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(2.0), Inches(3.6), Inches(4.5))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = CARD_BORDER
        tf = box.text_frame
        tf.word_wrap = True

        p_c = tf.paragraphs[0]
        p_c.text = comp.upper()
        p_c.font.size = Pt(12)
        p_c.font.bold = True
        p_c.font.color.rgb = clr

        p_t = tf.add_paragraph()
        p_t.text = tech
        p_t.font.size = Pt(18)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_MAIN

        p_d = tf.add_paragraph()
        p_d.text = f"\n{detail}\n\n• Sub-millisecond queries\n• 500MB upload support\n• Zero complex dependencies"
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 8: Review & Viva Ready
    # ==========================================
    s8 = prs.slides.add_slide(prs.slide_layouts[6])
    apply_bg(s8)
    add_clean_header(s8, "Ready for Review: All Deliverables Included")

    deliverables = [
        ("📄 1-Click PDF Report", "Exports an executive audit report with capture stats and security findings ready for submission.", CYAN),
        ("🎓 Viva Cheat Sheet", "Interactive TCP 3-way handshake diagram and 15+ curated viva exam questions with answers.", EMERALD),
        ("🧪 8/8 Automated Tests", "Comprehensive test suite covering endpoints, Scapy parsing, and security rules.", AMBER),
        ("⚡ 1-Click Demo", "Pre-packaged multi-protocol capture with realistic scan patterns to test instantly.", PURPLE),
    ]

    for i, (title, desc, clr) in enumerate(deliverables):
        col = i % 2
        row = i // 2
        left = Inches(0.9 + col * 5.9)
        top = Inches(2.0 + row * 2.4)

        box = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, Inches(5.6), Inches(2.1))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = CARD_BORDER
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = clr

        p_d = tf.add_paragraph()
        p_d.text = f"\n{desc}"
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = TEXT_MAIN

    output_path = Path("Packet_Analysis_Project_Presentation.pptx")
    try:
        prs.save(str(output_path))
    except PermissionError:
        output_path = Path("Packet_Analysis_Presentation_Clean.pptx")
        prs.save(str(output_path))
    print(f"[SUCCESS] Minimalist presentation generated: {output_path.resolve()}")

if __name__ == "__main__":
    create_deck()
