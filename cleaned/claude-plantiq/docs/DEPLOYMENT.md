# Running the server and connecting the app

## 1. Laptop on the farm Wi-Fi (simplest)
```bash
scripts\run_backend.bat          # Windows
./scripts/run_backend.sh         # Linux / macOS
```
First run creates `backend/.venv`, installs dependencies, copies `.env.example` → `.env`, builds the web UI and stores the RAG
models as safetensors. Put your `GEMINI_API_KEY` and/or `GROQ_API_KEY` into `backend/.env` (without them the app uses its
built-in offline guide). The console prints:
```
Phone:   http://192.168.1.15:8000   ← enter this in the app's Server settings
```
Allow Python through the Windows firewall for **private** networks when prompted. Port in use? `set PORT=8010` first.

## 2. Install the APK
Copy `dist/PlantIQ.apk` (or `release/PlantIQ-3.0.0.apk`) to the phone and open it (allow "install unknown apps").
On first launch the app asks for the server address — type the `Phone:` address, press **Test**, then **Continue**.
Change it any time from the server button (top bar) or Profile → Server. Nothing is baked into the APK.

Rebuild after changes: `python scripts/build_apk.py` (needs Node 20+, JDK 17+, Android SDK).

## 3. Cloud / VM (HTTPS)
```bash
docker build -t plantiq-backend -f backend/Dockerfile .
docker run -d --gpus all -p 8000:8000 --env-file backend/.env -e ENV=production \
  -e SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(48))") \
  -v plantiq-var:/app/backend/var plantiq-backend
```
Put Caddy/nginx in front for TLS and set `TRUST_PROXY_HEADERS=true`. Use `DATABASE_URL=postgresql+psycopg2://…` for Postgres.
In the app enter `https://your-domain`. A quick public URL for testing: `cloudflared tunnel --url http://localhost:8000`.

## 4. Release signing
```bash
keytool -genkey -v -keystore plantiq.jks -alias plantiq -keyalg RSA -keysize 2048 -validity 10000
python scripts/build_apk.py --release
apksigner sign --ks plantiq.jks --out PlantIQ-signed.apk dist/PlantIQ-release-unsigned.apk
```

## Configuration
All settings are environment variables documented in `backend/.env.example` (database, LLM keys, RAG profile, STT toggles,
rate limits, CORS). `RAG_PROFILE=auto` picks bge-m3 + bge-reranker-v2-m3 on a ≥6 GB GPU and bge-base + MiniLM otherwise.
