# 🚨 URGENT: API Token Security Fix

## Problem

Your TeamGantt API token was accidentally hardcoded in `scripts/populate_test_project_hours.py` and committed to git history (commit `a169c7c`).

**Token exposed:** `<REDACTED_API_TOKEN>`

---

## ✅ Fixes Applied

### 1. Script Fixed
- ✅ Removed hardcoded API token
- ✅ Now reads from `.env` file
- ✅ Changed `DRY_RUN = False` to `DRY_RUN = True` (safer default)
- ✅ Added validation for missing credentials

### 2. `.env.example` Created
- ✅ Template file for API credentials
- ✅ Safe to commit (no actual secrets)

### 3. Instructions Updated
- ✅ Added `.env` setup section
- ✅ Added security warnings
- ✅ Added comprehensive troubleshooting
- ✅ Added file structure diagram

---

## 🚨 IMMEDIATE ACTION REQUIRED

Since git commits contain the exposed token, you have TWO options:

### Option A: Repository NOT Pushed Yet (EASIEST)

**Status:** ✅ Your repo shows "Your branch is up to date with 'origin/main'" but this might be local only.

**Check if actually pushed:**
```bash
git remote -v
# If origin exists and you've pushed, use Option B
# If no remote or never pushed, use Option A
```

**If NOT pushed to any remote (GitHub/GitLab/etc):**

```bash
# 1. Check remotes
git remote -v

# 2. If you see a remote URL, check what's there
git ls-remote origin

# 3. If nothing is pushed or no remote exists:
# Just commit the fixes and you're done!
git add .
git commit -m "Security: Remove hardcoded API token, add .env support"

# No need to rewrite history if never pushed!
```

### Option B: Repository Already Pushed (MORE COMPLEX)

**If you've already pushed to GitHub/GitLab:**

```bash
# 1. FIRST: Rotate your API token immediately!
#    - Log into TeamGantt
#    - Settings → API
#    - Generate NEW token
#    - Update .env file

# 2. Create backup
git branch backup-before-rewrite

# 3. Remove token from history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch scripts/populate_test_project_hours.py' \
  --prune-empty --all

# 4. Clean up
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Add cleaned file
git add scripts/populate_test_project_hours.py .env.example scripts/INSTRUCTIONS_POPULATE_HOURS.md
git commit -m "Security: Remove hardcoded API token, add .env support"

# 6. Force push (THIS WILL REWRITE REMOTE HISTORY!)
git push --force-with-lease origin main

# 7. Notify team members to re-clone or reset
echo "⚠️  Tell team to: git fetch origin && git reset --hard origin/main"
```

---

## ⚡ Quick Decision Tree

```
Did you push to GitHub/GitLab/etc?
├─ NO  → Just commit the fixes, you're done!
│        git add .
│        git commit -m "Security: Remove hardcoded API token, add .env support"
│
└─ YES → Must rewrite history AND rotate token immediately!
         1. Rotate token in TeamGantt NOW
         2. Use git filter-branch (see Option B above)
         3. Force push to remote
         4. Update .env with new token
```

---

## 📋 Checklist

- [  ] Determine if repo was pushed to remote (`git remote -v` and `git ls-remote origin`)
- [  ] If pushed: **ROTATE API TOKEN IMMEDIATELY** in TeamGantt Settings
- [  ] If pushed: Run git filter-branch to clean history
- [  ] If pushed: Force push to remote
- [  ] If NOT pushed: Just commit the fixes
- [  ] Create `.env` file with credentials
- [  ] Test the script in DRY RUN mode
- [  ] Verify token works with new setup
- [  ] If pushed: Notify team members to re-sync

---

## 🔒 Prevention Going Forward

### Already Set Up:
- ✅ `.env` in `.gitignore`
- ✅ `.env.example` as template
- ✅ Script reads from environment
- ✅ Validation for missing credentials

### Best Practices:
- **NEVER** hardcode secrets in code
- **ALWAYS** use environment variables or `.env` files
- **ALWAYS** check commits before pushing
- **ROTATE** tokens immediately if exposed
- Use git hooks to prevent committing secrets (optional advanced step)

---

## 📞 Need Help?

**If unsure whether repo was pushed:**
```bash
git remote -v
git log --all --decorate --oneline --graph
```

**Common scenarios:**
- "No remote configured" → You're safe, just commit fixes
- "origin → github.com/..." → Check if you've pushed (`git ls-remote origin`)
- "fatal: 'origin' does not appear to be a git repository" → You're safe, just commit

---

**Created:** February 14, 2026  
**Status:** 🚨 URGENT - Action Required
