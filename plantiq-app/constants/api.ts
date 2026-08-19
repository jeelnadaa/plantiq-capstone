// DEMO BUILD: points at a temporary Cloudflare Tunnel to your laptop's local backend.
// This URL changes every time the tunnel is restarted (cloudflared tunnel --url http://localhost:5000).
// For normal local dev (same Wi-Fi as your PC), swap this back to your LAN IP instead.
export const BASE_URL = 'https://yukon-gourmet-seeker-felt.trycloudflare.com';
