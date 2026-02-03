# RFI-IRFOS // **QR-FORGE**

**Version:** 1.0.1
**State:** Stable
**Origin:** RFI-IRFOS (Graz, Austria)

---

## ⚠️ The Problem

Most QR generators commit the **static-integer fallacy**:

They pick a fixed font size (e.g., *20px*) and call it a day — **regardless of QR matrix density**.

So when you scale the QR for print or high-res displays, the code grows… but the caption stays microscopic.
Result: the “human-readable anchor” becomes decorative noise, and your visual hierarchy collapses.

---

## 🛠️ The Solution

**QR-Forge rejects static values.**

It enforces **ratio-based typography**.

Font size is dynamically computed as a function of the matrix width:

> **Font = Width × 0.08**

Meaning: your label maintains **ontological prominence** no matter the output resolution.

---

##  Capabilities

###  Phase-Shift Protocol

Native support for:

* **Void (Dark)** state
* **Photonic (Light)** state

User input determines the **binary collapse** of the output.

###  System Agnostic

The script autonomously hunts for valid **fixed-width / sans-serif `.ttf` binaries** on the host OS:

* Windows
* Linux
* Darwin

No more illegible PIL raster defaults.

###  H-Level Redundancy

Hardcoded to **ERROR_CORRECT_H (30%)**.
We sacrifice density for durability — because reality is hostile.

### 🧠 Neurosymbolic Alignment

Text is mathematically centered using **bounding-box calculations**.
No vibes. No guessed offsets. Pure geometry.

---

##  Deployment

### 1) Dependencies

```bash
pip install -r requirements.txt
```

### 2) Execution

Run the forge. The system will interrogate you for the desired state.

```bash
python qr_forge.py
```

### 3) Inputs

**Prompt:** `Select Mode [D]ark or [L]ight`

**Triggers:**

* `D`, `d`, `Dark`, `Void` → **Dark Mode** *(Black background, white data)*
* `L`, `l`, `Light` → **Light Mode** *(White background, black data)*

---

##  Configuration

Edit `qr_forge.py` and set your target anchor:

```python
LINK = "https://hast-du-zeit.at/"
TEXT = "RFI-IRFOS // 2026"
```

---

##  Signature

Built by the **Research Focus Institute (RFI-IRFOS)**.

> We fix what the industry ignores.
