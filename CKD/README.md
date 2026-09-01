# Explainable AI-Based Chronic Kidney Disease Prediction and Diagnosis System

A state-of-the-art web system for Chronic Kidney Disease (CKD) prediction featuring role-based user management (Patient & Doctor), prediction history tracking, interactive visualizations, and automated generation of clinical PDF reports with Explainable AI (SHAP, LIME, PDP) charts.

## 🌟 Features

- **ML-Based Prediction**: Trained models using XGBoost, Random Forest, and other algorithms
- **Explainable AI**: SHAP, LIME, and PDP interpretations for model transparency
- **Role-Based Access Control**: Separate portals for Patients and Doctors
- **Prediction History**: Track and review historical predictions
- **Clinical PDF Reports**: Automated generation of diagnostic reports with embedded XAI charts
- **REST API**: Django REST Framework with JWT authentication
- **Interactive Visualizations**: Plotly.js for dynamic data exploration

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 4.2 + Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Database**: SQLite (development) / MySQL (production)
- **ML/AI**: scikit-learn, XGBoost, LightGBM
- **Explainable AI**: SHAP, LIME
- **PDF Generation**: ReportLab
- **Data Processing**: Pandas, NumPy

### Frontend (Planned)
- React.js with modern UI components
- Plotly.js for interactive charts
- Dark mode support

## 📋 Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- Git

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd CKD
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

The project uses SQLite by default for local development. The database file (`db.sqlite3`) is already included with migrations applied.

**For SQLite (Recommended for Local Development):**

```bash
cd ckd_backend
python manage.py migrate
```

**For MySQL (Production/Docker Only):**

Only use MySQL if you have a MySQL server running and configured. Do NOT set these variables for local development.

```bash
# Set environment variables (only if you have MySQL configured)
set USE_MYSQL=True
set DB_NAME=ckd_db
set DB_USER=root
set DB_PASSWORD=your_actual_mysql_password
set DB_HOST=127.0.0.1
set DB_PORT=3306

# Run migrations
cd ckd_backend
python manage.py migrate
```

**If you accidentally set MySQL variables and want to revert to SQLite:**

```bash
# Unset MySQL environment variables
set USE_MYSQL=
set DB_NAME=
set DB_USER=
set DB_PASSWORD=
set DB_HOST=
set DB_PORT=

# Or simply close and reopen your terminal
```

### 5. Create Superuser (Optional)

```bash
cd ckd_backend
python manage.py createsuperuser
```

## 🏃 Running the Project

### Backend Setup

**Option 1: Using the batch file (Windows)**
```bash
run_backend.bat
```

**Option 2: Using SQLite (Recommended for Local Development)**
```bash
# Clear any MySQL environment variables
use_sqlite.bat

# Or manually:
cd ckd_backend
python manage.py runserver
```

The backend server will start at `http://127.0.0.1:8000/`

### Frontend Setup

**Option 1: Using the batch file (Windows)**
```bash
run_frontend.bat
```

**Option 2: Manual command**
```bash
cd ckd_frontend
npm install
npm run dev
```

The frontend will start at `http://localhost:3000/`

### Access the Application

- **Frontend**: `http://localhost:3000/`
- **Backend API**: `http://127.0.0.1:8000/api/`
- **Admin Panel**: `http://127.0.0.1:8000/admin/`
- **API Documentation**: Use Django REST Framework's browsable API at any endpoint

## 📁 Project Structure

```
CKD/
├── ckd_backend/              # Django backend project
│   ├── ckd_backend/         # Project settings
│   │   ├── settings.py      # Django configuration
│   │   ├── urls.py          # Main URL routing
│   │   └── wsgi.py          # WSGI configuration
│   ├── api/                 # Main Django app
│   │   ├── ml/              # ML models and inference
│   │   │   ├── ckd_model_pipeline.joblib  # Trained model
│   │   │   ├── model_metadata.joblib      # Model metadata
│   │   │   ├── inference.py              # Prediction logic
│   │   │   └── train.py                  # Training script
│   │   ├── migrations/        # Database migrations
│   │   ├── models.py          # Database models
│   │   ├── serializers.py     # DRF serializers
│   │   ├── views.py           # API views
│   │   ├── urls.py            # API URL routing
│   │   ├── pdf_generator.py  # PDF report generation
│   │   └── admin.py           # Admin configuration
│   ├── manage.py             # Django management script
│   └── db.sqlite3            # SQLite database (dev)
├── ckd_frontend/             # React frontend project
│   ├── src/
│   │   ├── components/       # React components
│   │   │   └── Navbar.jsx
│   │   ├── pages/            # Page components
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── PatientDashboard.jsx
│   │   │   ├── DoctorDashboard.jsx
│   │   │   ├── PredictionForm.jsx
│   │   │   └── PredictionResults.jsx
│   │   ├── contexts/         # React contexts
│   │   │   └── AuthContext.jsx
│   │   ├── services/         # API services
│   │   │   └── api.js
│   │   ├── App.jsx           # Main App component
│   │   ├── main.jsx          # Entry point
│   │   └── index.css         # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── Dockerfile
│   └── nginx.conf
├── dataset/                   # Training data
│   └── kidney_disease.csv    # UCI CKD dataset
├── requirements.txt          # Python dependencies
├── Dockerfile                # Backend Docker configuration
├── docker-compose.yml        # Docker Compose configuration
├── run_backend.bat          # Backend startup script (Windows)
├── run_frontend.bat          # Frontend startup script (Windows)
├── use_sqlite.bat           # SQLite setup script (Windows)
├── implementation_plan.md.resolved  # Detailed implementation plan
└── README.md                # This file
```

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login (returns JWT token)
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Predictions
- `POST /api/predictions/` - Create a new prediction (requires authentication)
- `GET /api/predictions/` - List predictions (filtered by user role)
- `GET /api/predictions/{id}/` - Get specific prediction details
- `GET /api/predictions/{id}/explanation/` - Get XAI explanation (SHAP/LIME)

### Users
- `GET /api/users/profile/` - Get current user profile
- `PUT /api/users/profile/` - Update user profile

### Reports
- `GET /api/reports/{prediction_id}/pdf/` - Generate and download PDF report

## 🧠 ML Model Information

The project includes a pre-trained ML pipeline (`ckd_model_pipeline.joblib`) that:

- **Input Features**: 24 clinical parameters (age, blood pressure, specific gravity, albumin, sugar, etc.)
- **Target**: CKD classification (ckd / notckd)
- **Model**: XGBoost classifier (optimized via hyperparameter tuning)
- **Preprocessing**: Includes imputation, encoding, and scaling
- **Output**: Prediction class, probability, and risk level

### Retrain the Model

To retrain the model with new data:

```bash
cd ckd_backend/api/ml
python train.py
```

## 🔧 Configuration

### Environment Variables

For MySQL configuration (optional for local dev):

```bash
USE_MYSQL=True          # Enable MySQL (default: False)
DB_NAME=ckd_db         # Database name
DB_USER=root           # Database user
DB_PASSWORD=password   # Database password
DB_HOST=127.0.0.1      # Database host
DB_PORT=3306           # Database port
```

### Django Settings

Key settings in `ckd_backend/settings.py`:
- `SECRET_KEY`: Django secret key (change for production)
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Add your domain for production
- `CORS_ALLOW_ALL_ORIGINS`: Adjust CORS settings for frontend

## 📊 Current Implementation Status

### ✅ Completed (Backend)
- [x] Django project setup and configuration
- [x] Database models (User, Doctor, Patient, Prediction, Explanation)
- [x] REST API endpoints with JWT authentication
- [x] ML model training and pipeline serialization
- [x] Prediction inference engine
- [x] SHAP/LIME explanation generation
- [x] PDF report generation
- [x] Role-based access control
- [x] SQLite database with migrations
- [x] API URL routing configuration

### ✅ Completed (Frontend)
- [x] React project structure with Vite
- [x] TailwindCSS styling
- [x] Authentication pages (Login/Register)
- [x] Patient dashboard with prediction history
- [x] Doctor dashboard with patient management
- [x] Prediction form with all clinical parameters
- [x] Prediction results display with risk levels
- [x] PDF report download functionality
- [x] JWT token management and refresh
- [x] Role-based routing and access control

### ✅ Completed (DevOps)
- [x] Docker configuration for backend
- [x] Docker configuration for frontend
- [x] Docker Compose for full stack deployment
- [x] Nginx configuration for frontend
- [x] MySQL database configuration for production
- [x] Batch scripts for easy startup (Windows)

### 🚧 Planned Enhancements
- [ ] Interactive Plotly visualizations for SHAP/LIME charts
- [ ] AWS EC2 deployment
- [ ] Production database setup (MySQL)
- [ ] Enhanced error handling and validation
- [ ] Unit and integration tests

See `implementation_plan.md.resolved` for the complete 18-stage execution plan.

## � Docker Deployment

### Using Docker Compose (Recommended for Production)

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

This will start:
- **MySQL database** on port 3306
- **Django backend** on port 8000
- **React frontend** on port 3000

### Individual Docker Builds

**Backend only:**
```bash
docker build -t ckd-backend .
docker run -p 8000:8000 ckd-backend
```

**Frontend only:**
```bash
cd ckd_frontend
docker build -t ckd-frontend .
docker run -p 3000:3000 ckd-frontend
```

## �🐛 Troubleshooting

### MySQL Connection Errors

If you get "Access denied for user 'root'@'localhost'" or similar MySQL errors, you likely have MySQL environment variables set but no MySQL server configured. **For local development, use SQLite instead:**

```bash
# Unset all MySQL environment variables
set USE_MYSQL=
set DB_NAME=
set DB_USER=
set DB_PASSWORD=
set DB_HOST=
set DB_PORT=

# Then run migrations with SQLite
cd ckd_backend
python manage.py migrate
```

Or simply close and reopen your terminal to clear environment variables.

### Port Already in Use
If port 8000 is already in use:
```bash
python manage.py runserver 8001
```

### Dependency Issues
If you encounter dependency conflicts:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Database Migration Errors
If migrations fail:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Module Import Errors
Ensure you're in the correct directory and virtual environment is activated:
```bash
cd ckd_backend
# Verify activation
python --version
```

### ML Model Loading Issues
If the model fails to load, ensure the `.joblib` files exist in `ckd_backend/api/ml/`:
```bash
dir ckd_backend\api\ml\*.joblib
```

## 📚 Additional Resources

- **Implementation Plan**: See `implementation_plan.md.resolved` for detailed 18-stage learning framework
- **Dataset**: UCI Chronic Kidney Disease Dataset
- **API Documentation**: Use Django REST Framework's browsable API at `http://127.0.0.1:8000/api/`

## 🤝 Contributing

This project is designed as an interactive learning framework for B.Tech IT students. Each stage includes theoretical concepts, implementation walkthroughs, and assessment checkpoints.

## 📝 License

This project is part of an academic initiative for Chronic Kidney Disease research and education.

## 📧 Contact

For questions about the implementation plan or project structure, refer to the detailed documentation in `implementation_plan.md.resolved`.
