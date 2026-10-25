# Feature parity matrix

Every behaviour found in the original app (`../backend`, `../frontend`, `../mobile`) has an ID here.
Status: ⬜ not started · 🟨 in progress · ✅ done (implemented + tested). "Where" points at the rebuild. All rows done as of 2026-10-25.

## A. Leaf scanner & diagnosis
| ID | Feature (original) | Status | Where |
|---|---|---|---|
| A1 | Tap to take photo / upload image (camera capture on mobile) | ✅ | `screens/Scanner.tsx` |
| A2 | Image preview with remove button | ✅ | Scanner |
| A3 | ResNet-50 classification with the original weights, 5 classes, 224×224 ImageNet norm | ✅ | `services/cnn.py` |
| A4 | Confidence % + confidence bar | ✅ | `components/DiagnosisCard.tsx` |
| A5 | Per-class probability distribution grid | ✅ | DiagnosisCard |
| A6 | Healthy / disease badge | ✅ | DiagnosisCard |
| A7 | "Blended advisory" low-confidence notice (CNN < 75 % or RAG < 0.60) + reasons | ✅ | `services/advisory.py`, DiagnosisCard |
| A8 | Optional specific question (typed) | ✅ | Scanner |
| A9 | Voice input for the question | ✅ | `components/VoiceButton.tsx` |
| A10 | Hybrid-RAG advisory rendered as formatted markdown | ✅ | `lib/markdown.tsx` (sanitised) |
| A11 | Dosage safety audit (dosages not found in sources flagged) | ✅ | `services/rag/query.py`, DiagnosisCard |
| A12 | SHA-256 dedup cache scoped by user + question + language | ✅ | `services/cache.py` |
| A13 | Scan saved to history (max 50 kept in original) | ✅ | `api/scans.py` (server-side) |
| A14 | "Ask follow-up in chat" hand-off with image + disease + advisory | ✅ | Scanner → Chat |
| A15 | Clear/reset scan | ✅ | Scanner |
| A16 | Image guard: magic bytes, 10 MB, ≤ 4096 px, decompression bomb, EXIF strip, re-encode, filename sanitise | ✅ | `core/uploads.py` |
| A17 | Disease names localised to Kannada | ✅ | `i18n/kn.ts` |
| A18 | Terminal pipeline progress logger (CNN → env → RAG → LLM → safety) | ✅ | `core/pipeline_log.py` |

## B. Location & microclimate
| ID | Feature | Status | Where |
|---|---|---|---|
| B1 | Auto GPS (with fallback default 13.3161, 75.7720 on error) | ✅ | `lib/location.tsx` |
| B2 | Manual latitude/longitude entry with range validation | ✅ | `components/WeatherCard.tsx` |
| B3 | Location persisted across sessions | ✅ | location store |
| B4 | Live microclimate panel: temperature, feels-like, humidity, 24 h rain, elevation | ✅ | `components/WeatherCard.tsx` |
| B5 | Incubation risk banner (high / moderate / low, same thresholds) | ✅ | `services/environment.py` |
| B6 | Refresh environment button | ✅ | MicroclimatePanel |
| B7 | Region detection (Chikkamagaluru / Kodagu / Hassan-Sakleshpur / Karnataka belt) | ✅ | environment service |
| B8 | No mock data — "unavailable" state when GPS/API missing | ✅ | environment service + UI |
| B9 | 60 s in-memory cache, retry on 429/503 | ✅ | environment service |
| B10 | Google Maps coordinates guide modal (EN + KN steps) | ✅ | `components/modals/GmapsGuide.tsx` |
| B11 | Estimated soil pH 6.2 (labelled "estimated") | ✅ | environment service |

## C. Chatbot
| ID | Feature | Status | Where |
|---|---|---|---|
| C1 | Multi-turn chat threads (server persisted) | ✅ | `api/chat.py` |
| C2 | Thread list / select previous conversation | ✅ | `screens/Chat.tsx` |
| C3 | New conversation | ✅ | Chat |
| C4 | Welcome message | ✅ | Chat |
| C5 | Attach image: upload/capture new | ✅ | `screens/Chat.tsx` (ImagePicker) |
| C6 | Attach image: pick from past scan history | ✅ | ImagePicker |
| C7 | Attached-image banner with thumbnail + remove | ✅ | Chat |
| C8 | CNN run on attached photo, diagnosis injected into prompt | ✅ | `services/chat.py` |
| C9 | Scan metadata hand-off (disease, confidence, advisory, env) + auto first question | ✅ | Chat |
| C10 | Voice input in chat | ✅ | VoiceButton |
| C11 | Location chip + auto GPS / manual coords in chat | ✅ | Chat |
| C12 | Coordinates parsed out of message text ("13.3, 75.7" / "lat: … lng: …") | ✅ | `services/chat.py` |
| C13 | Weather-intent detection (EN + KN keywords) with live readings or "unavailable" | ✅ | chat service |
| C14 | Kannada / Kanglish / English routing (LLM pre-router + regex fallback) | ✅ | `services/lang_router.py` |
| C15 | Last 8 messages included as context | ✅ | chat service |
| C16 | Prompt-injection fencing + input sanitisation + output key redaction | ✅ | `services/llm.py` |
| C17 | Images persisted with messages and shown when reloading a thread | ✅ | chat API (media ids) |
| C18 | Enter to send | ✅ | Chat |
| C19 | Anonymous threads isolated from user threads; owner-only access | ✅ | chat API (auth required now) |

## D. Voice (speech-to-text)
| ID | Feature | Status | Where |
|---|---|---|---|
| D1 | Language picker modal (Kannada / English / cancel) | ✅ | `components/VoiceButton.tsx` |
| D2 | Record with MediaRecorder, stop on second tap, recording state | ✅ | VoiceButton |
| D3 | Local IndicConformer-600M for Kannada (CTC/RNNT, device auto/cuda/cpu) | ✅ | `services/voice.py` |
| D4 | Local Svarah Whisper for Indian English | ✅ | voice service |
| D5 | Groq whisper-large-v3 fallback | ✅ | voice service |
| D6 | Gemini audio fallback | ✅ | voice service |
| D7 | FFmpeg decode (webm/ogg/mp3/mp4/wav → 16 kHz mono) with fallbacks | ✅ | voice service |
| D8 | Env toggles: ENABLE_LOCAL_STT, ENABLE_LOCAL_KANNADA_STT, ENABLE_LOCAL_ENGLISH_STT | ✅ | config |
| D9 | "Transcribing…" placeholder while waiting | ✅ | VoiceButton |

## E. Marketplace
| ID | Feature | Status | Where |
|---|---|---|---|
| E1 | Browse all listings | ✅ | `screens/Market.tsx` |
| E2 | "My listings" tab | ✅ | Market |
| E3 | Sell crop form (title, variety, qty+unit, price+unit, farmer, phone, address, GPS, photos) | ✅ | `components/ListingForm.tsx` |
| E4 | Units: kg, ton, quintal, bag 50 kg, bag 60 kg, custom → normalised kg | ✅ | `schemas/marketplace.py` |
| E5 | Price units: per kg/ton/quintal/50 kg bag/60 kg bag/custom → ₹/kg (+ "≈ ₹x/kg" display) | ✅ | schema + card |
| E6 | Exact 10-digit phone (strips +91) | ✅ | schema + form |
| E7 | Mandatory fields + bounds (price ≤ ₹10 L, qty ≤ 100 t) | ✅ | schema |
| E8 | Validation modal: what to fill + why, "fix" focuses the field, bilingual | ✅ | `components/ListingForm.tsx` (validation sheet) |
| E9 | Estate GPS: auto or manual coordinates in the form | ✅ | ListingForm |
| E10 | Multiple photos with individual captions, remove photo | ✅ | ListingForm |
| E11 | Photo gallery with hero image, thumbnails, caption overlay | ✅ | `components/ListingCard.tsx` |
| E12 | Search (title, variety, address, farmer) | ✅ | marketplace API |
| E13 | Sort: nearest (haversine), newest, price ↑, price ↓, quantity ↓ | ✅ | API + UI |
| E14 | Filters: max distance (15/30/60/120 km), variety, min qty (50/200/1000), price dual slider + inputs, photos only | ✅ | Market |
| E15 | Reset filters | ✅ | Market |
| E16 | Buyer location bar with refresh GPS | ✅ | Market |
| E17 | Distance badge "x km away" | ✅ | ListingCard |
| E18 | Call, WhatsApp (pre-filled message), Google Maps directions | ✅ | ListingCard |
| E19 | Edit own listing | ✅ | ListingForm |
| E20 | Delete with confirmation modal (preview of the listing) | ✅ | `screens/Market.tsx` (delete sheet) |
| E21 | "Your listing" badge / owner actions | ✅ | ListingCard |
| E22 | 50 active listings quota per user | ✅ | API |
| E23 | Report listing (API existed) | ✅ | API + **new** UI |
| E24 | HTML-escaping of text fields | ✅ | schema + React escaping |

## F. History
| ID | Feature | Status | Where |
|---|---|---|---|
| F1 | List of past scans (thumbnail, disease, date, confidence, badge) | ✅ | `screens/History.tsx` |
| F2 | Details modal: image, probabilities, microclimate, advisory | ✅ | `screens/History.tsx` (details sheet) |
| F3 | Delete single scan with 3-second undo toast + timer bar | ✅ | `lib/toast.tsx` |
| F4 | Clear all with undo | ✅ | History |
| F5 | Ask in chat from a past scan | ✅ | ScanDetails |
| F6 | Empty state | ✅ | History |

## G. Profile & account
| ID | Feature | Status | Where |
|---|---|---|---|
| G1 | Name + email display | ✅ | `screens/Profile.tsx` |
| G2 | Stats: total scans, active listings | ✅ | Profile |
| G3 | Sign out | ✅ | Profile |
| G4 | GDPR delete account (purges listings, reports, chats, tokens) | ✅ | `api/users.py` + **new** UI |

## H. App shell & platform
| ID | Feature | Status | Where |
|---|---|---|---|
| H1 | Bottom navigation: Scanner, Chatbot, Market, History, Profile | ✅ | `components/BottomNav.tsx` |
| H2 | Dark / light mode toggle (persisted) | ✅ | `lib/theme.tsx` |
| H3 | Colour palette picker (5 palettes, light+dark variants, active badge) | ✅ | `components/modals/PalettePicker.tsx` |
| H4 | EN / KN language toggle, full Kannada translation | ✅ | `lib/i18n/` |
| H5 | Server settings modal: URL input, test ping with latency, save & connect, reset to default | ✅ | `components/modals/ServerSettings.tsx` |
| H6 | Server status dot (green / amber / red) | ✅ | header |
| H7 | URL normalisation (adds http://, strips trailing slash) | ✅ | `lib/api.ts` |
| H8 | Auth guard (redirect to sign-in, verify session with `/me`) | ✅ | `App.tsx` |
| H9 | 401 → sign out + redirect | ✅ | api client |
| H10 | Android back button: close modal → go home → exit | ✅ | `lib/native.ts` |
| H11 | External app opener (tel:, WhatsApp, Maps) via Capacitor Browser | ✅ | native |
| H12 | Bypass-tunnel-reminder headers (localtunnel support) | ✅ | api client |
| H13 | Camera, microphone, location permissions in APK | ✅ | AndroidManifest |
| H14 | Backend serves the web UI at `/` | ✅ | `main.py` |
| H15 | OpenAPI docs `/docs`, `/redoc` (disabled in production) | ✅ | main |
| H16 | Health endpoint `/health` with version | ✅ | `api/misc.py` |
| H17 | Postgres with auto-create DB + SQLite fallback | ✅ | `core/db.py` |
| H18 | 422 diagnostic logging, safe 500 handler with reference id | ✅ | `core/errors.py` |

## Improvements (new in the rebuild)
| ID | Improvement | Status |
|---|---|---|
| N1 | Sign-up: phone and/or email, confirm password, strength meter, show/hide, username availability, language choice, terms | ✅ |
| N2 | Sign-in with username / email / phone, keep-me-signed-in, lockout countdown, generic errors | ✅ |
| N3 | Argon2id hashing, legacy hash re-hash, password policy | ✅ |
| N4 | JWT access + rotating refresh tokens with reuse detection; sessions list; logout-all | ✅ |
| N5 | Rate limiting + account lockout; audit log | ✅ |
| N6 | Change password, edit profile | ✅ |
| N7 | Server-side scan history (sync across devices, survives reinstall) with soft delete/restore | ✅ |
| N8 | Listing photos stored as sanitised files (`/media`), not base64 in DB | ✅ |
| N9 | Report listing UI; delete/rename chat threads | ✅ |
| N10 | XSS-safe markdown renderer | ✅ |
| N11 | Pickle-free RAG index; hardware-aware RAG profile (bge-m3 + multilingual reranker on GPU) with MMR | ✅ |
| N12 | Citations (source + page) shown with advisories | ✅ |
| N13 | Offline grounded advisory when no LLM is reachable | ✅ |
| N14 | 3-day forecast + spray-window advice | ✅ |
| N15 | First-run server setup screen in the APK | ✅ |
| N16 | Outdoor high-contrast palette, large tap targets, icon+text labels for low-literacy users | ✅ |
| N17 | Offline/backend-unreachable banners with retry | ✅ |
| N18 | Owner-only edits; listing writes require sign-in (fixes anonymous-ownership hole) | ✅ |
