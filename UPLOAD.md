# How to put this on GitHub

Take your time — this is about 15 minutes, and nothing here can break anything.

There are two ways. **Way A uses an app and needs no typing.** Pick that one if you're unsure.

---

## Before you start

You need a free GitHub account. If you don't have one yet, go to https://github.com/signup — it takes two minutes.

Then unzip the file you downloaded. You should end up with a folder called `kenchikushi-2027` containing 17 files. Put it somewhere you'll remember, like your Documents folder.

**One important warning:** do not upload these files by dragging them into the GitHub website. Two of the folders start with a dot (`.github` and `.nojekyll`), and your computer hides those. They get silently dropped when you drag, and then things quietly stop working. Both methods below avoid that problem.

---

## Way A — GitHub Desktop (recommended)

### 1. Install the app

Download GitHub Desktop from https://desktop.github.com and install it. Open it and sign in with your GitHub account when it asks.

### 2. Add your folder

In the menu bar: **File → Add Local Repository**

Click **Choose...** and select your `kenchikushi-2027` folder.

You'll probably see a message saying *"This directory does not appear to be a Git repository."* That's expected. Click the blue link that says **create a repository**.

### 3. Create it

A form appears. You only need to check one thing:

- **Name** — leave it as `kenchikushi-2027`
- **Git ignore** — leave as None
- **License** — leave as None

Click **Create Repository**.

You'll now see a list of all 17 files on the left. That's good — it means nothing was lost.

### 4. Commit

At the bottom left there's a box that says *Summary*. Type anything, for example `first upload`.

Click the blue **Commit to main** button.

### 5. Publish

At the top, click **Publish repository**.

**Keep "Keep this code private" checked.** Then click **Publish repository**.

That's it — your files are on GitHub. Skip ahead to *"Turn on the website"* below.

---

## Way B — Terminal

Only if you're comfortable with a command line.

```bash
cd kenchikushi-2027
git init
git add -A
git commit -m "first upload"
```

Then create the repository on GitHub and push:

```bash
gh repo create kenchikushi-2027 --private --source=. --push
```

If you don't have the `gh` command, make an empty repository at https://github.com/new (private, no README) and then:

```bash
git remote add origin https://github.com/YOUR-NAME/kenchikushi-2027.git
git branch -M main
git push -u origin main
```

---

## Turn on the website

Your files are uploaded, but the page isn't visible yet. Two settings to change.

### 1. Turn on Pages

Go to your repository on github.com. Click **Settings** (the tab at the top right, with the gear icon).

In the left sidebar, click **Pages**.

Under *Build and deployment → Source*, leave it as **Deploy from a branch**. Below that:

- **Branch** — change from `None` to `main`
- **Folder** — change from `/ (root)` to `/docs`

Click **Save**.

### 2. Let the automation write

Still in **Settings**, in the left sidebar click **Actions**, then **General**.

Scroll to the bottom, to **Workflow permissions**.

Select **Read and write permissions**, then click **Save**.

This is what lets the weekly checklist update your progress file.

---

## Look at it

Wait about two minutes, then go to:

```
https://YOUR-NAME.github.io/kenchikushi-2027/
```

(Replace `YOUR-NAME` with your GitHub username.)

You should see the plan. If you get a 404, wait another minute and refresh — the first build is slow.

**Bookmark this on your phone.** That's the page you'll open every day.

---

## Optional — sync your checkboxes

Without this, ticking a box on the page only lasts until you close it. With it, your progress saves and appears on every device.

1. On GitHub, click your avatar (top right) → **Settings**
2. Scroll all the way down the left sidebar → **Developer settings**
3. **Personal access tokens → Fine-grained tokens** → **Generate new token**
4. Fill in:
   - **Token name** — anything, e.g. `study plan`
   - **Expiration** — 90 days
   - **Repository access** — choose **Only select repositories**, then pick `kenchikushi-2027`
   - **Permissions → Repository permissions** — find **Contents** and set it to **Read and write**. Leave everything else alone.
5. Click **Generate token** and copy the code that appears (it starts with `github_pat_`). **You can only see it once.**
6. Open your page, scroll to the bottom, open **書き出しと設定**, and find the sync box
7. Type `YOUR-NAME/kenchikushi-2027` in the first field, paste the token in the second, and click **接続**

The dot turns green. From now on, ticking a box saves within a second.

If this feels like too much, skip it. The weekly issue works just as well and needs no setup.

---

## If something goes wrong

**The page shows 404**
Give it five minutes. If it's still failing, check Settings → Pages and make sure Folder says `/docs`, not `/ (root)`.

**The page loads but looks like plain text**
The `.nojekyll` file didn't upload. This happens with drag-and-drop. Re-upload using Way A.

**No weekly issue appears on Monday**
Check Settings → Actions → General → Workflow permissions is set to *Read and write*. You can also test it now: go to the **Actions** tab, click **weekly** on the left, then **Run workflow**.

**I want to change the exam date or the plan**
Edit `data/plan.yaml`. You can do this directly on github.com — click the file, then the pencil icon. Everything else updates automatically.

---

## What you'll actually touch

Out of the 17 files, you only ever need two:

| File | What it's for |
|---|---|
| `data/plan.yaml` | The plan itself — exam date, subjects, chapters, hours |
| `data/log.yaml` | Your progress — this fills itself in as you tick boxes |

Everything else runs the machinery. You can ignore it.
