# Security measures

What we protect, the measures taken, and the test that proves each one. Measures are grouped as **platform-wide** and then by
**module** (1 CNN · 2 RAG & environment · 3 Chatbot · 4 Market discovery). Test IDs refer to [TESTING.md](TESTING.md);
security tests live in `backend/tests/security/test_security.py`.

## Assets and threats
| Asset | Threats considered |
|---|---|
| Farmer accounts | password guessing, credential stuffing, stolen tokens, session hijack, account enumeration |
| Personal data (phone, email, location, photos) | leakage via photos' EXIF GPS, other users reading data (IDOR), logs |
| Server | malicious uploads, oversized requests, injection (SQL, prompt), code execution via model/index files, DoS |
| Advice quality | LLM hallucinating chemical doses, prompt injection changing advice |
| Marketplace | fake/abusive listings, hijacking someone else's listing, spam |
| API keys (Gemini, Groq, HF) | leaking through responses, logs or the repository |

---

## A. Platform-wide measures
| # | Measure | Detail | Verified by |
|---|---|---|---|
| A1 | Password hashing | **Argon2id** (t=3, 64 MB, p=2). Legacy bcrypt/PBKDF2 hashes from the original database still verify and are upgraded to Argon2id on next sign-in | unit: argon2/legacy tests; integration: legacy upgrade |
| A2 | Password policy | ≥ 8 chars, letters + digits, not in common-password list, not equal to username; enforced on server, mirrored in UI | unit + integration policy tests |
| A3 | Short-lived access tokens | JWT HS256, 15 min, algorithm pinned (rejects `alg=none`), requires exp/iat/sub/jti/typ, checks issuer & audience | unit: forged/none/expired/audience tests; security: forged tokens |
| A4 | Rotating refresh tokens | 384-bit random, **only SHA-256 stored**, new token on every refresh; replay of a used token revokes the whole session family and is audited | integration: rotate + reuse detection |
| A5 | Immediate logout | access token is rejected as soon as its session is revoked (not only at expiry); password change invalidates older tokens | integration: logout, sessions, change password |
| A6 | Brute-force protection | per-IP rate limit on auth (20/min) + global API limit; account lock after 5 failures for 15 min, independent of identifier variant (username/email/phone) | security: login rate limit, global limit, lockout bypass |
| A7 | No account enumeration | identical message for unknown user and wrong password; dummy hash verified for unknown users (similar timing) | integration: same message test |
| A8 | Re-authentication | password required to change password or delete the account | integration tests |
| A9 | Authorisation everywhere | every private endpoint requires a valid token (26 endpoints checked) | security: 401 on every private endpoint |
| A10 | Security headers | CSP (`script-src 'self'`, `object-src 'none'`, `frame-ancestors 'none'`), X-Frame-Options DENY, nosniff, Referrer-Policy, Permissions-Policy, COOP; HSTS over HTTPS; `no-store` on API | security: headers, HSTS |
| A11 | CORS allow-list | only app/web origins (+ private LAN in development); no cookies → no CSRF; wildcard refused in production | security: CORS test, production config test |
| A12 | Request limits | 15 MB body limit at the ASGI layer (declared and streamed) | security: body size test |
| A13 | Safe errors | uniform JSON with request id; no stack traces, paths or secrets returned | security: errors do not leak |
| A14 | Secure configuration | production refuses weak `SECRET_KEY` and `*` CORS, disables API docs; `.env` git-ignored; `.env.example` has no secrets | security: production config test |
| A15 | Audit log | register, login, failures, lockout, logout, session revoke, password change, deletion stored with time and IP | security: audit test |
| A16 | Privacy / GDPR | delete-account erases listings, reports, chats, scans, cache, tokens and photo files | integration: delete purges |
| A17 | Secrets never logged | passwords never in responses or logs | security: password never logged |
| A18 | Dependency patching | PyTorch upgraded 2.5.1 → 2.7.1 (CVE-2025-32434: `torch.load` code execution even with `weights_only=True`) | requirements pin |
| A19 | Mobile app | CSP in the bundle; `allowBackup=false`; only system CAs trusted; minimum permissions; warns on non-LAN `http://` servers; external links limited to https/tel | E2E + manifest review |
| A20 | XSS-safe rendering | LLM/user text rendered as React text nodes via a custom markdown renderer — never `innerHTML` | frontend: markdown XSS tests; listing escape test |

## B. Module 1 — CNN leaf diagnosis
| # | Measure | Detail | Verified by |
|---|---|---|---|
| B1 | Upload validation | file signature must be JPEG/PNG/WebP (extension ignored); empty, > 10 MB, > 4096 px rejected | unit: image guard; security: upload attacks |
| B2 | Decompression-bomb guard | PIL pixel limit (25 MP) and dimension check before decoding | unit + security tests |
| B3 | Metadata stripping | EXIF (incl. **GPS location**, camera serial) removed by re-encoding to a clean JPEG | unit: EXIF/GPS stripped |
| B4 | Path traversal | client filenames sanitised (`../../x` → `x.jpg`) | unit + security tests |
| B5 | Safe model loading | `weights_only=True` with patched PyTorch; weights file hash checked in tests | ml: weights are the original file |
| B6 | Per-user cache | cache key includes user id → one user can never receive another user's result | integration: cache scoped per user |
| B7 | Scan ownership | users only see/delete/restore their own scans (404 otherwise) | security: IDOR scans |
| B8 | Media capability URLs | photos served under 128-bit random ids, strict id regex, `nosniff`, always `image/jpeg` | integration: media serving |

## C. Module 2 — RAG advisory & environmental data
| # | Measure | Detail | Verified by |
|---|---|---|---|
| C1 | No pickle | knowledge index stored as FAISS + JSON (original used `pickle.load`, which runs code); models stored as safetensors | code review; index tests |
| C2 | Prompt-injection fencing | farmer text cleaned (control chars, `< > { } [ ] \` `` ` ``) and placed in `<user_query>`; system instruction: treat fenced content as data, never reveal instructions | security: prompt injection test |
| C3 | Grounding | LLM may only use retrieved passages; doses only if present in context | advisory unit tests |
| C4 | Dose audit | every number+unit in the answer checked against sources; unverified doses flagged to the farmer | unit: dosage audit |
| C5 | Secret redaction | LLM output scrubbed of API keys, JWTs and long hex tokens | unit + security: redaction |
| C6 | No fabricated weather | missing GPS / weather outage → "unavailable"; LLM told not to invent numbers | unit: never mocks; integration: weather unavailable |
| C7 | Outbound calls | fixed provider URLs only (no user-controlled URLs → no SSRF); timeouts and retry limits; API keys sent in headers, never in URLs or logs | LLM client tests |
| C8 | Coordinate validation | latitude/longitude range-checked before any outbound request | integration: environment validation |

## D. Module 3 — Chatbot
| # | Measure | Detail | Verified by |
|---|---|---|---|
| D1 | Thread privacy | read/write/delete of another user's thread → 403; can't inject messages into someone else's thread | integration: thread isolation |
| D2 | Photo reuse checks | a past-scan photo can only be attached by its owner | integration: media_id from scan |
| D3 | Input limits | message ≤ 2000 chars, scan metadata ≤ 20 KB, base64 images size-checked before decoding | integration: chat validation |
| D4 | Same upload guard as Module 1 | chat photos sanitised, EXIF stripped | integration: attach image |
| D5 | Audio guard | container sniffing (webm/ogg/wav/mp3/mp4/flac/aac), ≤ 10 MB, decoding capped at 90 s, temp files cleaned | unit: audio guard; integration: voice rejects bad audio |
| D6 | Fenced history | previous messages also cleaned and fenced in `<history>` | prompt tests |
| D7 | Rate limiting | heavy endpoints (chat, predict, voice) limited per IP | security: rate limit tests |

## E. Module 4 — Market discovery
| # | Measure | Detail | Verified by |
|---|---|---|---|
| E1 | Sign-in to sell | anonymous listing creation removed (was possible in the original) | security: 401 tests |
| E2 | Owner-only changes | edit/delete by anyone but the owner → 403 (original allowed editing "ownerless" listings) | integration: owner-only |
| E3 | Server-side validation | all fields re-validated; 10-digit phone; bounds on price/quantity; ₹/kg computed by server | unit: schema tables; integration: invalid body |
| E4 | Stored-XSS neutralised | angle brackets removed from free text + escaped on display | security: stored XSS; frontend escape test |
| E5 | SQL injection | only bound parameters (search with `LIKE` too) | security: SQL-injection strings |
| E6 | Photo ownership | listing photos must be the seller's own uploads | security: media reuse IDOR |
| E7 | Abuse controls | 50 listings per user; report once per listing; cannot report own listing | integration: quota, report once |
| E8 | Safe external links | only `https:`/`tel:` opened; WhatsApp/Maps URLs built server-side with URL encoding | code review |

---

## Vulnerabilities found in the original app and fixed
| Original issue | Fix | Ref |
|---|---|---|
| Anonymous listing creation; anyone could edit/delete listings without owner | sign-in + owner-only | E1, E2 |
| LLM/chat text injected as raw HTML (stored XSS) | text-node rendering | A20 |
| Plain-text 7-day tokens, no rotation/revocation | JWT + hashed rotating refresh + logout everywhere | A3–A5 |
| No rate limit/lockout, no password rules | A2, A6 | |
| `pickle.load` of RAG index | FAISS + JSON, safetensors | C1 |
| PyTorch CVE-2025-32434 | torch 2.7.1 | A18 |
| Listing photos as base64 in DB, EXIF kept | sanitised files | B3, B8 |
| `CORS_ORIGINS=*` | allow-list | A11 |

## Residual risks and recommendations
- **HTTP on farm Wi-Fi**: traffic to a laptop server is unencrypted; use HTTPS (reverse proxy or tunnel) beyond the local network.
- Rate limiter is per process; use Redis if running several workers.
- Photo URLs are unguessable capability links; anyone given a link can view that photo (no metadata inside).
- Tokens are kept in the WebView's local storage (mitigated by CSP and no HTML rendering).
- Debug APK uses the Android debug key; sign releases with your own keystore ([docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)).
- Reports are stored but there is no moderator dashboard yet.
