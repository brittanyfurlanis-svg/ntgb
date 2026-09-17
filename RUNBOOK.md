# Going live on www.ntgb.com.au — one-time setup

Everything below is clicking in GitHub and GoDaddy. Nothing to install. Allow about 30 minutes plus DNS time.
Hosting is GitHub Pages: free, HTTPS, no server to look after. Data is public AEMO data only.

## 1. Put the code on GitHub (10 min)
1. Sign in at github.com (create an account under your business email if you don't have one).
2. Click **New repository** → name `ntgb` → **Public** → leave everything else unticked → **Create repository**.
3. On the empty repo page choose **uploading an existing file**. Drag the whole contents of the `ntgb` folder in
   (the `site`, `scripts`, `data`, `tests`, `.github` folders and the `.gitignore`, `README.md`, `RUNBOOK.md` files).
   If the browser upload won't take the `.github` folder, install GitHub Desktop, "Add local repository" on the `ntgb` folder, Commit, Publish.
4. Commit message: `initial site` → **Commit changes**.

## 2. Turn on the site (3 min)
1. Repo → **Settings** → **Pages**.
2. Under **Build and deployment**, Source = **GitHub Actions**.
3. Repo → **Actions** tab → if it asks, **enable workflows**. Open **Publish site** → **Run workflow** → **Run workflow**.
   After a minute the site is live at `https://<your-username>.github.io/ntgb/` — check the map loads.

## 3. Point the domain at it (5 min at GoDaddy, then up to a few hours for DNS)
At GoDaddy → My Products → ntgb.com.au → **DNS** → add these records (delete any existing A / CNAME for `@` and `www` first):

| Type  | Name | Value                         | TTL     |
|-------|------|-------------------------------|---------|
| A     | @    | 185.199.108.153               | 1 hour  |
| A     | @    | 185.199.109.153               | 1 hour  |
| A     | @    | 185.199.110.153               | 1 hour  |
| A     | @    | 185.199.111.153               | 1 hour  |
| CNAME | www  | `<your-username>.github.io`   | 1 hour  |

(GoDaddy "Forwarding" is not needed — GitHub redirects ntgb.com.au to www.ntgb.com.au itself.)

Then back in GitHub → Settings → Pages → **Custom domain** = `www.ntgb.com.au` → Save. Wait for the DNS check to pass
(refresh the page; can take from minutes to a few hours), then tick **Enforce HTTPS**.

## 4. Start the data refresh (1 min)
Repo → **Actions** → **Refresh AEMO data** → **Run workflow**. It fetches the three AEMO files, commits new data and the site
republishes itself. From then on it runs at 13:00 and 17:00 ACST every day. If a run fails (AEMO file missing, nemweb down)
the site keeps showing the last good data — a failed fetch never blanks the page.

## Later
- ntgb.com and ntgasboard.com: at GoDaddy use **Forwarding** → `https://www.ntgb.com.au` (permanent, 301).
- To change the map: edit `site/index.html`, commit — the site republishes in about a minute.
- To move the data pipeline to Australian hosting for the private layer, `scripts/fetch_gbb.py` is plain Python and runs anywhere; the site stays static.
