# Takht-i-Bahi AI Digital Twin: Augmented Heritage Anastylosis
### *KPITB AI Innovation Challenge 2026 — Official Submission*

[![Live Demo](https://img.shields.io/badge/Demo-Live%20Website-success?style=for-the-badge)](https://danyal-yousafzai.github.io/takht-i-bahi-digital-twin/)
[![UNESCO](https://img.shields.io/badge/UNESCO-World%20Heritage%20Site-blue?style=for-the-badge)](https://whc.unesco.org/en/list/140/)
[![KPITB](https://img.shields.io/badge/Challenge-KPITB%20AI%202026-orange?style=for-the-badge)](https://aichallenge2026.kpitb.online/)

---

## 1. Project Description
**Takht-i-Bahi (Throne of Origins)** in Mardan, Khyber Pakhtunkhwa, is a UNESCO World Heritage site and one of the best-preserved Buddhist monastic complexes of the ancient Gandhara civilization. 

However, after 1,800 years, visitors on-site see only roofless, grey stone schist foundations. Because international UNESCO preservation charters (the *Venice Charter 1964*) strictly forbid physically rebuilding on ancient ruins, digital reconstruction is the only legally and ethically permissible method to restore the monument.

The **Takht-i-Bahi AI Digital Twin** is a zero-install WebAR and 3D spatial platform. By scanning or visiting the site, an interactive **Time-Warp Slider (2026 Ruins ◄────────► 2nd Century CE)** allows users to seamlessly watch the ancient monastery rise over the physical ruins with millimeter accuracy—revealing the monumental 10-meter central stupa, five tiered honorific umbrellas (*chattras*), barrel-vaulted chapels, and golden Buddha statues in their original Kushan-era architectural glory.

---

## 2. Key Features
1. **Interactive Time-Warp Anastylosis:** Smooth real-time GPU cross-fade dissolving between present-day stone ruins and the 2nd-century CE reconstructed Stupa Court.
2. **Dual Viewing Modes:**
   - **3D Orbit Mode:** Interactive 360° inspection with touch and mouse controls, designed for remote exploration and evaluation.
   - **Live AR Mode:** Real-world camera pass-through (`getUserMedia`) with device gyroscope tracking (`DeviceOrientationEvent`) to project the past onto the physical ruins.
3. **PBR Triplanar Photographic Textures:** Mapped authentic high-resolution field photographs of Takht-i-Bahi's unique **Gandharan diaper masonry** across the ruins with ambient cavity occlusion.
4. **Trilingual Neural Voice Narration:** Complete interface and audio narration in **English**, **Urdu (اردو)**, and **Pashto (پښتو)** with native Noto Nastaliq typography.
5. **Tourist Souvenir Photo Generator:** 1-click high-resolution watermarked screenshot capture for social media sharing.
6. **Zero-Install Client-Side Web Architecture:** Runs at 60 FPS in standard mobile browsers without requiring app store downloads.

---

## 3. Technology Stack & Architecture
- **3D Processing & Computer Vision:** Python 3.13, `trimesh`, `numpy`, `scipy`, `pillow`
- **Real-Time 3D Rendering:** Three.js (WebGL 2.0), GLTFLoader, OrbitControls
- **Custom Shaders:** GLSL (OpenGL Shading Language) — Triplanar normal projection and spatial court-bounding fade shader
- **Augmented Reality:** Web MediaDevices API, DeviceOrientation SLAM tracking
- **Voice AI:** Microsoft Edge Neural TTS / gTTS (`ur-PK-AsadNeural`, `ps-AF-GulNawazNeural`, `en-GB-RyanNeural`)
- **Hosting & CI/CD:** GitHub Pages, Git static pipeline

---

## 4. Setup & Running Instructions

### Prerequisites
- Python 3.10+ installed
- Modern web browser (Chrome, Edge, Safari, Firefox)

### Installation
1. Clone or extract the repository:
   ```bash
   cd takht-i-bahi-digital-twin
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
1. Start the local development web server:
   ```bash
   python -m http.server 8000
   ```
   *(Or double-click `RUN_WEB_APP.bat` on Windows)*.
2. Open your web browser and navigate to:
   ```
   http://localhost:8000
   ```

### Running Mobile Live AR Mode
Connect your smartphone to the same local Wi-Fi network and open:
```
http://<YOUR_LOCAL_IP>:8000
```
*(Or use the official live production link: https://danyal-yousafzai.github.io/takht-i-bahi-digital-twin/)*

---

## 5. Dataset & Photogrammetry Information
- **Source Photogrammetry Data:** Ground and aerial multi-view photogrammetry of the Takht-i-Bahi Main Stupa Court (EPSG:32642, UTM 42N).
- **Coordinate Reference:** Re-centered to local origin `(0, 0, 0)` from UTM coordinates (`771,275m E, 3,797,809m N, 402m Elevation`) to eliminate 32-bit GPU floating-point precision jitter.
- **Mesh Optimization:** Curvature-aware Quadric Error Metrics (QEM) decimation reducing 1,136,838 triangles (142 MB) to 135,706 faces (3.5 MB GLB).

---

## 6. Login Credentials
**None required.** The application is completely public, client-side, and accessible without login gates or authentication credentials.

---

## 7. Submission Details
- **Competition:** KPITB AI Innovation Challenge 2026
- **Live Production URL:** [https://danyal-yousafzai.github.io/takht-i-bahi-digital-twin/](https://danyal-yousafzai.github.io/takht-i-bahi-digital-twin/)
- **Repository:** [https://github.com/danyal-yousafzai/takht-i-bahi-digital-twin](https://github.com/danyal-yousafzai/takht-i-bahi-digital-twin)
