import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import platform

# --- CONFIGURATION ---
LINK = "https://hast-du-zeit.at/"
TEXT = "RFI-IRFOS // 2026"
OUTPUT_FILE = "rfi_qr_final.png"

# --- INPUT PROTOCOL (ROBUST) ---
print("--- RFI-IRFOS QR GENERATOR ---")
raw_input = input("Select Mode [D]ark or [L]ight: ").strip().upper()

# Logic: If 'D' appears anywhere in the input (e.g., "DARK", "d", "Dim"), use Dark Mode.
if "D" in raw_input:
    BG_COLOR = "black"    # Background becomes Void
    FILL_COLOR = "white"  # Data/Text becomes Photonic
    print(f"⚫ MODE SELECTED: DARK (Background: {BG_COLOR}, Text: {FILL_COLOR})")
else:
    BG_COLOR = "white"    # Background becomes Photonic
    FILL_COLOR = "black"  # Data/Text becomes Void
    print(f"⚪ MODE SELECTED: LIGHT (Background: {BG_COLOR}, Text: {FILL_COLOR})")

# --- FONT HUNTER ---
def get_system_font(target_size):
    system = platform.system()
    if system == "Windows":
        candidates = ["C:\\Windows\\Fonts\\arial.ttf", "C:\\Windows\\Fonts\\consola.ttf", "C:\\Windows\\Fonts\\calibri.ttf"]
    elif system == "Darwin": 
        candidates = ["/Library/Fonts/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Courier New.ttf"]
    else: 
        candidates = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"]
    
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, target_size)
    return ImageFont.load_default()

# 1. Generate QR Matrix with DYNAMIC COLORS
# This line was likely the failure point previously if variables weren't passed correctly.
qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=20, border=2)
qr.add_data(LINK)
qr.make(fit=True)

# FORCE the colors into the matrix generation
img = qr.make_image(fill_color=FILL_COLOR, back_color=BG_COLOR).convert('RGB')

# 2. Dimensions & Canvas
width, height = img.size
font_size = int(width * 0.08)
font = get_system_font(font_size)
footer_height = int(font_size * 3)

# 3. Create Canvas (Using BG_COLOR)
new_img = Image.new("RGB", (width, height + footer_height), BG_COLOR)
new_img.paste(img, (0, 0))

# 4. Render Text (Using FILL_COLOR)
draw = ImageDraw.Draw(new_img)
bbox = draw.textbbox((0, 0), TEXT, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

x_pos = (width - text_width) // 2
y_pos = height + (footer_height - text_height) // 2 - (text_height // 4)

draw.text((x_pos, y_pos), TEXT, fill=FILL_COLOR, font=font)
new_img.save(OUTPUT_FILE)

print(f"✅ Success. Generated {OUTPUT_FILE} in requested mode.")
