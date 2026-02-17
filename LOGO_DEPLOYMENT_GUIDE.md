# DREX Deployment with Logo - Quick Guide

## Files to Upload to GitHub

### Required Files:
1. ✅ **drex_calculator.py** - Main application (updated with logo)
2. ✅ **lf_systems_logo.jpg** - Your LF Systems logo
3. ✅ **requirements.txt** - Python dependencies
4. ✅ **DEF_Fan_Curves.xlsx** - Fan performance data
5. ✅ **gitignore** - Git ignore file (rename to .gitignore)
6. ✅ **packages.txt** - System packages (empty)
7. ✅ **README.md** - Documentation

---

## Upload Steps

### 1. Go to Your Repository
https://github.com/usdtxdprinter-ux/drex-calculator

### 2. Delete Old Files
Click on each old file and delete:
- Old drex_calculator.py
- Old requirements.txt

### 3. Upload New Files
Click "Add file" → "Upload files"

Drag and drop ALL files from DREX_Enhanced folder:
- drex_calculator.py
- lf_systems_logo.jpg ⭐ NEW!
- requirements.txt
- DEF_Fan_Curves.xlsx
- gitignore
- packages.txt
- README.md

### 4. Commit Changes
- Write commit message: "Added LF Systems logo and dryer icon"
- Click "Commit changes"

### 5. Wait for Deployment
- Streamlit Cloud will auto-detect changes
- Wait 2-3 minutes for rebuild
- App will be live at: https://usdtxdprinter-ux-drex-calculator.streamlit.app

---

## What's New

### 🎨 Visual Updates:

1. **LF Systems Logo**
   - Displays your actual logo at top of page
   - Professional branding
   - Automatic fallback if logo file missing

2. **Dryer Icon** 🧺
   - Browser tab now shows laundry basket icon
   - More relevant than fire emoji
   - Helps identify the app in browser tabs

3. **Logo Position**
   - Left side: Your logo (300px width)
   - Right side: App title and description
   - Clean, professional layout

---

## Logo Details

**Filename:** lf_systems_logo.jpg  
**Type:** JPEG image  
**Display Width:** 300px  
**Location:** Top left of every page

The logo is your official LF Systems horizontal logo:
- Black "LF SYSTEMS" text
- LF icon on left
- "BY RM MANIFOLD" tagline below

---

## Fallback Behavior

If the logo file is missing or fails to load:
- App shows 🧺 emoji instead
- Text reads "By LF Systems - A Division of RM Manifold Group Inc."
- All functionality remains intact
- No errors displayed to user

---

## Testing Checklist

After deployment, verify:
- [ ] LF Systems logo displays correctly
- [ ] Browser tab shows 🧺 icon
- [ ] Logo is properly sized (not too big/small)
- [ ] All calculations still work
- [ ] Fan curve plot displays
- [ ] Gamma button works
- [ ] PDF downloads
- [ ] Manual diameter selection works

---

## Icon Options Used

**Page Icon:** 🧺 (Laundry basket - represents clothes dryer)

**Alternative icons you could use:**
- 🌀 (Cyclone - represents airflow)
- 💨 (Wind - represents exhaust)
- 🏭 (Factory - represents commercial)
- ♨️ (Hot springs - represents heat/dryer)

To change the icon, edit line 657 in drex_calculator.py:
```python
page_icon="🧺"  # Change this emoji
```

---

## Logo Tips

### Current Setup:
- Logo displays at 300px width
- Maintains aspect ratio
- Professional placement

### To Adjust Logo Size:
Edit line 665 in drex_calculator.py:
```python
st.image("lf_systems_logo.jpg", width=300)  # Change 300 to desired width
```

### To Center Logo:
Change column ratio on line 662:
```python
col1, col2 = st.columns([1, 3])  # Adjust [1, 3] ratio
```

---

## File Paths

All files should be in the root directory:
```
drex-calculator/
├── drex_calculator.py
├── lf_systems_logo.jpg ⭐ 
├── requirements.txt
├── DEF_Fan_Curves.xlsx
├── .gitignore
├── packages.txt
└── README.md
```

**Important:** Logo must be in same directory as drex_calculator.py!

---

## Troubleshooting

### Logo Not Showing?
1. Check filename is exactly: `lf_systems_logo.jpg`
2. Verify file uploaded to GitHub root directory
3. Check Streamlit Cloud logs for errors
4. Try hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

### Icon Not Showing?
- Browser cache issue - clear cache
- Wait a few minutes for deployment
- Icon shows in browser tab, not in page

### Need Different Logo?
- Replace lf_systems_logo.jpg with your new logo
- Keep the same filename
- Or update filename in code (line 665)

---

## Support

**Website:** www.lfsystems.net  
**GitHub:** github.com/usdtxdprinter-ux  
**App URL:** https://usdtxdprinter-ux-drex-calculator.streamlit.app

---

## Summary

✅ LF Systems logo added to header  
✅ Dryer icon (🧺) for browser tab  
✅ Professional branding throughout  
✅ Automatic fallback if logo missing  
✅ All features working  
✅ Ready to deploy!

Just upload all files and you're done! 🚀
