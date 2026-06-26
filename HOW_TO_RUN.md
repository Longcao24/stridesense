# HOW TO RUN

Run the phone motion-tracking demo and open the English web UI on your phone.

---

## 1. Requirements

- **macOS** (`serve_https.py` auto-generates the self-signed certificate with the built-in `openssl`).
- **Python 3** — standard library only, no extra packages to install.
- **Phone and computer on the same WiFi.**

---

## 2. Start the server

```bash
cd phone-motion-tracker
python3 serve_https.py            # default port 8443; python3 serve_https.py 9000 to change it
```

The terminal prints the address to open on your phone. You can also get the LAN IP manually:

```bash
ipconfig getifaddr en0 || ipconfig getifaddr en1
```

> ⚠️ **The IP changes** (after switching WiFi / a DHCP renewal / the computer waking from sleep), so always use the current IP, not an old one.

---

## 3. Open it on your phone

Open the **English UI (default home page)**:

```
https://<computer-IP>:8443/
```

On the first "certificate not trusted" prompt → choose **Continue / Visit anyway** (normal for a self-signed certificate).

---

## 4. Use it

1. **① Grant & start sensors** → on the iOS prompt choose **Allow**.
2. **② Calibrate** → lay the phone flat and keep it still for ~1.5 s.
3. Pick a mode:
   - **Gesture mode**: ③ Start recording → draw a circle / write in the air (2–4 s) → ■ Stop → the trajectory shows on the right (replay / export available).
   - **Walking mode (PDR)**: strap the phone to your instep/ankle → ▶ Start walk tracking → take 6–8 steps → ■ Stop → see the top-down path + gait panel + 3D view.
4. *(Optional)* **⬆ Upload** sends the recording back to the computer (`uploads/upload_NNN.json`).

---

## 5. Stop

Press `Ctrl-C` in the terminal (or `pkill -f serve_https.py` if it runs in the background).

---

## Troubleshooting

**"sensor permission denied" on iOS** — this is a local iOS Safari behavior, not the server. Once denied, refreshing the page or restarting the server does nothing because the "deny" is cached per site (IP:port). Clear it **on the phone**:

1. **Settings → Safari → Motion & Orientation Access**: make sure it is on; if it already is, **turn it off and back on** (resets the site's memory).
2. Still failing: **Settings → Safari → Advanced → Website Data** → delete `<computer-IP>` (or "Clear History and Website Data").
3. Reopen the page → "Continue" on the certificate → **① Grant access, this time choose Allow**.

> Tip: during a live demo, open the page and grant access **on the spot** (don't open it in advance and let it sit — iOS reclaims/reloads idle background tabs); turn off the phone's auto-lock; keep the computer awake.

**Other quick fixes**

| Symptom | Fix |
|------|------|
| Phone can't open the page / keeps spinning | Not on the same WiFi, or using an old IP — get the IP again and confirm the same network |
| No authorization prompt | Make sure the address is `https://` (not `http://`), and iOS Motion & Orientation Access is on |
| The walking path slowly rotates over a long distance | Expected: slow yaw drift without a magnetometer; not noticeable on a short demo |
