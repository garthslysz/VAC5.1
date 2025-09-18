# VAC Assessment UI - Professional Frontend Interface

A professional Next.js frontend for Veterans Affairs Canada disability assessment adjudicators.

## Features

### 🏥 **Professional Adjudicator Dashboard**
- Real-time case statistics and metrics
- Quick actions for common workflows
- System health monitoring
- Recent cases overview

### 💬 **Assessment Chat Interface** 
- AI-powered VAC assessment conversations
- Function calling integration with backend API
- Professional conversation management
- Case context preservation
- Quick action buttons for common requests

### 📄 **Document Management**
- Drag-and-drop file uploads (PDF, DOCX, TXT, JSON)
- Automatic text extraction and medical condition detection
- File processing status and progress tracking
- Integration with case management

### 📋 **Case Management**
- Comprehensive case listing and filtering
- Status tracking (pending, in-progress, completed, review)
- Priority management (urgent, high, normal, low)
- Progress visualization
- Quick access to chat and documents

### 📖 **VAC ToD Browser**
- Browse Table of Disabilities 2019 by chapter
- Search conditions and assessment criteria
- Symptom matching and condition lookup
- Professional reference interface

### 📊 **Reports & Analytics**
- Assessment performance metrics
- Disability rating distribution analysis
- Processing time tracking
- Condition frequency analysis
- Monthly performance trends
- Export and print capabilities

## Technology Stack

- **Frontend**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with VAC government theme
- **UI Components**: Headless UI with Hero Icons
- **API Client**: Axios with TypeScript interfaces
- **File Upload**: React Dropzone
- **Forms**: React Hook Form

## Quick Start

### Prerequisites
- Node.js 18+ installed
- Your VAC Assessment API running on `http://localhost:8000`

### Installation

```bash
cd ui

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local

# Start development server
npm run dev
```

### Environment Configuration

Create `.env.local` in the `ui` directory:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Custom branding
NEXT_PUBLIC_APP_NAME="VAC Assessment System"
NEXT_PUBLIC_VERSION="1.0.0"
```

### Development Commands

```bash
# Start development server (with hot reload)
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Export static build
npm run export
```

## Project Structure

```
ui/
├── app/                          # Next.js 13+ app directory
│   ├── globals.css              # Global styles with VAC theme
│   ├── layout.tsx               # Root layout with providers
│   ├── page.tsx                 # Dashboard home page
│   ├── providers.tsx            # Context providers
│   ├── chat/page.tsx            # Assessment chat interface
│   ├── upload/page.tsx          # Document upload interface
│   ├── cases/page.tsx           # Case management interface
│   ├── tod/page.tsx             # VAC ToD browser interface
│   └── reports/page.tsx         # Reports and analytics
├── components/                   # Reusable components
│   ├── Sidebar.tsx              # Main navigation sidebar
│   └── DashboardLayout.tsx      # Common layout wrapper
├── lib/                         # Utility libraries
│   └── api.ts                   # API client with TypeScript
├── public/                      # Static assets
├── package.json                 # Dependencies and scripts
├── tailwind.config.js           # Tailwind CSS configuration
├── tsconfig.json               # TypeScript configuration
└── next.config.js              # Next.js configuration
```

## Key Components

### Navigation Sidebar (`components/Sidebar.tsx`)
- Professional government-style navigation
- User profile display
- Active case indicator
- Quick access to all features

### API Client (`lib/api.ts`)
- TypeScript interfaces for all API endpoints
- Automatic error handling
- Response formatting utilities
- File upload support

### Dashboard Layout (`components/DashboardLayout.tsx`)
- Responsive layout with mobile support
- Consistent header and navigation
- Professional VAC branding

## Page Interfaces

### 1. Dashboard (`/`)
- **Purpose**: Overview of adjudicator's workload
- **Features**: Statistics, recent cases, quick actions, system status
- **Users**: All VAC adjudicators

### 2. Assessment Chat (`/chat`)
- **Purpose**: AI-assisted VAC assessments
- **Features**: Conversation management, function calling, case context
- **Users**: Adjudicators conducting assessments

### 3. Document Upload (`/upload`)
- **Purpose**: Upload and process medical documents
- **Features**: Drag-and-drop, progress tracking, condition detection
- **Users**: Adjudicators preparing cases

### 4. Case Management (`/cases`)
- **Purpose**: Manage veteran disability cases
- **Features**: Filtering, sorting, status tracking, priority management
- **Users**: Senior adjudicators, case managers

### 5. VAC ToD Browser (`/tod`)
- **Purpose**: Reference Table of Disabilities 2019
- **Features**: Chapter browsing, condition search, criteria lookup
- **Users**: All adjudicators for reference

### 6. Reports (`/reports`)
- **Purpose**: Performance analytics and reporting
- **Features**: Metrics, trends, export capabilities
- **Users**: Supervisors, quality assurance

## Styling & Theme

### VAC Government Theme
The interface uses a professional color scheme appropriate for government use:

```css
/* Primary Colors */
--vac-blue-600: #2563eb    /* Primary actions */
--vac-red-600: #dc2626     /* Urgent/important items */
--vac-gray-900: #111827    /* Primary text */

/* Status Colors */
--green-600: #059669       /* Completed/success */
--yellow-600: #d97706      /* In progress/warning */
--red-600: #dc2626         /* Failed/urgent */
```

### Professional Components
- Clean, accessible interface design
- Consistent spacing and typography
- Professional icons from Hero Icons
- Responsive design for desktop and tablet
- Print-friendly layouts for reports

## API Integration

### Endpoint Coverage
The frontend integrates with all backend API endpoints:

- ✅ `GET /health` - System health check
- ✅ `POST /chat` - Assessment conversations
- ✅ `POST /upload` - Document upload
- ✅ `POST /assess` - Case assessment
- ✅ `GET /conditions` - VAC condition lookup
- ✅ `GET /chapters` - VAC ToD chapters
- ✅ `GET /search` - Document search

### Type Safety
All API interactions are fully typed with TypeScript interfaces:

```typescript
interface VACCasePayload {
  case_id?: string
  conditions: VACCondition[]
  pre_existing?: VACCondition[]
  medical_evidence?: any[]
  assessment_date?: string
}

interface AssessmentResult {
  total_disability_rating: number
  individual_conditions: any[]
  quality_of_life_impact: any
  recommendations: string[]
}
```

## Responsive Design

### Desktop First (1024px+)
- Full sidebar navigation
- Multi-column layouts
- Detailed data tables
- Professional dashboard experience

### Tablet (768px - 1023px) 
- Collapsible sidebar
- Responsive grids
- Touch-friendly interface
- Maintained functionality

### Mobile Support (< 768px)
- Mobile menu overlay
- Single-column layouts
- Essential features accessible
- Professional mobile experience

## Production Deployment

### Static Export (Recommended)
```bash
# Build and export static files
npm run build
npm run export

# Deploy to Azure Static Web Apps
az staticwebapp create \
  --name vac-assessment-ui \
  --resource-group rg-vac-prod \
  --source . \
  --location canadacentral
```

### Container Deployment
```bash
# Build production container
docker build -t vac-assessment-ui .

# Deploy to Azure Container Apps
az containerapp create \
  --name vac-ui \
  --resource-group rg-vac-prod \
  --image vac-assessment-ui \
  --target-port 3000
```

### Environment Variables (Production)
```bash
NEXT_PUBLIC_API_URL=https://your-api.azurecontainerapps.io
NODE_ENV=production
NEXT_PUBLIC_VERSION=1.0.0
```

## Security Considerations

### Authentication
- Designed for integration with Azure AD
- Session management ready
- Role-based access control structure

### Data Security
- HTTPS-only in production
- No sensitive data stored in browser
- Professional audit trail support

### Compliance
- Government accessibility standards
- Professional data handling
- VAC branding compliance

## Development Workflow

### Local Development
1. Start backend API: `uvicorn app_simplified.main:app --reload --port 8000`
2. Start frontend: `npm run dev`
3. Access at: `http://localhost:3000`

### Code Quality
- TypeScript for type safety
- ESLint for code consistency
- Professional naming conventions
- Component reusability

### Testing Strategy
- Component integration testing
- API endpoint testing
- User workflow validation
- Cross-browser compatibility

## Customization

### Branding
Update `tailwind.config.js` and `globals.css` for custom colors and branding.

### Features
Add new pages in `app/` directory following the established patterns.

### API Extensions
Extend `lib/api.ts` with new endpoints and TypeScript interfaces.

## Performance Optimization

### Built-in Optimizations
- Next.js automatic code splitting
- Image optimization
- Static generation where possible
- Professional caching strategies

### Production Performance
- Optimized bundle sizes
- CDN-ready static assets
- Professional loading states
- Efficient data fetching

## Support & Maintenance

### Monitoring
- Built-in error boundaries
- Professional logging
- Performance monitoring ready

### Updates
- Semantic versioning
- Professional update procedures
- Backward compatibility focus

## Accessibility

- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader optimization
- Professional accessibility standards

---

**Ready for VAC Production Use**

This professional interface is designed specifically for VAC adjudicators and meets government standards for accessibility, security, and usability.