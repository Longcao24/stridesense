# Cloudflare Backend Deploy

This Worker replaces the local Python `POST /upload` receiver when the web app is hosted on HTTPS.

## 1. Create the KV namespace

```bash
npx wrangler login
npx wrangler kv namespace create MOTION_UPLOADS
```

Copy the returned `id` into `wrangler.toml`:

```toml
kv_namespaces = [
  { binding = "MOTION_UPLOADS", id = "your-real-id" }
]
```

## 2. Deploy

```bash
npx wrangler deploy
```

Wrangler prints a URL like:

```text
https://phone-motion-tracker-upload.<account>.workers.dev
```

Open the web app, paste this into the Cloudflare upload field:

```text
https://phone-motion-tracker-upload.<account>.workers.dev/upload
```

Then tap **Save cloud**. Gesture and gait uploads will go to Cloudflare KV instead of the local Python server.

## 3. Check uploads

```text
GET https://phone-motion-tracker-upload.<account>.workers.dev/health
GET https://phone-motion-tracker-upload.<account>.workers.dev/uploads
GET https://phone-motion-tracker-upload.<account>.workers.dev/uploads/<name>.json
```
