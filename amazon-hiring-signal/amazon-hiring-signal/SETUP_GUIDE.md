# Setup Guide (no coding required)

This walks through getting your hiring-signal dashboard live and
self-updating. You're just clicking buttons on a website — you won't
write or edit any code.

Total time: ~15 minutes. Totally free.

---

## Step 1 — Create a free GitHub account

GitHub is where your scraper and dashboard will "live" and run automatically.

1. Go to **github.com/signup**
2. Enter an email, password, and username
3. Verify your email when it asks

---

## Step 2 — Create a repository (a project folder)

1. Once logged in, click the green **"New"** button (or go to
   github.com/new)
2. Repository name: type something like `hiring-signal`
3. Set it to **Private** (so only you can see it)
4. Leave everything else as default
5. Click **"Create repository"**

---

## Step 3 — Upload the files I gave you

1. Unzip the `amazon-hiring-signal.zip` file I sent you, on your computer.
   You should see a folder with `scraper.py`, `README.md`,
   a `dashboard` folder, a `data` folder, and a `.github` folder inside it.
2. Back on GitHub, on your new repo's page, click **"Add file" → "Upload
   files"**
3. Open the unzipped folder on your computer, select **everything inside
   it** (all files and folders), and drag them into the GitHub upload box
   — GitHub will preserve the folder structure automatically
4. Scroll down and click the green **"Commit changes"** button

> If your browser won't let you drag whole folders, you can upload files
> one at a time — just make sure `scrape.yml` ends up inside a folder
> path of `.github/workflows/scrape.yml` and `index.html` ends up inside
> `dashboard/`.

---

## Step 4 — Give the automation permission to save its results

1. In your repo, click **"Settings"** (top right of the repo page)
2. In the left sidebar, click **"Actions" → "General"**
3. Scroll down to **"Workflow permissions"**
4. Select **"Read and write permissions"**
5. Click **"Save"**

(This lets the daily scrape save its results back into your repo.)

---

## Step 5 — Run it for the first time

1. Click the **"Actions"** tab at the top of your repo
2. You'll see a workflow called **"Scrape Amazon Jobs"** — click it
3. Click the **"Run workflow"** button (dropdown, then a green button)
4. Wait about 1–2 minutes, then refresh the page — you should see a green
   checkmark when it's done
5. This means it just went out, pulled current Amazon job postings, and
   saved them into your repo, replacing the placeholder sample data

If it fails (red X), click into it to see the error — the most likely
cause is Amazon blocking the request, which the README explains how to
diagnose. Feel free to paste me the error and I'll help troubleshoot.

---

## Step 6 — Turn on your live dashboard link

1. Go to **"Settings" → "Pages"** (left sidebar)
2. Under **"Build and deployment" → "Source"**, choose
   **"Deploy from a branch"**
3. Under **"Branch"**, choose **`main`** and folder **`/ (root)`**
4. Click **"Save"**
5. Wait 1–2 minutes, then refresh this settings page — a link will
   appear at the top like:
   `https://yourusername.github.io/hiring-signal/`
6. Your actual dashboard is one folder deeper — go to:
   `https://yourusername.github.io/hiring-signal/dashboard/`
7. Bookmark that link — that's your live dashboard, forever

---

## You're done

From now on:
- Every day, GitHub automatically re-scrapes Amazon.jobs and updates your data
- Every time you open your bookmarked link, you see current numbers
- You never need to touch the code again

If anything looks broken or you want a change (like tracking specific
teams you care about, or getting an email alert when a category spikes),
just tell me and I'll make the edit — you'd just re-upload the changed
file the same way as Step 3.
