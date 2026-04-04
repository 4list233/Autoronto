# 🚀 Create a Git Repository for R2Y5 TeamGantt Project

## Step 1: Initialize Git Repository

```bash
cd "/Users/5425855/Documents/Uoft Studying/Autoronto"
git init
```

## Step 2: Stage All Files

```bash
git add .
```

**Note:** Your `.env` file with API credentials is already protected by `.gitignore` and won't be committed! ✅

## Step 3: Create Initial Commit

```bash
git commit -m "Initial commit: R2Y5 TeamGantt project analysis tools and status report"
```

## Step 4: Create GitHub Repository (Two Options)

### Option A: Using GitHub CLI (Recommended - Fastest)

If you have GitHub CLI installed:
```bash
gh repo create R2Y5-TeamGantt-Analysis --private --source=. --remote=origin --push
```

This will:
- Create a **private** repository on GitHub
- Set it as the remote origin
- Push your code automatically

### Option B: Manual Setup (GitHub Website)

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `R2Y5-TeamGantt-Analysis`
3. Description: `TeamGantt project tracking and analysis tools for R2Y5`
4. Select **Private** (to protect your project data)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **Create repository**

Then connect your local repo:
```bash
git remote add origin https://github.com/YOUR_USERNAME/R2Y5-TeamGantt-Analysis.git
git branch -M main
git push -u origin main
```

## Step 5: Verify Upload

```bash
git status
git remote -v
```

You should see:
```
origin  https://github.com/YOUR_USERNAME/R2Y5-TeamGantt-Analysis.git (fetch)
origin  https://github.com/YOUR_USERNAME/R2Y5-TeamGantt-Analysis.git (push)
```

## 🔒 Security Check

Verify your credentials are NOT in the repo:

```bash
git log --all --full-history -- .env
```

Should return nothing (empty). ✅

## 📝 Future Updates

When you want to save changes:

```bash
# 1. Pull latest (if working with team)
git pull

# 2. Check what changed
git status

# 3. Add your changes
git add .

# 4. Commit with a message
git commit -m "Updated status report with latest data"

# 5. Push to GitHub
git push
```

## 🔄 Quick Update Script

Want to automate updates? Add this to `scripts/update_and_commit.sh`:

```bash
#!/bin/bash
# Fetch fresh data, generate report, and commit

cd "/Users/5425855/Documents/Uoft Studying/Autoronto"

# Pull latest data
./scripts/fetch_teamgantt_data.sh

# Generate new report
python3 scripts/analyze_teamgantt.py

# Commit changes
git add data/ PROJECT_STATUS_REPORT.*
git commit -m "Updated report: $(date '+%Y-%m-%d %H:%M')"
git push

echo "✅ Report updated and pushed to GitHub!"
```

Then make it executable:
```bash
chmod +x scripts/update_and_commit.sh
```

## ⚠️ Important Notes

- ✅ `.env` is in `.gitignore` - your API token is safe
- ✅ Use **private** repository to protect project data
- ✅ Share repo access only with authorized team members
- 🔄 Re-run analysis script whenever you export fresh data

## 🎯 What Gets Committed?

**Included:**
- ✅ Scripts (fetch_teamgantt_data.sh, analyze_teamgantt.py)
- ✅ Reports (HTML & Markdown)
- ✅ README and documentation
- ✅ Exported data files (CSV/JSON)
- ✅ .gitignore

**Protected (NOT committed):**
- 🔒 .env (API credentials)
- 🔒 Any files matching patterns in .gitignore

---

Need help? Run `git status` anytime to see what's happening!
