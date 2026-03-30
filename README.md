# Moa-Skeleton

A web application that overlays moa-bone collection statuses onto an uploaded
skeleton diagram figure.

## Features

- Upload any image (PNG, JPEG, GIF, BMP, TIFF, WebP) as the skeleton diagram.
- Edit the quantity in stock and status (Missing / Found / Partial) for each of
  the 18 bone groups.
- Download the original figure with a colour-coded status panel appended to the
  right side.

## Bone groups

| Element ID | Category   | Description / Presumed Bone               |
|-----------|------------|-------------------------------------------|
| 1–7       | Skull      | Cranium and Mandible                      |
| 8–24      | Axial      | Cervical Vertebrae (Neck)                 |
| 25–35     | Axial      | Thoracic / Synsacrum Vertebrae (Back)     |
| 36–43     | Ribs       | Right Ribs                                |
| 44–51     | Ribs       | Left Ribs                                 |
| 52–54     | Sternum    | Sternum / Breastbone elements             |
| 55–57     | Pelvis     | Ilium, Ischium, Pubis (Pelvic Girdle)     |
| 58        | Right Leg  | Right Femur                               |
| 59        | Right Leg  | Right Tibiotarsus                         |
| 60        | Right Leg  | Right Fibula                              |
| 61        | Right Leg  | Right Tarsometatarsus                     |
| 62–76     | Right Foot | Right Phalanges (Toes/Claws)              |
| 77        | Pelvis     | Caudal Vertebrae (Tail)                   |
| 78        | Left Leg   | Left Femur                                |
| 79        | Left Leg   | Left Tibiotarsus                          |
| 80        | Left Leg   | Left Fibula                               |
| 81        | Left Leg   | Left Tarsometatarsus                      |
| 82–96     | Left Foot  | Left Phalanges (Toes/Claws)               |

## Running locally

```bash
pip install -r requirements.txt
python app.py
```

Then open <http://localhost:5000> in your browser.
