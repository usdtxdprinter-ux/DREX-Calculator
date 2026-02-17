# DREX - Commercial Dryer Exhaust Calculator

![DREX Logo](https://img.shields.io/badge/DREX-Dryer%20Exhaust%20Calculator-003366)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)

**Developed by US Draft Co.**

A comprehensive web-based sizing program for commercial dryer exhaust systems. DREX handles up to 20 clothes dryers, performs complete duct design calculations, optimizes manifold sizing, and generates professional documentation.

🌐 **[Live Demo](https://your-app.streamlit.app)** ← *Deploy and update this link*

---

## 🚀 Features

- ✅ **Multiple Dryer Support** - Handle up to 20 commercial dryers
- ✅ **Copy Function** - Quickly add multiple identical dryers
- ✅ **Duct Design Calculations** - ASHRAE standard pressure loss equations
- ✅ **Location Lookup** - Automatic zip code to elevation conversion
- ✅ **Manifold Optimization** - Auto-size for 1.0 IN WC maximum
- ✅ **Pressure Loss Warnings** - Alerts when connector > 0.25 IN WC
- ✅ **Lint Collector Support** - Add custom K-values for accessories
- ✅ **DEF Fan Selection** - Automatic selection from performance curves
- ✅ **Professional Reports** - Generate PDF reports and CSI specifications

---

## 📊 Quick Start

### Try it Online
Visit the live demo: **[DREX Calculator](https://your-app.streamlit.app)**

### Run Locally

```bash
# Clone the repository
git clone https://github.com/yourusername/drex-calculator.git
cd drex-calculator

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run drex_calculator.py
```

The app will open in your browser at `http://localhost:8501`

---

## 🎯 How It Works

### 1. Project Information
- Enter project name and location (zip code)
- Automatic elevation lookup for accurate calculations

### 2. Add Dryers
- Specify CFM, outlet diameter, connector details
- Use copy function for multiple identical units
- Add up to 20 dryers total

### 3. Configure Manifold
- Enter length and fittings
- Choose automatic optimization or manual diameter
- System optimizes for 1.0 IN WC maximum

### 4. Review Results
- View complete system calculations
- Receive warnings for high pressure losses
- See recommended DEF fan model
- Download PDF report and CSI specification

---

## 📐 Design Criteria

- **Connector Maximum**: 0.25 IN WC (warning threshold)
- **Manifold Maximum**: 1.0 IN WC (optimization target)
- **No 90° Tees**: Only lateral tees per code
- **Air Density**: 0.075 lb/ft³ (dryer exhaust standard)

---

## 🔧 Calculations

Uses the standard ASHRAE duct design equation:

```
ΔP = (0.3 × L/D + ΣK) × ρ × (V/1096.2)²
```

Where:
- **L** = Length (feet)
- **D** = Diameter (feet)
- **K** = Fitting loss coefficients
- **ρ** = Air density (lb/ft³)
- **V** = Velocity (FPM)

### K-Values

| Fitting | K-Value |
|---------|---------|
| 90° Elbow (smooth) | 0.75 |
| 90° Elbow (standard) | 1.3 |
| 45° Elbow | 0.35 |
| Lateral Tee (branch) | 1.0 |
| Lateral Tee (straight) | 0.4 |
| Entry/Exit | 0.5/1.0 |

---

## 🌬️ DEF Fan Models

| Model | Max CFM | Max SP |
|-------|---------|--------|
| DEF04 | 540 | 1.0 IN WC |
| DEF08 | 970 | 1.75 IN WC |
| DEF015 | 1,860 | 2.0 IN WC |
| DEF025 | 2,480 | 2.0 IN WC |
| DEF035 | 4,100 | 2.0 IN WC |
| DEF050 | 5,850 | 2.0 IN WC |

---

## 📱 Deploy to Streamlit Cloud

### Step 1: Fork this Repository
Click the "Fork" button at the top right of this page.

### Step 2: Sign up for Streamlit Cloud
Visit [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.

### Step 3: Deploy
1. Click "New app"
2. Select your forked repository
3. Set main file: `drex_calculator.py`
4. Click "Deploy"

Your app will be live in minutes!

---

## 📄 Generated Documents

### PDF Report Includes:
- Project information
- System summary
- Individual dryer details
- Manifold specifications
- Fan selection with justification
- Warnings and recommendations

### CSI Specification Includes:
- Section 11 31 00 format
- General requirements
- Product specifications
- Installation guidelines
- Quality assurance
- Testing procedures

---

## 🏗️ Code Compliance

Supports compliance with:
- **International Mechanical Code (IMC)**
- **NFPA 211** - Chimneys, Fireplaces, Vents, and Solid Fuel-Burning Appliances
- **Local building codes** and fire marshal requirements

---

## 💡 Example Use Cases

### Small Laundromat
- 5 dryers @ 200 CFM each
- Short connectors (8-10 feet)
- Optimized manifold
- **Result**: DEF08 or DEF015

### Large Commercial Facility
- 15 dryers @ 300 CFM each
- Longer manifold run (150 feet)
- Individual lint collectors
- **Result**: DEF035 or DEF050

### Multi-Story Building
- 20 dryers on multiple floors
- Vertical manifold routing
- High static pressure
- **Result**: May require multiple systems

---

## 🛠️ Technology Stack

- **Python 3.8+** - Core language
- **Streamlit 1.28+** - Web framework
- **Pandas** - Data manipulation
- **NumPy** - Numerical calculations
- **ReportLab** - PDF generation
- **OpenPyXL** - Excel file reading
- **Requests** - API calls for location lookup

---

## 📚 Documentation

- [Quick Start Guide](QUICK_START.md) - Getting started
- [Design Guidelines](DESIGN_GUIDELINES.md) - Engineering best practices
- [Technical Documentation](TECHNICAL.md) - Detailed calculations

---

## ⚠️ Troubleshooting

### No Suitable Fan Found
- Reduce system pressure loss
- Increase manifold diameter
- Shorten connector lengths
- Consider splitting into multiple systems

### Connector Warning (> 0.25 IN WC)
- Reduce connector length
- Increase duct diameter
- Minimize fittings
- Use smooth elbows

### Location Lookup Fails
- Verify 5-digit US zip code
- Check internet connection
- Calculator continues without location data

---

## 🤝 Contributing

This is a proprietary application developed for US Draft Co. For questions or support, please contact the development team.

---

## 📞 Support

For technical support:
- **Developer**: Tim Engineering
- **Organization**: US Draft Co.
- **Documentation**: See included guides

---

## 📜 License

© 2026 US Draft Co. All rights reserved.

Proprietary software for commercial dryer exhaust system design.

---

## 🎯 Version History

### v1.0.0 (February 2026)
- Initial release
- Support for up to 20 dryers
- Automatic manifold optimization
- DEF fan selection
- PDF and CSI report generation
- Chatbot-style interface

---

## 🌟 Key Benefits

✅ **Time Savings** - Minutes instead of hours for manual calculations  
✅ **Accuracy** - Industry-standard ASHRAE equations  
✅ **Code Compliance** - Built-in validation and warnings  
✅ **Professional Output** - PDF reports and CSI specifications  
✅ **Ease of Use** - Chatbot-style step-by-step interface  
✅ **Optimization** - Automatic manifold sizing  
✅ **Flexibility** - 1-20 dryers, any configuration  

---

**Made with ❤️ by US Draft Co.**
