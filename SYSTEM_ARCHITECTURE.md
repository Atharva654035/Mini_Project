# System Architecture - Complaint Management System

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Technology Stack](#technology-stack)
4. [System Components](#system-components)
5. [Data Flow](#data-flow)
6. [Security Architecture](#security-architecture)
7. [Database Schema](#database-schema)
8. [API Endpoints](#api-endpoints)
9. [Deployment Architecture](#deployment-architecture)

---

## 1. System Overview

### Purpose
A secure web-based complaint management system that allows users to submit, track, and manage complaints while administrators can review, update, and resolve them.

### Key Features
- **User Authentication**: Separate login for regular users and administrators
- **Complaint Management**: Create, Read, Update, Delete (CRUD) operations
- **Data Encryption**: Sensitive data (names, complaints) encrypted at rest
- **Admin Dashboard**: Comprehensive complaint tracking and management
- **PDF Reports**: Export complaint data to PDF format
- **File Uploads**: Support for complaint evidence (images)
- **Status Tracking**: Real-time complaint status updates
- **Priority Management**: Categorize complaints by priority levels

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ User Portal  │  │ Admin Portal │  │  Authentication UI   │   │
│  │  (HTML/CSS)  │  │  (HTML/CSS)  │  │     (Login/Signup)   │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Django Web Framework (5.2.5)                │   │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐    │   │
│  │  │  Views     │  │  URL       │  │  Authentication  │    │   │
│  │  │  Layer     │  │  Router    │  │  Middleware      │    │   │
│  │  └────────────┘  └────────────┘  └──────────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │ 
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       BUSINESS LOGIC LAYER                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Complaint    │  │ User         │  │  Encryption          │   │
│  │ Management   │  │ Management   │  │  Manager             │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ PDF          │  │ File         │  │  Status              │   │
│  │ Generator    │  │ Handler      │  │  Tracker             │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         DATA ACCESS LAYER                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                Django ORM (Models)                       │   │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐    │   │
│  │  │ Complaint  │  │ Category   │  │ ComplaintUpdate  │    │   │
│  │  │  Model     │  │  Model     │  │     Model        │    │   │
│  │  └────────────┘  └────────────┘  └──────────────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      PERSISTENCE LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              MySQL Database (complaint_system)           │   │
│  │  • auth_user                                             │   │
│  │  • home_complaint (with encrypted fields)                │   │
│  │  • home_complaintcategory                                │   │
│  │  • home_complaintupdate                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         FILE STORAGE                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Media Storage (File System)                 │   │
│  │  • /media/complaints/  (complaint images)                │   │
│  │  • /media/action_images/  (admin action proof)           │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

### Backend
- **Framework**: Django 5.2.5
- **Language**: Python 3.x
- **ORM**: Django ORM
- **Database**: MySQL (complaint_system)
- **Authentication**: Django Auth System

### Security
- **Encryption Library**: Cryptography (Fernet)
- **Algorithm**: AES-128 (via Fernet)
- **Key Derivation**: PBKDF2HMAC with SHA256

### Reporting
- **PDF Generation**: ReportLab
- **PDF Features**: Tables, styling, pagination

### Frontend
- **Templates**: Django Templates (HTML)
- **Styling**: CSS
- **UI Components**: Bootstrap (inferred from templates)

### File Handling
- **Media Storage**: Django FileSystemStorage
- **Upload Handling**: Django FileField

---

## 4. System Components

### 4.1 User Module
**Location**: `Home/views.py`

**Components**:
- `login_page()`: User authentication
- `signup_page()`: User registration
- `logout_page()`: Session termination
- `home()`: Main user dashboard

**Features**:
- Session management
- Password hashing
- User validation

### 4.2 Complaint Module
**Location**: `Home/models.py`, `Home/views.py`

**Components**:
- `Complaint` Model: Core complaint entity
- `ComplaintCategory` Model: Complaint categorization
- `ComplaintUpdate` Model: Status change logging

**Operations**:
- Create complaint with file upload
- View complaint details
- Edit pending complaints
- Delete pending complaints
- Auto-ID generation (starts from 100)

### 4.3 Admin Module
**Location**: `Home/views.py`, `Home/admin.py`

**Components**:
- `Admin_Login()`: Admin authentication
- `Admin_Panel()`: Admin dashboard
- Django Admin interface

**Features**:
- Staff/superuser verification
- Complaint status management
- Response and action tracking
- File evidence upload
- Search and filter functionality

### 4.4 Encryption Module
**Location**: `Home/encryption.py`

**Components**:
- `EncryptionManager`: Centralized encryption handler
- `EncryptedTextField`: Auto-encrypting text field
- `EncryptedCharField`: Auto-encrypting char field

**Security Features**:
- Transparent encryption/decryption
- PBKDF2 key derivation
- Base64 encoding for storage

### 4.5 Reporting Module
**Location**: `Home/views.py` (download_complaints_pdf)

**Features**:
- Dynamic PDF generation
- Table formatting
- Text wrapping
- Filter-based export
- Search integration

---

## 5. Data Flow

### 5.1 User Complaint Submission Flow
```
User → Login → Home Page → Fill Complaint Form → Upload File (optional)
  → Select Category & Priority → Submit
  → Encryption Layer → Database Storage → Success Message
  → Display in User Dashboard
```

### 5.2 Admin Complaint Management Flow
```
Admin → Admin Login → Admin Panel → View All Complaints
  → Filter/Search → Select Complaint → Update Status
  → Add Response/Action → Upload Action Image (optional)
  → Save → Log Update → Notify via Status Change
```

### 5.3 Data Encryption Flow
```
Plaintext Input → EncryptedField.get_prep_value()
  → EncryptionManager.encrypt() → PBKDF2 Key Derivation
  → Fernet Encryption → Base64 Encoding → Database Storage

Database Retrieval → Base64 Decoding → Fernet Decryption
  → EncryptedField.from_db_value() → Plaintext Output
```

### 5.4 PDF Export Flow
```
Admin Panel → Apply Filters → Click Export PDF
  → Query Database → Format Data → Text Wrapping
  → Generate Table → Apply Styles → Build PDF
  → Download Response
```

---

## 6. Security Architecture

### 6.1 Authentication & Authorization
- **User Authentication**: Django session-based auth
- **Admin Authentication**: Staff/superuser privilege check
- **Login Required Decorators**: `@login_required` on protected views
- **Role-Based Access**: Separate admin and user portals

### 6.2 Data Encryption
**Encrypted Fields**:
- Complaint name (EncryptedCharField)
- Complaint description (EncryptedTextField)

**Encryption Specification**:
```python
Algorithm: Fernet (AES-128 CBC + HMAC)
Key Derivation: PBKDF2HMAC
  - Hash: SHA256
  - Iterations: 100,000
  - Salt: Static (should be dynamic in production)
Encoding: Base64 URL-safe
```

**Security Key**: Stored in `settings.ENCRYPTION_KEY`

### 6.3 File Upload Security
- **Validated Upload**: Django FileField validation
- **Isolated Storage**: `/media/complaints/` and `/media/action_images/`
- **Access Control**: Served only in DEBUG mode (dev)

### 6.4 Password Security
- Django's built-in password hashing (PBKDF2)
- Password validation rules (configured in settings)

### 6.5 CSRF Protection
- Django CSRF middleware enabled
- CSRF tokens in all forms

---

## 7. Database Schema

### 7.1 Entity Relationship Diagram
```
┌─────────────────┐
│   auth_user     │
│  (Django User)  │
│─────────────────│
│ id (PK)         │
│ username        │
│ password        │
│ is_staff        │
│ is_superuser    │
└─────────────────┘
        │
        │ 1:N
        ↓
┌──────────────────────────┐
│   home_complaint         │
│──────────────────────────│
│ id (PK) - starts at 100  │
│ user_id (FK)             │
│ name (encrypted)         │
│ division                 │
│ complaint (encrypted)    │
│ complaint_img            │
│ category_id (FK)         │
│ status                   │
│ priority                 │
│ complaint_date           │
│ resolved_date            │
│ admin_response           │
│ action_taken             │
│ action_image             │
└──────────────────────────┘
        │                   ↑
        │ N:1               │ N:1
        ↓                   │
┌────────────────────┐      │
│ home_complaint     │      │
│ category           │      │
│────────────────────│      │
│ id (PK)            │──────┘
│ name               │
│ description        │
│ created_at         │
└────────────────────┘

┌──────────────────────────┐
│ home_complaintupdate     │
│──────────────────────────│
│ id (PK)                  │
│ complaint_id (FK)        │
│ updated_by_id (FK)       │
│ old_status               │
│ new_status               │
│ update_message           │
│ updated_at               │
└──────────────────────────┘
```

### 7.2 Table Specifications

#### Complaint Table
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | AutoField | PK, starts at 100 | Unique complaint ID |
| user_id | ForeignKey | CASCADE | Reference to auth_user |
| name | EncryptedCharField | max_length=500 | Encrypted complainant name |
| division | CharField | max_length=100 | Department/division |
| complaint | EncryptedTextField | - | Encrypted complaint text |
| complaint_img | FileField | nullable | Evidence image |
| category_id | ForeignKey | SET_NULL | Complaint category |
| status | CharField | choices | pending/in_progress/resolved/rejected |
| priority | CharField | choices | low/medium/high/urgent |
| complaint_date | DateTimeField | auto_now_add | Submission timestamp |
| resolved_date | DateTimeField | nullable | Resolution timestamp |
| admin_response | TextField | blank | Admin's response |
| action_taken | TextField | blank | Actions performed |
| action_image | FileField | nullable | Action proof image |

#### ComplaintCategory Table
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | AutoField | PK | Unique category ID |
| name | CharField | max_length=100 | Category name |
| description | TextField | blank | Category description |
| created_at | DateTimeField | auto_now_add | Creation timestamp |

#### ComplaintUpdate Table
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | AutoField | PK | Unique update ID |
| complaint_id | ForeignKey | CASCADE | Reference to complaint |
| updated_by_id | ForeignKey | CASCADE | Admin who updated |
| old_status | CharField | max_length=20 | Previous status |
| new_status | CharField | max_length=20 | New status |
| update_message | TextField | blank | Update description |
| updated_at | DateTimeField | auto_now_add | Update timestamp |

---

## 8. API Endpoints

### 8.1 Authentication Endpoints
| URL | Method | View | Access | Description |
|-----|--------|------|--------|-------------|
| `/` | GET/POST | `login_page` | Public | User login |
| `/signup/` | GET/POST | `signup_page` | Public | User registration |
| `/logout/` | GET | `logout_page` | Authenticated | Logout user |
| `/AdminLogin/` | GET/POST | `Admin_Login` | Public | Admin login |

### 8.2 User Endpoints
| URL | Method | View | Access | Description |
|-----|--------|------|--------|-------------|
| `/home/` | GET/POST | `home` | User | User dashboard & create complaint |
| `/complaints/<id>/` | GET | `view_complaint` | User/Admin | View complaint details |
| `/complaints/<id>/edit/` | GET/POST | `edit_complaint` | User (owner) | Edit pending complaint |
| `/complaints/<id>/delete/` | GET/POST | `delete_complaint` | User (owner) | Delete pending complaint |

### 8.3 Admin Endpoints
| URL | Method | View | Access | Description |
|-----|--------|------|--------|-------------|
| `/AdminPanel/` | GET/POST | `Admin_Panel` | Admin | Admin dashboard & update status |
| `/download-pdf/` | GET | `download_complaints_pdf` | Admin | Export complaints to PDF |
| `/admin/` | ALL | Django Admin | Superuser | Django admin interface |

### 8.4 Request/Response Examples

**Create Complaint (POST /home/)**
```
Request Body:
- name: string
- division: string
- complaint: text
- complaint_img: file (optional)
- category: id
- priority: string (low/medium/high/urgent)

Response:
- Success: Redirect to /home/ with message
- Error: Render form with error message
```

**Update Status (POST /AdminPanel/)**
```
Request Body:
- complaint_id: int
- new_status: string
- admin_response: text
- action_taken: text
- action_image: file (optional)

Response:
- Success: Redirect to /AdminPanel/ with message
- Error: Render form with error message
```

---

## 9. Deployment Architecture

### 9.1 Development Environment
```
┌─────────────────────────────────────┐
│   Development Server (Django)      │
│   - DEBUG = True                    │
│   - SQLite/MySQL                    │
│   - Static files served by Django   │
│   - Media files served by Django    │
└─────────────────────────────────────┘
```

### 9.2 Production Environment (Recommended)
```
┌─────────────────────────────────────────────────────┐
│                Load Balancer (Nginx)                │
│  - SSL/TLS Termination                              │
│  - Static file serving                              │
│  - Request routing                                  │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│         Application Server (Gunicorn/uWSGI)         │
│  - Django Application                               │
│  - Multiple worker processes                        │
│  - DEBUG = False                                    │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│           Database Server (MySQL)                   │
│  - Persistent storage                               │
│  - Encrypted data at rest                           │
│  - Regular backups                                  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│        File Storage (AWS S3 or Local NAS)           │
│  - Media files (complaints, action images)          │
│  - Static files (CSS, JS)                           │
└─────────────────────────────────────────────────────┘
```

### 9.3 Security Considerations for Production
1. **Change SECRET_KEY** to a strong random value
2. **Change ENCRYPTION_KEY** to a strong secret
3. **Use dynamic salt** for encryption (per installation)
4. **Enable HTTPS** (SSL/TLS)
5. **Set ALLOWED_HOSTS** to specific domains
6. **Disable DEBUG** mode
7. **Use environment variables** for secrets
8. **Implement rate limiting** on login endpoints
9. **Set up proper file permissions**
10. **Regular security audits** and updates

### 9.4 Scalability Considerations
- **Horizontal Scaling**: Multiple Django instances behind load balancer
- **Database Optimization**: Read replicas for reporting
- **Caching**: Redis/Memcached for session storage
- **CDN**: For static file delivery
- **File Storage**: Cloud storage (S3) for media files
- **Background Tasks**: Celery for async operations (PDF generation)

---

## 10. System Workflow Summary

### User Journey
1. **Register** → Create account with username/password
2. **Login** → Authenticate and start session
3. **Submit Complaint** → Fill form with optional image
4. **Track Status** → View complaint in dashboard
5. **Edit/Delete** → Modify pending complaints only
6. **View Details** → See full complaint information

### Admin Journey
1. **Admin Login** → Authenticate with staff credentials
2. **View Dashboard** → See all complaints with filters
3. **Search/Filter** → Find specific complaints
4. **Update Status** → Change status and add response
5. **Take Action** → Document actions with proof
6. **Export Report** → Generate PDF for records

### System Operations
1. **Encryption** → Automatic on save/retrieve
2. **File Management** → Secure upload and storage
3. **Status Logging** → Track all changes
4. **Access Control** → Role-based permissions
5. **Data Integrity** → Transaction management

---

## 11. Future Enhancements

### Potential Improvements
1. **Email Notifications**: Notify users on status changes
2. **Real-time Updates**: WebSocket for live status
3. **Advanced Analytics**: Dashboard with charts
4. **Mobile App**: React Native/Flutter app
5. **Multi-language**: i18n support
6. **API REST/GraphQL**: For third-party integration
7. **Advanced Search**: Elasticsearch integration
8. **Audit Logs**: Comprehensive activity tracking
9. **Two-Factor Auth**: Enhanced security
10. **Cloud Deployment**: AWS/Azure/GCP setup

---

## 📝 Notes
- This architecture follows Django best practices
- Encryption provides data-at-rest security
- Role-based access ensures proper authorization
- Modular design allows easy extension
- File structure supports scalability

**Created**: October 2025  
**Version**: 1.0  
**Author**: System Architecture Documentation
