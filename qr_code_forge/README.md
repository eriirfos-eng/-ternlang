RFI-IRFOS // QR-Forge (Binary State)

Status: Active // Version: 1.0.0 // License: MIT

"Legibility is not a suggestion; it is an ontological requirement." — RFI Directive

Overview

QR-Forge is a neurosymbolic artifact generation tool developed by the Research Focus Institute (RFI-IRFOS). Unlike standard generators that treat typography as a static afterthought, QR-Forge utilizes a dynamic scaling algorithm that binds font size to the matrix density. This ensures that the human-readable anchor (the text) remains ontologically distinct and legible regardless of the resolution or "box size" of the QR code.

The system operates in two binary states—Photonic (Light) and Void (Dark)—allowing for seamless integration into diverse aesthetic ecosystems without compromising scan redundancy.

Core Capabilities

Binary State Collapse: User-defined input triggers a phase shift between Dark Mode (White Data/Black Void) and Light Mode (Black Data/White Void).

Dynamic Scaling Logic: Font size is calculated as a fixed percentage (8%) of the total matrix width, eliminating "tiny text" errors on high-resolution renders.

System Font Hunter: The script autonomously scans the host OS (Windows, MacOS, Linux) for valid fixed-width or sans-serif .ttf files, preventing the degradation of the visual output to default bitmap fonts.

High Redundancy: Default configuration uses Level H (30%) error correction to maintain functional integrity even in damaged environments.

Installation

Clone the Repository

git clone [https://github.com/RFI-IRFOS/qr-forge.git](https://github.com/RFI-IRFOS/qr-forge.git)
cd qr-forge


Install Dependencies
We rely on pillow for the canvas manipulation and qrcode for the matrix logic.

pip install -r requirements.txt


Usage Protocol

Execute the forge via the terminal. The system will request a state selection before collapsing the wavefunction.

python qr_forge.py


Interaction Flow:

Initiate: Script launches.

Select State: Enter D (Dark) or L (Light).

Process: The system locates a valid font, generates the matrix, and fuses the layers.

Artifact: Output saved as rfi_qr_final.png.

Configuration

Target variables are located in the CONFIGURATION block of qr_forge.py:

LINK = "[https://hast-du-zeit.at/](https://hast-du-zeit.at/)"   # Target URL
TEXT = "RFI-IRFOS // 2026"           # Human-Readable Anchor


Developed by RFI-IRFOS (Graz, Austria). We build the tools that others forgot to engineer.
