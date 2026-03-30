import io
import os

from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
MAX_UPLOAD_MB = 16
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "tiff", "webp"}

DEFAULT_BONES = [
    {"id": "1-7",   "category": "Skull",      "description": "Cranium and Mandible",                  "quantity": 0, "status": "Missing"},
    {"id": "8-24",  "category": "Axial",      "description": "Cervical Vertebrae (Neck)",             "quantity": 0, "status": "Missing"},
    {"id": "25-35", "category": "Axial",      "description": "Thoracic / Synsacrum Vertebrae (Back)", "quantity": 0, "status": "Missing"},
    {"id": "36-43", "category": "Ribs",       "description": "Right Ribs",                            "quantity": 0, "status": "Missing"},
    {"id": "44-51", "category": "Ribs",       "description": "Left Ribs",                             "quantity": 0, "status": "Missing"},
    {"id": "52-54", "category": "Sternum",    "description": "Sternum / Breastbone elements",         "quantity": 0, "status": "Missing"},
    {"id": "55-57", "category": "Pelvis",     "description": "Ilium, Ischium, Pubis (Pelvic Girdle)", "quantity": 0, "status": "Missing"},
    {"id": "58",    "category": "Right Leg",  "description": "Right Femur",                           "quantity": 0, "status": "Missing"},
    {"id": "59",    "category": "Right Leg",  "description": "Right Tibiotarsus",                     "quantity": 0, "status": "Missing"},
    {"id": "60",    "category": "Right Leg",  "description": "Right Fibula",                          "quantity": 0, "status": "Missing"},
    {"id": "61",    "category": "Right Leg",  "description": "Right Tarsometatarsus",                 "quantity": 0, "status": "Missing"},
    {"id": "62-76", "category": "Right Foot", "description": "Right Phalanges (Toes/Claws)",          "quantity": 0, "status": "Missing"},
    {"id": "77",    "category": "Pelvis",     "description": "Caudal Vertebrae (Tail)",               "quantity": 0, "status": "Missing"},
    {"id": "78",    "category": "Left Leg",   "description": "Left Femur",                            "quantity": 0, "status": "Missing"},
    {"id": "79",    "category": "Left Leg",   "description": "Left Tibiotarsus",                      "quantity": 0, "status": "Missing"},
    {"id": "80",    "category": "Left Leg",   "description": "Left Fibula",                           "quantity": 0, "status": "Missing"},
    {"id": "81",    "category": "Left Leg",   "description": "Left Tarsometatarsus",                  "quantity": 0, "status": "Missing"},
    {"id": "82-96", "category": "Left Foot",  "description": "Left Phalanges (Toes/Claws)",           "quantity": 0, "status": "Missing"},
]


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_bones_from_form(form):
    """Parse bone quantity and status values submitted from the form."""
    bones = []
    for i, bone in enumerate(DEFAULT_BONES):
        quantity = form.get(f"quantity_{i}", "0")
        try:
            quantity = int(quantity)
        except ValueError:
            quantity = 0
        status = form.get(f"status_{i}", bone["status"])
        bones.append({**bone, "quantity": quantity, "status": status})
    return bones


def _get_status_colour(status):
    """Return an RGB colour tuple for a given bone status string."""
    status_lower = status.strip().lower()
    if status_lower == "missing":
        return (220, 53, 69)    # Bootstrap danger red
    if status_lower == "found":
        return (40, 167, 69)    # Bootstrap success green
    if status_lower == "partial":
        return (255, 193, 7)    # Bootstrap warning amber
    return (108, 117, 125)      # Bootstrap secondary grey


def annotate_image(image_bytes, bones):
    """
    Overlay a bone-status legend panel on the right-hand side of the
    uploaded figure and return the annotated image as PNG bytes.
    """
    original = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    orig_w, orig_h = original.size

    # --- Panel dimensions ---
    padding = 12
    row_height = 22
    font_size = 14
    panel_width = 420
    header_height = 30
    panel_height = len(bones) * row_height + padding * 3 + header_height

    # Try to load a basic font; fall back to the Pillow default if unavailable.
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except (OSError, IOError):
        font = ImageFont.load_default()
        font_bold = font

    # Create panel image
    panel = Image.new("RGBA", (panel_width, max(orig_h, panel_height)), (255, 255, 255, 230))
    draw = ImageDraw.Draw(panel)

    # Header
    draw.rectangle([0, 0, panel_width, header_height + padding], fill=(52, 58, 64, 255))
    draw.text((padding, padding // 2 + 4), "Moa Bone Collection Status", font=font_bold, fill=(255, 255, 255, 255))

    # Column headers
    y = header_height + padding * 2
    draw.text((padding, y), "ID", font=font_bold, fill=(0, 0, 0, 255))
    draw.text((padding + 55, y), "Description", font=font_bold, fill=(0, 0, 0, 255))
    draw.text((padding + 270, y), "Qty", font=font_bold, fill=(0, 0, 0, 255))
    draw.text((padding + 310, y), "Status", font=font_bold, fill=(0, 0, 0, 255))
    y += row_height

    # Bone rows
    for idx, bone in enumerate(bones):
        bg_colour = (245, 245, 245, 255) if idx % 2 == 0 else (255, 255, 255, 255)
        draw.rectangle([0, y - 2, panel_width, y + row_height - 4], fill=bg_colour)

        status_colour = _get_status_colour(bone["status"]) + (255,)
        # Coloured dot
        dot_r = 5
        cx = padding + dot_r
        cy = y + row_height // 2 - 6
        draw.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=status_colour)

        draw.text((padding + 14, y), bone["id"], font=font, fill=(0, 0, 0, 255))
        # Truncate long descriptions to fit column, adding ellipsis if needed
        max_desc_chars = 28
        desc = bone["description"]
        if len(desc) > max_desc_chars:
            desc = desc[:max_desc_chars - 1] + "…"
        draw.text((padding + 55, y), desc, font=font, fill=(0, 0, 0, 255))
        draw.text((padding + 270, y), str(bone["quantity"]), font=font, fill=(0, 0, 0, 255))
        draw.text((padding + 310, y), bone["status"], font=font, fill=status_colour)
        y += row_height

    # Compose: place original on the left, panel on the right
    total_width = orig_w + panel_width
    total_height = max(orig_h, panel_height)
    composite = Image.new("RGBA", (total_width, total_height), (255, 255, 255, 255))
    composite.paste(original, (0, (total_height - orig_h) // 2))
    composite.paste(panel, (orig_w, 0), panel)

    output = io.BytesIO()
    composite.convert("RGB").save(output, format="PNG")
    output.seek(0)
    return output


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", bones=DEFAULT_BONES,
                           statuses=["Missing", "Found", "Partial"],
                           max_upload_mb=MAX_UPLOAD_MB)


@app.route("/annotate", methods=["POST"])
def annotate():
    if "figure" not in request.files:
        return render_template("index.html", bones=DEFAULT_BONES,
                               statuses=["Missing", "Found", "Partial"],
                               max_upload_mb=MAX_UPLOAD_MB,
                               error="No figure file was included in the upload.")

    file = request.files["figure"]
    if file.filename == "":
        return render_template("index.html", bones=DEFAULT_BONES,
                               statuses=["Missing", "Found", "Partial"],
                               max_upload_mb=MAX_UPLOAD_MB,
                               error="Please select a figure file before submitting.")

    if not allowed_file(file.filename):
        return render_template("index.html", bones=DEFAULT_BONES,
                               statuses=["Missing", "Found", "Partial"],
                               max_upload_mb=MAX_UPLOAD_MB,
                               error="Unsupported file type. Please upload a PNG, JPEG, GIF, BMP, TIFF, or WebP image.")

    image_bytes = file.read()
    bones = parse_bones_from_form(request.form)

    try:
        annotated = annotate_image(image_bytes, bones)
    except Image.UnidentifiedImageError:
        return render_template("index.html", bones=bones,
                               statuses=["Missing", "Found", "Partial"],
                               max_upload_mb=MAX_UPLOAD_MB,
                               error="The uploaded file could not be identified as a valid image.")
    except (OSError, IOError) as exc:
        return render_template("index.html", bones=bones,
                               statuses=["Missing", "Found", "Partial"],
                               max_upload_mb=MAX_UPLOAD_MB,
                               error=f"Could not read or process image: {exc}")

    return send_file(annotated, mimetype="image/png",
                     as_attachment=True, download_name="moa_skeleton_annotated.png")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
