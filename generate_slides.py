from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1920, 1080
DARK   = (13, 13, 13)
CARD   = (22, 22, 22)
BLUE   = (30, 144, 255)
WHITE  = (240, 240, 240)
MUTED  = (136, 136, 136)
BORDER = (42, 42, 42)

OUT = "/home/user/Claude-bot/slides"
os.makedirs(OUT, exist_ok=True)

def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def new_slide():
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img)
    return img, d

def tag(d, text, y):
    f = get_font(22)
    d.text((W//2, y), text.upper(), font=f, fill=BLUE, anchor="mm")

def title(d, lines, y, size=72):
    f = get_font(size, bold=True)
    for i, line in enumerate(lines):
        parts = line.split("||")  # "||" = blue segment
        total_w = sum(d.textlength(p, font=f) for p in parts)
        x = W//2 - total_w//2
        for j, part in enumerate(parts):
            color = BLUE if j % 2 == 1 else WHITE
            d.text((x, y + i * (size + 10)), part, font=f, fill=color, anchor="lm")
            x += d.textlength(part, font=f)

def subtitle(d, text, y, color=MUTED, size=28):
    f = get_font(size)
    # word wrap
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = cur + " " + w if cur else w
        if d.textlength(test, font=f) < W - 300:
            cur = test
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    for i, line in enumerate(lines):
        d.text((W//2, y + i * 38), line, font=f, fill=color, anchor="mm")
    return y + len(lines) * 38

def divider(d, y):
    d.rectangle([(W//2 - 40, y), (W//2 + 40, y + 4)], fill=BLUE)

def rounded_rect(d, x1, y1, x2, y2, r=16, fill=CARD, outline=BORDER, width=1):
    d.rounded_rectangle([(x1, y1), (x2, y2)], radius=r, fill=fill, outline=outline, width=width)

def blue_line_card(d, x1, y1, x2, y2):
    d.rounded_rectangle([(x1, y1), (x2, y2)], radius=12, fill=CARD, outline=CARD)
    d.rectangle([(x1, y1+12), (x1+4, y2-12)], fill=BLUE)

def stat_box(d, cx, y, num, lbl):
    bw, bh = 230, 130
    rounded_rect(d, cx-bw//2, y, cx+bw//2, y+bh, fill=CARD, outline=BORDER)
    nf = get_font(52, bold=True)
    lf = get_font(20)
    d.text((cx, y+42), num, font=nf, fill=BLUE, anchor="mm")
    d.text((cx, y+100), lbl.upper(), font=lf, fill=MUTED, anchor="mm")

def wrap_text(d, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = cur + " " + w if cur else w
        if d.textlength(test, font=font) < max_w:
            cur = test
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def draw_text_block(d, text, x, y, max_w, size=24, color=MUTED, center=False):
    f = get_font(size)
    lines = wrap_text(d, text, f, max_w)
    for i, line in enumerate(lines):
        anchor = "mm" if center else "lm"
        tx = x if not center else x + max_w//2
        d.text((tx, y + i*34), line, font=f, fill=color, anchor=anchor)
    return y + len(lines)*34

# ── SLIDE 1: COVER ──────────────────────────────────────────────────────────
img, d = new_slide()
# background gradient tint (top-right blue glow)
for i in range(400):
    alpha = int(60 * (1 - i/400))
    d.ellipse([(W-500-i, -200-i//2), (W+200+i, 600+i//2)], fill=(10, 42, 74))

# circle logo
cx, cy = W//2, 280
d.ellipse([(cx-70, cy-70), (cx+70, cy+70)], outline=BLUE, width=4)
lf = get_font(54, bold=True)
d.text((cx, cy), "F", font=lf, fill=WHITE, anchor="mm")

tag(d, "Marketing Proposal", 390)
title(d, ["Accelerating ||Faded|| Automotive's", "Growth"], 430, size=78)
divider(d, 640)
subtitle(d, "Elland, West Yorkshire  ·  Vehicle Customisation Specialists", 668, color=MUTED, size=26)
subtitle(d, "A tailored digital marketing strategy to expand your reach, attract premium clients, and build lasting brand authority.", 720, color=(180,180,180), size=26)

img.save(f"{OUT}/slide_01_cover.png")
print("Slide 1 done")

# ── SLIDE 2: ABOUT ──────────────────────────────────────────────────────────
img, d = new_slide()
tag(d, "About Faded Automotive", 100)
title(d, ["A Trusted Name in Vehicle", "||Customisation||"], 150, size=68)
subtitle(d, "Based in Elland HX50PA, Faded Automotive has built a loyal local following through exceptional craftsmanship and an unmatched portfolio of premium vehicle services.", 360, color=(180,180,180), size=26)

stats = [("697","Facebook Followers"),("98%","Recommendation Rate"),("27","5-Star Reviews"),("9+","Core Services")]
positions = [W//2 - 390, W//2 - 130, W//2 + 130, W//2 + 390]
for cx, (num, lbl) in zip(positions, stats):
    stat_box(d, cx, 500, num, lbl)

img.save(f"{OUT}/slide_02_about.png")
print("Slide 2 done")

# ── SLIDE 3: SERVICES ───────────────────────────────────────────────────────
img, d = new_slide()
tag(d, "Service Portfolio", 80)
title(d, ["Everything Under ||One Roof||"], 130, size=68)

services = [
    ("🚗", "Vehicle Wrapping"), ("✏", "Sign Writing & Branding"), ("🪟", "Window Tinting"),
    ("🌈", "Chameleon Windscreen"), ("💡", "Light Tinting"), ("✨", "Valeting & Detailing"),
    ("🛡", "Ceramic Coatings"), ("🏷", "Fleet & Commercial"), ("⭐", "Premium Finishes"),
]
cols, rows = 3, 3
cw, ch = 500, 140
sx = (W - cols*cw - (cols-1)*20)//2
sy = 280
tf = get_font(26, bold=True)
for i, (icon, name) in enumerate(services):
    col, row = i % cols, i // cols
    x1 = sx + col*(cw+20)
    y1 = sy + row*(ch+16)
    rounded_rect(d, x1, y1, x1+cw, y1+ch, fill=CARD, outline=BORDER)
    d.text((x1+30, y1+ch//2-10), icon, font=get_font(36), fill=WHITE, anchor="lm")
    d.text((x1+90, y1+ch//2), name, font=tf, fill=WHITE, anchor="lm")

img.save(f"{OUT}/slide_03_services.png")
print("Slide 3 done")

# ── SLIDE 4: OPPORTUNITY ────────────────────────────────────────────────────
img, d = new_slide()
tag(d, "The Opportunity", 80)
title(d, ["You Have the Quality —", "Let's Build the ||Visibility||"], 130, size=62)

opps = [
    ("Growing Market", "The UK vehicle customisation market is expanding rapidly. Premium wraps & ceramic coatings are increasingly sought after by private and commercial clients."),
    ("Untapped Audience", "With only 697 followers, there is massive headroom for social growth. Your 98% recommendation rate is a powerful asset waiting to be amplified."),
    ("Low Competition Online", "Most local competitors lack strong digital presence. A focused SEO & content strategy can position Faded Automotive as the go-to brand in West Yorkshire."),
    ("Visual-First Services", "Wraps, tints, and detailing are inherently visual — perfectly suited to Instagram, TikTok, and YouTube content that converts viewers into paying customers."),
]
cw, ch = 840, 200
sx = (W - 2*cw - 30)//2
sy = 360
hf = get_font(26, bold=True)
bf = get_font(22)
for i, (heading, body) in enumerate(opps):
    col, row = i % 2, i // 2
    x1 = sx + col*(cw+30)
    y1 = sy + row*(ch+20)
    blue_line_card(d, x1, y1, x1+cw, y1+ch)
    d.text((x1+24, y1+36), heading.upper(), font=hf, fill=BLUE, anchor="lm")
    draw_text_block(d, body, x1+24, y1+70, cw-40, size=22, color=(180,180,180))

img.save(f"{OUT}/slide_04_opportunity.png")
print("Slide 4 done")

# ── SLIDE 5: STRATEGY ───────────────────────────────────────────────────────
img, d = new_slide()
tag(d, "Our Strategy", 70)
title(d, ["A ||4-Pillar|| Growth Plan"], 120, size=68)

strats = [
    ("01", "Social Media Growth", "Consistent, high-quality Reels and TikToks showcasing before/after transformations, time-lapses, and client reactions — turning your work into viral content."),
    ("02", "Paid Advertising", "Targeted Meta and Google Ads campaigns reaching car enthusiasts, fleet managers, and businesses in West Yorkshire actively searching for your services."),
    ("03", "SEO & Google Business", "Optimise your Google Business profile and build local SEO authority so Faded Automotive appears first for 'window tinting Elland' or 'car wrap West Yorkshire'."),
    ("04", "Review & Reputation Management", "Systematic post-job review requests to push your count from 27 to 100+ — making your 98% rating impossible to ignore and converting browsers into bookings."),
]
item_h = 148
sy = 260
nf = get_font(52, bold=True)
hf = get_font(28, bold=True)
bf = get_font(22)
iw = W - 300
ix = 150
for num, heading, body in strats:
    rounded_rect(d, ix, sy, ix+iw, sy+item_h, fill=CARD, outline=BORDER)
    d.text((ix+36, sy+item_h//2), num, font=nf, fill=BLUE, anchor="lm")
    d.text((ix+120, sy+30), heading, font=hf, fill=WHITE, anchor="lm")
    draw_text_block(d, body, ix+120, sy+68, iw-140, size=22, color=(170,170,170))
    sy += item_h + 14

img.save(f"{OUT}/slide_05_strategy.png")
print("Slide 5 done")

# ── SLIDE 6: PACKAGES ───────────────────────────────────────────────────────
img, d = new_slide()
tag(d, "What We Deliver", 70)
title(d, ["Choose Your ||Growth Package||"], 120, size=68)

packages = [
    ("Starter", False, ["Google Business Optimisation","12 Social Posts / Month","Monthly Performance Report","Review Request System"]),
    ("Growth", True,  ["Everything in Starter","Meta & Google Ads Management","4 Short-Form Videos / Month","SEO Content Strategy","Bi-weekly Strategy Calls","Lead Tracking Dashboard"]),
    ("Premium", False,["Everything in Growth","Full Brand Identity Refresh","Website Design & Build","8 Videos / Month + Editing","Influencer Collaboration","Weekly Strategy Calls"]),
]
cw, ch = 520, 560
sx = (W - 3*cw - 40)//2
sy = 260
hf = get_font(32, bold=True)
lf = get_font(22)
bf = get_font(18)
for i, (name, featured, items) in enumerate(packages):
    x1 = sx + i*(cw+20)
    fill = (10,26,46) if featured else CARD
    outline = BLUE if featured else BORDER
    rounded_rect(d, x1, sy, x1+cw, sy+ch, fill=fill, outline=outline, width=2 if featured else 1)
    if featured:
        badge_text = "RECOMMENDED"
        bw = int(d.textlength(badge_text, font=lf)) + 30
        bx = x1 + cw//2 - bw//2
        d.rounded_rectangle([(bx, sy-16), (bx+bw, sy+16)], radius=10, fill=BLUE)
        d.text((x1+cw//2, sy), badge_text, font=lf, fill=WHITE, anchor="mm")
    d.text((x1+cw//2, sy+50), name, font=hf, fill=WHITE, anchor="mm")
    ly = sy + 100
    for item in items:
        d.text((x1+30, ly+12), "✓", font=lf, fill=BLUE, anchor="lm")
        d.text((x1+60, ly+12), item, font=bf, fill=(180,180,180), anchor="lm")
        d.line([(x1+20, ly+36), (x1+cw-20, ly+36)], fill=(40,40,40), width=1)
        ly += 44

img.save(f"{OUT}/slide_06_packages.png")
print("Slide 6 done")

# ── SLIDE 7: RESULTS ────────────────────────────────────────────────────────
img, d = new_slide()
tag(d, "Projected Results — 6 Months", 100)
title(d, ["What ||Growth|| Looks Like"], 150, size=72)
subtitle(d, "Based on comparable automotive businesses in the UK, here are realistic targets with a consistent Growth package strategy.", 310, color=(180,180,180), size=26)

results = [("3×","Social Following"),("+60%","Website Traffic"),("100+","Google Reviews"),("Top 3","Local SEO Ranking")]
rw, rh = 360, 200
rx = (W - 4*rw - 3*30)//2
ry = 420
vf = get_font(68, bold=True)
lf2 = get_font(22)
for val, lbl in results:
    rounded_rect(d, rx, ry, rx+rw, ry+rh, fill=CARD, outline=BORDER)
    d.text((rx+rw//2, ry+80), val, font=vf, fill=BLUE, anchor="mm")
    d.text((rx+rw//2, ry+150), lbl.upper(), font=lf2, fill=MUTED, anchor="mm")
    rx += rw + 30

img.save(f"{OUT}/slide_07_results.png")
print("Slide 7 done")

# ── SLIDE 8: WHY US ─────────────────────────────────────────────────────────
img, d = new_slide()
tag(d, "Why Work With Us", 80)
title(d, ["Marketing That Understands ||Automotive||"], 130, size=62)

why = [
    ("🎯","Niche Expertise","We specialise in trades and automotive businesses — we know what content converts and what audiences want to see."),
    ("📊","Data-Driven","Every decision is backed by analytics. We track leads, cost-per-booking, and ROI — not just likes and impressions."),
    ("🤝","Transparent Partnership","No lock-in contracts, no hidden fees. Regular calls, clear reporting, and a team that genuinely cares about your growth."),
    ("⚡","Fast Execution","We hit the ground running. Onboarding in 48 hours, first content live within 7 days of sign-up."),
]
cw, ch = 820, 200
sx = (W - 2*cw - 30)//2
sy = 340
icf = get_font(44)
hf  = get_font(28, bold=True)
bf  = get_font(22)
for i, (ico, heading, body) in enumerate(why):
    col, row = i % 2, i // 2
    x1 = sx + col*(cw+30)
    y1 = sy + row*(ch+20)
    rounded_rect(d, x1, y1, x1+cw, y1+ch, fill=CARD, outline=BORDER)
    d.text((x1+30, y1+ch//2-10), ico, font=icf, fill=WHITE, anchor="lm")
    d.text((x1+100, y1+40), heading, font=hf, fill=WHITE, anchor="lm")
    draw_text_block(d, body, x1+100, y1+80, cw-120, size=22, color=(170,170,170))

img.save(f"{OUT}/slide_08_why.png")
print("Slide 8 done")

# ── SLIDE 9: CTA ────────────────────────────────────────────────────────────
img, d = new_slide()
# blue glow
for i in range(350):
    d.ellipse([(-100-i, H-400-i//2), (700+i, H+100+i//2)], fill=(10,42,74))

tag(d, "Let's Get Started", 180)
title(d, ["Ready to Take ||Faded Automotive||", "to the Next Level?"], 240, size=68)
subtitle(d, "Book a free 30-minute strategy call and we'll show you exactly how we'd grow your business — no commitment, no fluff.", 470, color=(180,180,180), size=26)

# CTA button
bw, bh = 420, 70
bx, by = W//2 - bw//2, 560
d.rounded_rectangle([(bx, by), (bx+bw, by+bh)], radius=35, fill=BLUE)
d.text((W//2, by+bh//2), "Book a Free Strategy Call", font=get_font(28, bold=True), fill=WHITE, anchor="mm")

# contact row
contacts = [("Location","Elland, West Yorkshire HX50PA"),("Facebook","Faded Automotive"),("Rating","98% Recommended ⭐")]
cx_positions = [W//2 - 480, W//2, W//2 + 480]
lf3 = get_font(22)
vf3 = get_font(24, bold=True)
for cx, (lbl, val) in zip(cx_positions, contacts):
    d.text((cx, 710), lbl, font=lf3, fill=MUTED, anchor="mm")
    d.text((cx, 746), val, font=vf3, fill=WHITE, anchor="mm")

img.save(f"{OUT}/slide_09_cta.png")
print("Slide 9 done")

print(f"\nAll 9 slides saved to {OUT}/")
