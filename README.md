# VAC 5.1 - Veterans Affairs Canada Disability Rating System

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-13+-black.svg)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://typescriptlang.org)

A comprehensive Veterans Affairs Canada disability assessment system implementing the **2019 Table of Disabilities (ToD 2019)** framework with AI-powered evaluation capabilities.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- OpenAI API Key

### Local Development
```bash
# Clone the repository
git clone https://github.com/garthslysz/VAC5.1.git
cd VAC5.1

# Start both services with one command
./start_local.sh

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

## 📋 Features

### ✅ VAC ToD 2019 Compliance
- **Full Framework Implementation**: Complete adherence to Veterans Affairs Canada's official 2019 Table of Disabilities
- **Bracketing Rules**: Proper handling of same-chapter condition overlaps
- **PCT Integration**: Cross-chapter Pensionable Contribution Table calculations
- **Quality of Life Assessment**: Table 2.1 and 2.2 implementation for comprehensive ratings

### 🤖 AI-Powered Assessments
- **OpenAI Integration**: Intelligent condition evaluation and rating determination
- **Evidence-Based Analysis**: Direct quotation and mapping from VAC rating tables
- **Standardized Output**: Consistent format with audit trail and compliance verification
- **Real-Time Processing**: Immediate disability assessment results

### 📊 Data Integrity
- **14 Conditions Loaded**: Comprehensive coverage from VAC ToD 2019
- **14 Rating Tables**: Direct access to all assessment criteria
- **Conversion Auditing**: 100% data integrity verification from original sources
- **Backup & Recovery**: Original data preservation with rollback capability

## 🏗️ System Architecture

### Backend (FastAPI + Python)
```
app_simplified/
├── main.py              # FastAPI application entry point
├── core/
│   ├── vac_data.py      # VAC ToD data loader and management
│   └── ai_client.py     # OpenAI API integration
├── data/
│   └── rules/
│       ├── master2019ToD.json     # VAC ToD 2019 (converted structure)
│       └── master2019ToD_old.json # Original backup
└── requirements.txt     # Python dependencies
```

### Frontend (Next.js + TypeScript)
```
ui/
├── pages/               # Next.js pages and API routes
├── components/          # React components
├── styles/             # CSS and styling
├── types/              # TypeScript definitions
└── package.json        # Node.js dependencies
```

### Supporting Scripts
```
├── convert_json_structure.py  # VAC data structure conversion
├── audit_json_conversion.py   # Data integrity verification
├── test_payload.json         # Sample assessment data
└── prompts/
    └── system_prompt.md      # AI assessment instructions
```  

## 🔧 Configuration

### Environment Variables

#### Backend Configuration
```bash
# app_simplified/.env
OPENAI_API_KEY=your-openai-api-key-here
VAC_DATA_PATH=data/rules/master2019ToD.json
```

#### Frontend Configuration
```bash
# ui/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development Services
```bash
# Backend development server
cd app_simplified
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend development server
cd ui
npm install && npm run dev
```

## 📚 VAC ToD 2019 Framework

### Assessment Process
1. **Condition Verification**: Entitlement and chronicity confirmation
2. **Table Mapping**: Proper chapter and table selection from master2019ToD.json
3. **Medical Impairment**: Rating determination with descriptor quotation
4. **Overlap Resolution**: Bracketing or PCT application as appropriate
5. **Quality of Life**: Level assessment using Table 2.1 criteria
6. **Final Calculation**: MI + QoL with partial entitlement adjustments

### Core Components

#### Medical Impairment (MI)
- Table-based rating from relevant body system chapter
- Direct descriptor quotation from official VAC tables
- Evidence-to-criteria mapping with rationale

#### Quality of Life (QoL)
- Single rating per condition using Table 2.1 descriptors
- Level 1-3 assessment with specific criteria
- Table 2.2 conversion for MI-band adjustment

#### Disability Assessment (DA)
- Final calculation: MI + QoL
- Partial entitlement fraction application
- 100% payable cap enforcement

### Overlap Rules

#### Bracketing (Same Chapter)
- Multiple conditions within same chapter combine
- Single MI and single QoL for bracketed group
- Applied to all non-psychiatric chapters when applicable

#### PCT (Cross Chapter)
- Cross-chapter or non-entitled contributors
- Modifies MI only using Table 3.1 calculations
- Never applied to QoL ratings

#### Psychiatry Special Rules (Chapter 21)
- All psychiatric diagnoses bracket together
- PCT only for non-Chapter 21 contributors
- Comprehensive mental health assessment approach

## 🧪 Testing & Validation

### Sample Assessment Data
The project includes `test_payload.json` with realistic disability assessment scenarios:

```json
{
  "message": "Chronic Low Back Pain (CLBP) — entitlement established.\nDaily axial low back pain, 1-2 flares/week...\nLumbar flexion: 45°, Extension: 15°...\nPain impacts daily activities but remains independent..."
}
```

### Data Integrity Verification
```bash
# Run comprehensive audit
python audit_json_conversion.py

# Expected output:
# ✅ ALL AUDITS PASSED!
# ✅ Data integrity verified - no adjudication data lost
# ✅ Conversion successful and safe to use
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Assessment submission
curl -X POST http://localhost:8000/api/vac/assess \
  -H "Content-Type: application/json" \
  -d @test_payload.json

# View loaded conditions
curl http://localhost:8000/api/vac/conditions
```

## 🌐 Deployment

### Azure Configuration
- **Resource Group**: `VAC51-rg`
- **Backend API**: `vac51-api.azurewebsites.net`
- **Frontend**: `vac51-frontend.azurestaticapps.net`
- **Region**: Canada Central

### Deployment Commands
```bash
# Backend deployment
zip -r backend-deploy.zip app_simplified/ prompts/ -x "*.pyc" "*__pycache__*"
az webapp deploy --resource-group VAC51-rg --name vac51-api --src-path backend-deploy.zip --type zip

# Frontend deployment
cd ui && npm install && npm run build && cd ..
# Upload build/ directory to Azure Static Web App
```

### Production Environment Variables
```bash
# Azure App Service (Backend)
OPENAI_API_KEY=production-key
VAC_DATA_PATH=data/rules/master2019ToD.json
WEBSITES_PORT=8000

# Azure Static Web App (Frontend)
NEXT_PUBLIC_API_URL=https://vac51-api.azurewebsites.net
```

## 🔍 API Reference

### Endpoints

#### GET /health
Health check endpoint
```json
{
  "status": "healthy",
  "conditions_loaded": 14,
  "rating_tables_loaded": 14
}
```

#### POST /api/vac/assess
Disability assessment submission
```json
{
  "message": "Complete assessment request with condition details, clinical findings, and quality of life impact..."
}
```

#### GET /api/vac/conditions
List available conditions
```json
{
  "17_ROM_spine": {
    "name": "Spine Range of Motion Impairment",
    "chapter": "17",
    "keywords": ["spine", "back", "musculoskeletal"]
  }
}
```

## 🔰 Troubleshooting

### Common Issues

#### Backend Service Issues
```bash
# Check service status
curl -I http://localhost:8000/health

# View VAC data loading
# Look for: "🏥 Conditions: 14" and "📋 Rating tables: 14" in startup logs
```

#### Frontend Build Issues
```bash
# Clear cache and rebuild
cd ui
rm -rf .next node_modules package-lock.json
npm install && npm run dev
```

#### VAC Data Loading Issues
```bash
# Verify JSON structure integrity
python audit_json_conversion.py

# Re-convert if necessary
python convert_json_structure.py
```

### Development Tips
- Use `./start_local.sh` for consistent service startup
- Monitor backend logs for VAC data loading confirmation
- Test assessments with `test_payload.json` for validation
- Run integrity audits after any data modifications

## 🤝 Contributing

### Development Standards
- **VAC Compliance**: Maintain strict adherence to ToD 2019 framework
- **Data Integrity**: Preserve all adjudication data in modifications
- **Testing**: Validate all assessment logic against VAC manual
- **Documentation**: Update guides for any architectural changes

### Code Quality
- Python: Follow PEP 8 standards and FastAPI best practices
- TypeScript: Use strict mode and maintain type safety
- Testing: Comprehensive coverage for assessment calculations
- Validation: Audit all data structure changes

## 📊 Project Status

### Current Capabilities
- ✅ VAC ToD 2019 framework fully implemented
- ✅ 14 conditions loaded and accessible
- ✅ 14 rating tables with complete data integrity
- ✅ AI-powered assessments with bracketing/PCT rules
- ✅ Quality of Life integration (Tables 2.1/2.2)
- ✅ Real-time web interface
- ✅ Azure deployment ready

### Assessment Coverage
- **Musculoskeletal**: Chapter 17 (spine, back pain, ROM impairments)
- **Psychiatric**: Chapter 21 (PTSD, anxiety, depression)
- **Cross-Chapter**: PCT application for overlapping conditions
- **Quality of Life**: Comprehensive Level 1-3 assessment

## 📄 License

This project is developed for Veterans Affairs Canada disability assessment purposes. All VAC Table of Disabilities data remains property of Veterans Affairs Canada.

## 🆘 Support

For technical issues or questions:
- Check troubleshooting section in documentation
- Review Azure deployment logs for production issues
- Verify VAC data integrity with included audit scripts
- Validate assessment logic against ToD 2019 manual

---

**VAC 5.1** represents the state-of-the-art in digital disability assessment tools, combining regulatory compliance with modern AI capabilities to serve Canadian veterans with accuracy and consistency.

---

*Last updated: September 18, 2025*