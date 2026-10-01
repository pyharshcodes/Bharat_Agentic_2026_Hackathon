# 🚀 Jan-Sahayak AI — Apne Friend Ke PC Me Kaise Chalayein

Is project ko apne friend ke laptop ya PC me chalane ke **2 sabse aasan tareeqe** hain:

---

## 🟢 Tareeqa 1: Friend Ke PC Me Run Karna (Sabse Simple — 1 Click)

Apne friend ko bas ye steps follow karne ko bolo:

### Step 1: Project Download Karein
* Ya to **GitHub se clone** karein:
  ```bash
  git clone https://github.com/pyharshcodes/Bharat_Agentic_2026_Hackathon.git
  ```
* Ya fir aap apna poora `Bharat_agentic_hackathon` folder **ZIP banakar** unhe Pen Drive ya WhatsApp/Drive se de dein.

### Step 2: 1-Click Run Karein
* Folder ke andar jayein aur **`START_JAN_SAHAYAK.bat`** file par **Double Click** karein!
* Ye script automatically:
  1. Dependencies (`fastapi`, `uvicorn`, `reportlab`, `gTTS`, etc.) check aur install kar lega.
  2. Server start kar dega.
  3. Browser me automatically `http://127.0.0.1:8000` open kar dega!

*(Note: Friend ke PC me bas Python 3.10+ installed hona chahiye aur install karte waqt "Add Python to PATH" tick hona chahiye).*

---

## 🌐 Tareeqa 2: Friend Ko Bina Kuch Install Karwaye Apne PC Se Live Dikhana (Instant Link)

Agar friend ke paas Python nahi hai aur aap **turant abhi apne laptop se unke PC ya phone par live dikhana chahte hain**:

Aapke laptop par server pehle se chal raha hai. Bas ek naya terminal kholo aur ye 1 line run karo:

```bash
npx localtunnel --port 8000
```
Ya agar `ngrok` hai to:
```bash
ngrok http 8000
```

Aapko ek public link mil jayega (jaise `https://xxxx-xx.loca.lt`). Wo link apne friend ko WhatsApp par bhej do — wo apne phone ya kisi bhi laptop ke browser me khol kar poora Jan-Sahayak live chala sakega!
