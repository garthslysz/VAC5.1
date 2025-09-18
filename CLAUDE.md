# VAC 5.1 - Veterans Affairs Canada Disability Rating System

## Project Overview
**VAC 5.1** is a comprehensive Veterans Affairs Canada disability assessment system implementing the 2019 Table of Disabilities (ToD 2019) framework. This system provides AI-powered disability rating assessments with full compliance to VAC bracketing and PCT rules.

### Key Features
- **VAC ToD 2019 Compliance**: Full implementation of Canada's official disability rating framework
- **AI-Powered Assessments**: OpenAI integration for intelligent condition evaluation
- **Bracketing & PCT Rules**: Proper handling of Medical Impairment overlaps and cross-chapter contributions
- **Quality of Life Integration**: Table 2.1 and 2.2 implementation for comprehensive ratings
- **Real-time Assessment**: Web-based interface for immediate disability evaluations
- **Data Integrity Auditing**: Comprehensive validation of rating table conversions

## Project Structure
```
gwsGPT/
├── CLAUDE.md                           # Project-specific instructions
├── README.md                          # Project documentation
├── start_local.sh                     # Local development server startup
├── convert_json_structure.py          # VAC ToD JSON conversion utility
├── audit_json_conversion.py           # Data integrity audit script
├── test_payload.json                  # Sample disability assessment data
├── prompts/
│   └── system_prompt.md              # AI assessment framework instructions
├── app_simplified/                    # Main application
│   ├── main.py                       # FastAPI backend entry point
│   ├── requirements.txt              # Python dependencies
│   ├── core/
│   │   ├── vac_data.py              # VAC ToD data loader
│   │   └── ai_client.py             # OpenAI integration
│   └── data/
│       └── rules/
│           ├── master2019ToD.json    # VAC ToD 2019 rating tables (converted)
│           └── master2019ToD_old.json # Original backup
└── ui/                               # Next.js frontend
    ├── package.json
    ├── pages/
    │   └── api/
    ├── components/
    └── styles/
```

## Technology Stack

### Backend (FastAPI + Python)
- **FastAPI**: High-performance API framework
- **Python 3.12**: Core runtime environment
- **OpenAI API**: AI-powered assessment engine
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for development

### Frontend (Next.js + TypeScript)
- **Next.js 13+**: React framework with app directory
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **React Hooks**: Modern state management

### Data & Configuration
- **VAC ToD 2019 JSON**: Comprehensive disability rating tables
- **JSON Schema Validation**: Data integrity assurance
- **Environment Configuration**: Flexible deployment settings

## Local Development Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn

### Quick Start
```bash
# Clone and navigate to project
cd /home/gslys/gwsGPT

# Start both backend and frontend services
./start_local.sh

# Frontend will be available at: http://localhost:3000
# Backend API will be available at: http://localhost:8000
```

### Individual Service Startup
```bash
# Backend only
cd app_simplified && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend only
cd ui && npm install && npm run dev
```

### Environment Configuration
```bash
# Backend (.env in app_simplified/)
OPENAI_API_KEY=your-openai-api-key-here
VAC_DATA_PATH=data/rules/master2019ToD.json

# Frontend (.env.local in ui/)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## VAC ToD 2019 Framework Implementation

### Core Assessment Components
1. **Medical Impairment (MI)**: Table-based rating from relevant body system
2. **Quality of Life (QoL)**: Single rating using Table 2.1 Level descriptors and Table 2.2 conversion
3. **Disability Assessment (DA)**: MI + QoL final calculation

### Overlap Resolution Rules
- **Bracketing**: Multiple same-chapter conditions combine into single MI and QoL
- **PCT (Pensionable Contribution Table)**: Cross-chapter contributors modify MI only using Table 3.1
- **Psychiatry (Ch.21)**: All psychiatric conditions bracket together; PCT only for non-Ch.21 contributors

### Assessment Process
1. Condition entitlement and chronicity verification
2. Table mapping from master2019ToD.json
3. MI rating determination with proper descriptor quotation
4. Bracketing/PCT application as appropriate
5. QoL Level assessment using Table 2.1 criteria
6. Final DA calculation: MI + QoL
7. Partial entitlement fraction application if applicable

## Data Management

### JSON Structure Conversion
The system includes utilities to convert VAC ToD data between structures:

```bash
# Convert chapter-based to flat structure
python convert_json_structure.py

# Audit conversion integrity
python audit_json_conversion.py
```

### Current Data Status
- **Conditions**: 14 loaded from VAC ToD 2019
- **Rating Tables**: 14 accessible via flat structure
- **Data Integrity**: 100% preserved from original chapter structure

## API Endpoints

### Backend API Routes
```bash
GET  /health              # Health check endpoint
POST /api/vac/assess      # Disability assessment submission
GET  /api/vac/conditions  # Available conditions list
GET  /api/vac/tables      # Rating tables access
```

### Assessment Request Format
```json
{
  "message": "Entitled condition details, medical questionnaire findings, prior assessments, and quality of life statement..."
}
```

## Azure Deployment Configuration

### Resource Naming (VAC 5.1)
- **Resource Group**: `VAC51-rg`
- **Backend API**: `vac51-api.azurewebsites.net`
- **Frontend**: `vac51-frontend.azurestaticapps.net`
- **Location**: `Canada Central`

### Deployment Commands
```bash
# Backend deployment
zip -r backend-deploy.zip app_simplified/ prompts/ -x "*.pyc" "*__pycache__*"
az webapp deploy --resource-group VAC51-rg --name vac51-api --src-path backend-deploy.zip --type zip

# Frontend build and deployment
cd ui && npm install && npm run build && cd ..
# Manual upload to Azure Static Web App
```

### Environment Variables (Azure)
```bash
# Backend App Service Configuration
OPENAI_API_KEY=your-production-openai-key
VAC_DATA_PATH=data/rules/master2019ToD.json
WEBSITES_PORT=8000
SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Frontend Static Web App
NEXT_PUBLIC_API_URL=https://vac51-api.azurewebsites.net
```

## Testing & Quality Assurance

### Sample Test Data
```json
{
  "condition": "Chronic Low Back Pain (CLBP)",
  "clinical_findings": {
    "pain_pattern": "Daily axial low back pain with 1-2 flares/week",
    "functional_tolerances": {
      "sitting": "30-45 minutes",
      "standing": "20-30 minutes",
      "walking": "~400 meters"
    },
    "range_of_motion": {
      "lumbar_flexion": "45°",
      "extension": "15°",
      "lateral_flexion": "20°/20°"
    }
  }
}
```

### Data Integrity Verification
```bash
# Run comprehensive audit
python audit_json_conversion.py

# Expected output: ✅ ALL AUDITS PASSED!
```

## System Capabilities

### Current Assessment Scope
- **Musculoskeletal Conditions**: Chapter 17 (Spine, back pain, ROM impairments)
- **Psychiatric Conditions**: Chapter 21 (PTSD, anxiety, depression)
- **Cross-chapter Integration**: PCT application for overlapping conditions
- **Quality of Life**: Comprehensive Level 1-3 assessment with Table 2.2 conversion

### AI Assessment Features
- Evidence-based reasoning with direct quotation from VAC tables
- Proper bracketing and PCT rule application
- Quality of Life impact evaluation
- Compliance with VAC ToD 2019 methodology
- Standardized output format with audit trail

## Troubleshooting

### Common Issues
1. **Module Import Errors**: Ensure Python 3.12+ and all requirements installed
2. **Frontend Build Failures**: Check Node.js version (18+) and npm dependencies
3. **VAC Data Loading**: Verify master2019ToD.json structure integrity
4. **API Connection**: Confirm environment variables and CORS configuration

### Development Tips
- Use `./start_local.sh` for consistent service startup
- Monitor backend logs for VAC data loading confirmation
- Test with provided `test_payload.json` for validation
- Run audit scripts after any JSON structure modifications

## Contributing

### Code Standards
- Follow FastAPI best practices for backend development
- Use TypeScript strict mode for frontend development
- Maintain VAC ToD 2019 compliance in all assessment logic
- Preserve data integrity in any rating table modifications

### Testing Requirements
- Validate all assessment calculations against VAC ToD 2019 manual
- Test bracketing and PCT scenarios comprehensively
- Verify Quality of Life Level assignments with Table 2.1/2.2
- Audit any data structure changes for integrity

---

## Project History & Context

**VAC 5.1** represents the evolution of Veterans Affairs Canada digital assessment tools, building on previous iterations (VAC 1.7, VAC 1.9) with enhanced AI integration and comprehensive ToD 2019 implementation.

### Key Improvements
- Complete VAC ToD 2019 framework compliance
- Robust JSON structure conversion with integrity auditing
- Enhanced AI prompt engineering for accurate assessments
- Streamlined development and deployment processes
- Comprehensive documentation and troubleshooting guides

*This project serves veterans by providing accurate, consistent, and compliant disability assessments while maintaining the highest standards of data integrity and regulatory compliance.*