# Security

Controls in the PlantIQ rebuild, the threats they address, and where the tests are. Security tests live in
`backend/tests/security/test_security.py` (run `pytest -m security`), with more in the auth/integration suites and
`frontend/tests/unit/components.test.tsx` (XSS rendering).

## Vulnerabilities fixed from the original app
| Original issue | Fix |
|---|---|
| Anyone (even anonymous) could create listings; listings with no owner could be edited/deleted by any user | All marketplace writes require sign-in; edit/delete strictly owner-only (403) |
| Advisory / chat text rendered with `innerHTML` (stored XSS via LLM output or chat history) | React text nodes only; custom markdown renderer never creates HTML from strings |
| Opaque 7-day session tokens stored in plain text, no rotation or revocation UI | 15-min JWT access tokens + 30-day refresh tokens stored **hashed**, rotated on every use, with reuse detection; logout, logout-all, per-device sign-out |
| No login rate limit or lockout | Per-IP rate limits + account lockout (5 failures → 15 min), identifier-independent |
| No password rules | Policy: ≥8 chars, letters + digits, not common, not the username; strength meter in UI |
| `pickle.load` of RAG index files (code execution if the index dir is writable) | Index stored as FAISS + JSON; models stored as safetensors (`scripts/prepare_models.py`) |
| torch 2.5.1 `torch.load` RCE even with `weights_only=True` (CVE-2025-32434) | torch 2.7.1 |
| Listing photos as base64 in DB rows | Uploads re-encoded to JPEG, EXIF/GPS stripped, stored as files with random 128-bit ids |
| `CORS_ORIGINS=*` with credentials | Explicit allow-list (+ private-LAN regex in development only); no cookies → no CSRF surface; `*` refused in production |

## Authentication & sessions
- **Argon2id** (time 3, memory 64 MB) for new hashes; legacy bcrypt and PBKDF2 hashes from the original DB still verify and are
  transparently upgraded on next login.
- Constant-ish time for unknown users (a dummy hash is verified), and the **same message** for unknown user and wrong password.
- JWT: HS256 pinned (rejects `alg=none` / algorithm confusion), requires `exp/iat/sub/jti/typ`, checks `iss`/`aud`.
- Access tokens die immediately on logout (session family must be alive) and when the password changes.
- Refresh tokens: 384-bit random, only SHA-256 stored, rotated each use; replaying a used token revokes the whole family
  (`refresh_reuse_detected` audit event).
- Password change and account deletion require the current password.
- Audit log table for register / login / failures / lockout / logout / password change / deletion.

## Input & upload handling
- Pydantic v2 validation on every body; phone exactly 10 digits; bounds on price/quantity; angle brackets stripped from
  free-text listing fields (display-safe, no `&amp;` artefacts).
- Images: magic-byte check (JPEG/PNG/WebP only), ≤10 MB, ≤4096 px, decompression-bomb guard, EXIF transpose then strip,
  re-encode, filename sanitised (path traversal).
- Audio: container sniffing (webm/ogg/wav/mp3/mp4/flac/aac), ≤10 MB, FFmpeg decode limited to 90 s.
- Request body limit 15 MB at the ASGI layer (Content-Length and streaming).
- SQL only through SQLAlchemy parameters; `LIKE` searches use bound parameters.
- Media ids validated with a strict regex before touching the filesystem; reusing a photo in chat or a listing requires owning it.

## LLM safety
- User text cleaned (control chars and `<>{}[]\`` removed, length-capped) and fenced inside `<user_query>` / `<agronomic_context>`
  with a system instruction to treat them as data.
- LLM output passes through secret redaction (Groq/Gemini/HF/OpenAI keys, JWTs, 64-hex tokens).
- **Dosage audit**: numbers with units in the advice are checked against the retrieved documents; unverified doses are flagged in the UI.
- No LLM → built-in grounded offline guide, so the app never shows an empty/invented answer.

## Transport, headers, errors
- Headers on every response: CSP (`script-src 'self'`, `frame-ancestors 'none'`, `object-src 'none'`), X-Frame-Options DENY,
  nosniff, Referrer-Policy, Permissions-Policy (camera/mic/geo self), COOP; HSTS when served over HTTPS; `Cache-Control: no-store` on API.
- The APK bundle carries its own CSP meta tag.
- Errors: uniform JSON with a request id; no stack traces or internals ever returned.
- OpenAPI docs disabled in production; production refuses to start without a strong `SECRET_KEY`.

## Mobile app
- Backend URL is user-configured at runtime; the app warns when an `http://` address is not a private LAN address.
- Cleartext HTTP is allowed by `network_security_config.xml` because farm laptops have no TLS. Use HTTPS (reverse proxy or tunnel)
  for anything beyond the local Wi-Fi. User-installed CAs are **not** trusted.
- `allowBackup=false`, only the permissions the features need (camera, microphone, location, images).
- Tokens live in WebView localStorage; mitigated by the strict CSP and no HTML rendering of remote content.

## Known limitations / residual risk
- Rate limiter is in-process; run one worker or move it to Redis when scaling out.
- Media URLs are capability URLs (unguessable, but anyone with the link can view the image). Images carry no EXIF.
- Debug APK is signed with the Android debug key — sign release builds with your own keystore (see docs/DEPLOYMENT.md).
- Listing reports are stored but there is no moderator UI yet.

## Reporting
Open an issue in the project repository (do not include exploit details publicly) or contact the maintainer directly.
