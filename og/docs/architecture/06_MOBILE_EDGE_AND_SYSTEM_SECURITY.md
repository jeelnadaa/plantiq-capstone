# 📱 Module 6: Mobile Edge Architecture, Networking & System Security

## 1. Executive Summary & Architecture Paradigm
PlantIQ is engineered as a cross-platform, high-performance mobile client packaged as an Android APK via **Capacitor 7** alongside a **FastAPI** asynchronous backend.

The architecture emphasizes:
1. **Zero-Overhead Hybrid WebView Bridge** (vs. heavy React Native / Flutter runtimes)
2. **Stateless JWT Bearer Token Security with PBKDF2 Password Hashing**
3. **Dynamic In-App Server Switching for Demonstration Resilience**
4. **Android Safe Area Inset Support & Hardware Back Button Lifecycle Interception**

---

## 2. Mobile Framework Comparative Rationale

| Dimension | Capacitor 7 (Chosen) | React Native | Flutter | Progressive Web App (PWA) Alone |
| :--- | :--- | :--- | :--- | :--- |
| **APK Binary Footprint** | **4.11 MB** | ~35–50 MB | ~45–65 MB | N/A (Browser dependent) |
| **Asset Sync & Build Time** | **~10 seconds** | 3–6 minutes | 2–5 minutes | Instant |
| **Hardware Access** | Camera, GPS, Mic via Bridge | Bridge / Native | Platform Channels | Limited background & intent access |
| **Offline Code Sharing** | **100% unified HTML/JS** | Requires JSX rewrite | Requires Dart rewrite | 100% unified |

### Why Capacitor 7 Was Chosen:
* **Lightweight Efficiency**: Low-end Android smartphones owned by estate workers often have limited internal storage. A 4.11 MB APK installs in seconds without burdening the device.
* **100% Shared Frontend Logic**: The exact same HTML5, CSS design tokens, and JavaScript modules run identically on the local web server, cloud deployments, and inside the mobile APK.

---

## 3. Security & Authentication Architecture

### 3.1 Cryptographic Password Hashing (PBKDF2-HMAC-SHA256)
Passwords are never stored in plaintext. They are salted and hashed using Password-Based Key Derivation Function 2 (PBKDF2) with 100,000 iterations:
$$\text{DK} = \text{PBKDF2}(\text{HMAC-SHA256}, \text{Password}, \text{Salt}, c=100000, \text{dkLen}=32)$$

### 3.2 Stateless JWT Token Authentication
Upon successful authentication, the API issues a JSON Web Token (JWT) signed with HMAC-SHA256:
$$\text{Token} = \text{Header} \mathbin{\Vert} \text{Payload} \mathbin{\Vert} \text{HMAC-SHA256}(\text{Header} \mathbin{\Vert} \text{Payload}, \text{SecretKey})$$
* Tokens contain `sub` (User ID), `role`, and expiration timestamp (`exp`).
* All protected endpoints (`/api/scanner/predict`, `/api/chat/*`, `/api/marketplace/listings`) validate the Bearer token in the `Authorization` header.

---

## 4. In-App Dynamic Server IP Switcher

### 4.1 Demonstration & Network Mobility Problem
During academic capstone evaluations or field demonstrations, the backend server laptop and mobile devices switch between institutional Wi-Fi, personal 4G/5G hotspots, and remote cloud URLs. Hardcoding IP addresses results in broken connections.

### 4.2 Dynamic Client-Side Ingestion Architecture
* **Real-Time Latency Ping**: The client performs a background `GET /health` fetch to measure round-trip time in milliseconds:
  $$\text{Latency} = t_{\text{response}} - t_{\text{request}}$$
* **Visual Status Indicator**:
  * 🟢 **Green (200 OK)**: Backend reachable with active ping measurement.
  * 🔴 **Red (Offline / Unreachable)**: Prompts farmer/evaluator to update the server IP.
* **Local Storage Persistence**: The active endpoint is saved in `localStorage.setItem('plantiq_server_url', ...)` and loaded across app lifecycles.
