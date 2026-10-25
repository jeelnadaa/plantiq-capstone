# API reference

Base path `/api/v1` (the original `/api/...` paths are aliased). Interactive docs at `/docs` in development.
Auth: `Authorization: Bearer <access_token>`. Errors: `{"detail", "code", "request_id", "errors"?}`.

## Auth
| Method | Path | Body / query | Notes |
|---|---|---|---|
| POST | `/auth/register` | `full_name, username, phone?, email?, password, confirm_password, preferred_language, accept_terms, remember?, device?` | 201 → tokens + user. 409 on duplicate username/phone/email |
| POST | `/auth/login` | `identifier` (username/email/phone) `password, remember?, device?` (also accepts `username`) | 401 generic; 423 locked with `retry_after` |
| POST | `/auth/refresh` | `refresh_token` | rotates; reuse of an old token revokes the session family |
| POST | `/auth/logout` · `/auth/logout-all` | — | 204 |
| GET | `/auth/sessions` · DELETE `/auth/sessions/{id}` | — | signed-in devices |
| GET | `/auth/me` | — | current user |
| GET | `/auth/availability?field=username\|email\|phone&value=` | — | `{available, reason}` |
| POST | `/auth/password-strength` | `password, username?` | `{ok, score 0–4, problems}` |

## Profile
`GET/PATCH /users/me` (full_name, email, phone, preferred_language) · `GET /users/me/stats` → `{scans, listings, chats}` ·
`POST /users/me/password` (current, new, confirm → new tokens; other devices signed out) · `DELETE /users/me` (`password`) — GDPR purge.

## Diagnosis & history
| Method | Path | Notes |
|---|---|---|
| POST | `/predict` | multipart `file`, `user_question?`, `language en\|kn`, `latitude?`, `longitude?` → disease, confidence, distribution, env_data, advisory (markdown), citations, safety_audit, is_blended, reasons, provider, scan_id, image_url |
| GET | `/predict/classes` | the 5 classes with EN/KN names |
| GET | `/scans?kind=all\|disease\|healthy&limit&offset` | newest first |
| GET/DELETE | `/scans/{id}` | DELETE is a soft delete (undo window) |
| POST | `/scans/{id}/restore` | undo |
| DELETE | `/scans` | clear all (soft) → `{ids}` |
| POST | `/scans/restore` | `{ids}` undo clear-all |

## Chat
`POST /chat/message` (form: `user_message`, `session_id?`, `language`, `latitude?`, `longitude?`, `image_file?` | `image_base64?` |
`media_id?`, `attached_image_name?`, `disease_context?`, `scan_metadata_json?`) → `{session_id, reply, history, disease, language,
provider, sources, env_used, image_url}` · `GET /chat/threads` · `GET /chat/threads/{id}/messages` · `PATCH /chat/threads/{id}` (`title`) ·
`DELETE /chat/threads/{id}`.

## Marketplace
`GET /marketplace/listings?q&variety&min_qty&min_price&max_price&has_photos&latitude&longitude&max_distance_km&sort_by=distance|newest|price_asc|price_desc|qty_desc` ·
`GET /marketplace/my-listings` · `POST /marketplace/listings` · `GET/PUT/DELETE /marketplace/listings/{id}` (owner only for writes) ·
`POST /marketplace/listings/{id}/report` (`reason`; once per user).
Listing body: `title, variety, quantity, quantity_unit, price, price_unit, farmer_name, phone_number, address, latitude?, longitude?,
photos[{media_id, caption}]` — server computes `quantity_kg` and `price_per_kg`.

## Media, voice, weather, system
`POST /media` (multipart `file`, `kind`) → `{id, url, width, height}` · `GET /media/{id}.jpg` ·
`POST /voice/transcribe` (`file`, `target_language kn|en`) → `{text, language, provider}` · `GET /voice/status` ·
`GET /environment/live?latitude&longitude` (alias `/environment/microclimate`) · `GET /environment/forecast` ·
`GET /system/info` · `GET /health` (also `/api/health`).
