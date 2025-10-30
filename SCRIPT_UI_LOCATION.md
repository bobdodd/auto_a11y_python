# Where to Find Script Management UI

## 🎯 Location: Page Detail View

The script management interface is accessed **from individual pages**, not from a top-level menu.

### How to Access:

1. **Navigate to a Page:**
   ```
   Dashboard → Projects → [Your Project] → [Your Website] → [Any Page]
   ```

2. **Look for the Scripts Button:**
   On the page detail view, you'll see action buttons in the top-right:
   ```
   [Run Test] [Edit] [Scripts] ← Green button
   ```

3. **Click the Scripts Button:**
   This takes you to: `/scripts/page/{page_id}/scripts`

## 📍 Exact Button Location

The **green "Scripts" button** appears:
- **Next to** the "Edit" button
- **Below** the page title and URL
- **In the** page actions area (top-right of page)

**Visual layout:**
```
┌─────────────────────────────────────────────────────┐
│ Home > Project > Website > Page Title               │
│                                                     │
│ Page Title                    [Run Test] [Edit] [Scripts] │
│ https://example.com/page                           │
└─────────────────────────────────────────────────────┘
```

## ✅ After Clicking Scripts

You'll see the **Script Management Page** with:
- List of all scripts for this page
- "Create New Script" button (top-right)
- Table showing existing scripts
- Edit/Delete/Toggle buttons for each script

## 🚀 Quick Test

1. **Restart your app** (if running):
   ```bash
   # Stop with Ctrl+C
   python run.py
   ```

2. **Open browser:**
   ```
   http://localhost:5001
   ```

3. **Navigate to any page:**
   - Click on a project
   - Click on a website
   - Click on any page in the list

4. **Look for the green "Scripts" button** next to "Edit"

## 🔍 Troubleshooting

### Don't See the Scripts Button?

**Check 1: Restart the app**
```bash
# Stop the app (Ctrl+C)
python run.py
```

**Check 2: Check the Flask startup logs**
Look for:
```
Registered blueprint: scripts at /scripts
```

**Check 3: Verify you're on a page detail view**
- URL should be: `/pages/{page_id}`
- Should see "Run Test" and "Edit" buttons
- If yes, "Scripts" should be right next to "Edit"

**Check 4: Clear browser cache**
```
Ctrl+Shift+R (hard refresh)
or
Clear cache and reload
```

**Check 5: Check browser console for errors**
```
F12 → Console tab
Look for any JavaScript errors
```

### Still Don't See It?

**Verify the templates were updated:**
```bash
cd /Users/bob3/Desktop/auto_a11y_python
git status
git log --oneline -5
```

You should see recent commits like:
- "feat: Add comprehensive GUI for page setup script management"
- "fix: Add Scripts button to view_enhanced template"

**Pull latest changes:**
```bash
git pull origin main
```

**Check file contents:**
```bash
grep -n "Scripts" auto_a11y/web/templates/pages/view.html
grep -n "Scripts" auto_a11y/web/templates/pages/view_enhanced.html
```

Both should show lines with the Scripts button.

## 📋 What You Can Do

Once you find the Scripts button and click it:

### ✅ On the Script List Page:
- See all scripts for the current page
- See website-wide scripts (read-only)
- Click "Create New Script" (top-right, blue button)
- Edit existing scripts (pencil icon)
- Delete scripts (trash icon)
- Enable/disable scripts (toggle icon)

### ✅ On the Create Script Page:
- Fill in script name and description
- Check "Test BEFORE" and/or "Test AFTER"
- Add steps with the step builder
- Configure state validation
- Save the script

### ✅ After Creating a Script:
- Go back to the page view
- Click "Run Test"
- Script runs automatically
- Multiple test results created (if multi-state enabled)

## 🎨 Visual Guide

### Page View (where Scripts button is):
```
┌───────────────────────────────────────────────────┐
│ 🏠 Dashboard > Project > Website > Page          │
├───────────────────────────────────────────────────┤
│                                                   │
│  Page Title                    [▶ Run Test]      │
│  https://example.com/page      [✏️ Edit]          │
│                                [💻 Scripts]  ← HERE │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │ Test Results                                │ │
│  │ Violations: 10  Warnings: 5  Passes: 45    │ │
│  └─────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────┘
```

### Script Management Page (after clicking Scripts):
```
┌───────────────────────────────────────────────────┐
│ 🏠 > Project > Website > Page > Scripts          │
├───────────────────────────────────────────────────┤
│                                                   │
│  Page Setup Scripts        [+ Create New Script] │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │ Page-Specific Scripts                  (2)  │ │
│  ├─────────────────────────────────────────────┤ │
│  │ Name               Steps    Actions          │ │
│  │ Cookie Banner      2 steps  [👁️] [✏️] [🗑️]   │ │
│  │ Open Modal         3 steps  [👁️] [✏️] [🗑️]   │ │
│  └─────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────┘
```

### Create Script Page (after clicking Create New Script):
```
┌───────────────────────────────────────────────────┐
│ 🏠 > Project > Website > Page > Scripts > Create │
├───────────────────────────────────────────────────┤
│                                                   │
│  Create Page Setup Script                        │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │ Basic Information                           │ │
│  │ Name: [_____________________]               │ │
│  │ Description: [_______________]              │ │
│  │ ☑ Script Enabled                            │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │ Multi-State Testing                         │ │
│  │ ☐ Test BEFORE executing script              │ │
│  │ ☑ Test AFTER executing script               │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │ Script Steps                                │ │
│  │ [+ Add Step]                                │ │
│  └─────────────────────────────────────────────┘ │
│                                                   │
│  [Cancel]                      [Create Script]  │
└───────────────────────────────────────────────────┘
```

## 💡 Why It's Page-Level

Scripts are associated with **specific pages** because:
- Different pages need different setup (some have cookie banners, some don't)
- Scripts are executed when testing **that specific page**
- Website-wide scripts are shown but managed at the website level
- This keeps scripts organized and easy to find

## 🎯 Quick Access Checklist

To access script management:
- [ ] App is running (`python run.py`)
- [ ] Browser open to `http://localhost:5001`
- [ ] Navigated to: Project → Website → **Page** (not stopped at website)
- [ ] On page detail view (see "Run Test" button)
- [ ] Look for green "Scripts" button next to "Edit"
- [ ] Click "Scripts" button

## 📞 Still Can't Find It?

If you've followed all the above and still don't see the Scripts button:

1. **Check your git status:**
   ```bash
   git status
   git log --oneline -1
   ```
   Should show: "fix: Add Scripts button to view_enhanced template"

2. **Check the app is using the new code:**
   - Stop the app
   - `git pull origin main` (just to be sure)
   - Start the app again
   - Hard refresh browser (Ctrl+Shift+R)

3. **Check Flask logs:**
   Look for the line about registering the scripts blueprint

4. **Try a direct URL:**
   ```
   http://localhost:5001/scripts/page/YOUR_PAGE_ID/scripts
   ```
   Replace YOUR_PAGE_ID with an actual page ID from your database

5. **Check if page exists:**
   Make sure you have at least one page in your database to test with

---

**The Scripts button is there!** It's on the page detail view, next to the Edit button. After restarting the app and refreshing your browser, you should see it.

If you still have issues, let me know what you see on the page detail view and I can help debug further!
