# SmartTrade Africa — Secure E-Commerce Platform

<div align="center">

![SmartTrade Africa](https://img.shields.io/badge/SmartTrade%20Africa-E--Commerce-1f2937?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=flat-square&logo=flask)
![WebAuthn](https://img.shields.io/badge/WebAuthn-W3C%20Standard-0078d4?style=flat-square)
![SQLite](https://img.shields.io/badge/Database-SQLite-003b57?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

A production-ready, secure e-commerce platform featuring **WebAuthn biometric authentication**, **trust management systems**, and **role-based access control** for the African market.

[Features](#features) • [Tech Stack](#tech-stack) • [Quick Start](#quick-start) • [Architecture](#architecture) • [Security](#security) • [Demo](#demo)

</div>

---

## Overview

SmartTrade Africa is a full-featured secure e-commerce web application designed for the African market with a focus on **security**, **trust**, and **accessibility**. The platform integrates crypt[...]

### Key Highlights

✨ **Biometric Authentication** — W3C WebAuthn standard with fingerprint/face recognition  
🔐 **End-to-End Encryption** — Field-level Fernet encryption for sensitive data  
⭐ **Trust Score System** — Dynamic 0–100 trust scoring based on user behavior  
👥 **Role-Based Access** — Distinct workflows for buyers, sellers, and admins  
💳 **Payment Integration** — Mock gateway with multiple payment methods (card, mobile money)  
📊 **Comprehensive Auditing** — Security event logging for compliance  
📱 **Responsive Design** — Premium UI/UX with glass morphism and bento-grid layouts  
🌐 **HTTPS Ready** — LAN deployment with mkcert certificates  

---

## Features

### 🔐 Authentication & Security

- **WebAuthn Biometric Login** — Fingerprint/face recognition via platform authenticator
- **Device Trust Fingerprinting** — SHA-256 hashing of device attributes for security
- **PIN Fallback** — 4-digit PIN for environments without WebAuthn support
- **Session Security** — HMAC-SHA256 session fingerprinting + automatic regeneration
- **Rate Limiting** — 10 login attempts/minute, 5-attempt account lockout (15 min)
- **Encryption at Rest** — PBKDF2 password hashing + Fernet field-level encryption
- **Security Headers** — CSP, X-Frame-Options, X-Content-Type-Options, HSTS

### 👤 User Management

- **Flexible Registration** — Buyer or seller account types with role-specific fields
- **Profile Management** — Edit name, phone, password, security questions
- **Trust Score Dashboard** — Visual breakdown of trust score components
- **Password Recovery** — Email-based 6-digit verification codes (1-hour expiry)
- **Notification System** — Real-time alerts for security events, messages, orders

### 🛍️ Shopping Features

- **Product Catalog** — Paginated listing with category filters and search
- **Smart Search** — Full-text search with sorting (price, rating, newest, name)
- **Shopping Cart** — Real-time quantity adjustment with stock validation
- **Product Ratings** — 5-star reviews with verified purchase badges
- **Buyer-Seller Chat** — Product-specific messaging system
- **Wishlist** — Heart-icon favorites on product cards

### 💳 Payment System

- **Mock Payment Gateway** — Configurable success/failure modes for testing
- **Multiple Payment Methods** — Credit/debit cards, M-Pesa, Tigo Pesa, Airtel Money, Halopesa
- **Biometric Payment Auth** — 2-minute biometric verification before payment confirmation
- **Transaction History** — Complete payment records with receipt generation
- **Processing Fees** — Transparent 2.9% + $0.30 fee calculation
- **Admin Refunds** — Full or partial refund capability with audit trail

### 🏪 Seller Dashboard

- **Seller Registration** — Multi-step verification with document upload (tax ID, certificate)
- **Product Management** — Create, edit, delete products with multi-image galleries
- **Order Tracking** — View orders containing seller's products
- **Ratings & Reviews** — Seller performance metrics and customer feedback
- **Inventory Management** — Stock tracking with admin alerts

### 🛡️ Admin Console

- **Dashboard Metrics** — KPIs: users, products, orders, revenue, transaction stats
- **Seller Verification** — Review and approve/reject seller registrations
- **User Management** — View all users, decrypt sensitive fields, manage status
- **Order Management** — Status tracking, shipping updates, refund processing
- **Transaction Analytics** — Filters by status, method, date range; payment breakdown charts
- **Low Stock Alerts** — Notifications for inventory below threshold

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python Flask 3.1 + Werkzeug 3.1 |
| **Database** | SQLite via SQLAlchemy ORM |
| **Authentication** | Flask-Login + WebAuthn (W3C standard) |
| **Biometric** | webauthn library — platform authenticator only |
| **Encryption** | Fernet (cryptography) + PBKDF2 key derivation |
| **Frontend** | HTML5, CSS3 (custom properties), Vanilla JavaScript |
| **Payment** | Mock Payment Gateway (Stripe-compatible) |
| **Rate Limiting** | Flask-Limiter |
| **Optional SSO** | Auth0 OAuth2 |
| **Deployment** | HTTPS via mkcert certificates |

---

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/3lackcybr/smartTrade-e-commerce.git
   cd smartTrade-e-commerce
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings (see Configuration section)
   ```

5. **Initialize database**
   ```bash
   python seed.py
   ```

6. **Start development server**
   ```bash
   python run.py
   ```

   The server will be available at `https://localhost:5000`

### Default Admin Credentials

The application comes with a default admin account for initial setup:

```
Username: admin
Password: Admin@123456
```

⚠️ **IMPORTANT SECURITY WARNINGS:**

1. **Change these credentials immediately** after first login in production environments
2. **Never commit `.env` files** containing sensitive credentials to version control
3. **Regenerate encryption keys** for production deployments
4. **Use environment variables** or a secrets manager (HashiCorp Vault, AWS Secrets Manager) for production credentials

**First Login Steps:**
1. Navigate to `https://localhost:5000/auth/login`
2. Enter username: `admin` and password: `Admin@123456`
3. Complete biometric setup (fingerprint/face or PIN)
4. Go to `/auth/profile` and immediately change the password
5. Update other security settings as needed

---

## Architecture

### Application Structure

```
smartTrade-e-commerce/
├── app/
│   ├── __init__.py                      # App factory, extensions, hooks
│   ├── models.py                        # 15 database models
│   ├── routes/
│   │   ├── auth.py                      # Registration, login, biometric
│   │   ├── main.py                      # Home, privacy, trust, FAQ
│   │   ├── products.py                  # Catalog, search, detail
│   │   ├── cart.py                      # Cart management
│   │   ├── payment.py                   # Checkout, payment, orders
│   │   ├── seller.py                    # Seller dashboard & products
│   │   ├── admin.py                     # Admin dashboard & management
│   │   ├── chat.py                      # Buyer-seller messaging
│   │   ├── ratings.py                   # Product & seller ratings
│   │   ├── notifications.py             # Notification system
│   │   └── auth0_bp.py                  # Auth0 SSO integration
│   ├── services/
│   │   └── payment_gateway.py           # MockPaymentGateway class
│   ├── utils/
│   │   ├── security.py                  # Encryption, audit, fingerprint
│   │   └── decorators.py                # @admin_required, @biometric_required
│   ├── templates/                       # 30+ HTML templates
│   ├── static/
│   │   ├── css/style.css                # Premium design system (2,950+ lines)
│   │   ├── js/main.js                   # Core functionality
│   │   ├── js/fingerprint.js            # Device fingerprinting
│   │   └── js/biometric.js              # WebAuthn helpers
│   └── static/uploads/                  # Product images
├── config.py                            # Configuration management
├── run.py                               # HTTPS entry point
├── seed.py                              # Database seeder
├── requirements.txt                     # Python dependencies
├── .env                                 # Environment variables (excluded from git)
├── .env.example                         # Environment template
├── .gitignore                           # Git exclusions
└── ssl/                                 # mkcert certificates (HTTPS)
```

### Database Models

| Model | Purpose |
|-------|---------|
| `User` | Account management, biometric keys, trust score |
| `Product` | Product catalog with pricing, stock, images |
| `ProductImage` | Multiple images per product |
| `Category` | Product categorization |
| `CartItem` | Shopping cart items |
| `Order` | Order records with shipping & payment status |
| `OrderItem` | Order line items |
| `PaymentTransaction` | Payment records & gateway responses |
| `TrustedDevice` | Device fingerprints with trust flag |
| `Notification` | User notification queue |
| `Message` | Buyer-seller chat messages |
| `ProductRating` | Product reviews |
| `SellerRating` | Seller reviews |
| `AuditLog` | Security event audit trail |
| `PasswordResetToken` | Timed password reset tokens |
| `VerificationCode` | 6-digit verification codes |

---

## Configuration

### Environment Variables (`.env`)

```ini
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///ecommerce.db

# Encryption
ENCRYPTION_KEY=your-encryption-key-here

# Admin Account
ADMIN_PASSWORD=Admin@123456

# Server
HOST=0.0.0.0
PORT=5000
SESSION_TIMEOUT_MINUTES=30

# Mock Payment Gateway
MOCK_PAYMENT_MODE=always_succeed    # Options: always_succeed, random_fail
MOCK_FAILURE_RATE=0.0               # 0.0 to 1.0
MOCK_PROCESSING_DELAY=0.5

# Security
SECURITY_HEADERS_ENABLED=true

# Optional: Auth0 SSO
AUTH0_DOMAIN=your-auth0-domain.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
```

### HTTPS Setup (LAN Access)

The application requires HTTPS even in development. Certificates are provided via mkcert and cover:
- `localhost`, `127.0.0.1`, `192.168.1.212`

**For Android/phone access:**

1. Download `ssl/mkcert-rootCA.pem` to your phone
2. Open Settings → Security → Install from storage → Select certificate
3. Access `https://192.168.1.212:5000`

---

## Security

### Defense Layers

```
┌─────────────────────────────────────────┐
│            HTTPS / SSL                    │
├─────────────────────────────────────────┤
│       CSP Headers (nonce-based)          │
├─────────────────────────────────────────┤
│    Session Fingerprint (IP + UA)        │
├─────────────────────────────────────────┤
│     CSRF Tokens (Flask-WTF)            │
├─────────────────────────────────────────┤
│   Input Sanitization (Bleach)          │
├─────────────────────────────────────────┤
│   Field Encryption (Fernet)            │
├─────────────────────────────────────────┤
│  Password Hashing (PBKDF2-SHA256)       │
├─────────────────────────────────────────┤
│  Rate Limiting + Account Lockout       │
├─────────────────────────────────────────┤
│  Audit Logging (all security events)    │
└─────────────────────────────────────────┘
```

### Security Headers

| Header | Value |
|--------|-------|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `X-XSS-Protection` | `1; mode=block` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | Restricted (geo, mic, camera, payment) |
| `Content-Security-Policy` | Nonce-based scripts, restricted sources |
| `Strict-Transport-Security` | Production only (max-age 1 year) |

### Trust Score System

**Scoring breakdown (0–100):**

| Action | Points |
|--------|--------|
| Base score | 35 |
| Email verified | +15 |
| Phone verified | +10 |
| Biometric enabled | +15 |
| Security question set | +10 |
| Admin account | +10 |
| Per paid order | up to +10 total |
| Failed login penalty | up to -20 |

**Effects:**
- `trust_score >= 40` → order marked as `trust_verified`
- `trust_score < 30` → blocked from certain actions

---

## Demo

### Test Credentials

**Buyer Account:**
```
Email: buyer@test.com
Password: TestPassword@123
```

**Seller Account:**
```
Email: seller@test.com
Password: TestPassword@123
```

**Admin Account:**
```
Username: admin
Password: Admin@123456
```

⚠️ **Default credentials are for development/testing only. Change immediately in production.**

### Test Payment Methods

**Credit/Debit Card:**
- Card Number: `4242 4242 4242 4242`
- Expiry: `12/26`
- CVV: `123`

**Mobile Money Providers:**
- M-Pesa
- Tigo Pesa
- Airtel Money
- Halopesa

### User Flow

1. **Register** → Create account as buyer or seller
2. **Login** → Authenticate with credentials
3. **Setup Biometric** → Enroll fingerprint/face or PIN
4. **Browse Products** → Search, filter, view details
5. **Add to Cart** → Select quantity
6. **Checkout** → Enter shipping information
7. **Pay** → Verify biometric, select payment method
8. **Receipt** → View and print transaction details
9. **Rate** → Leave reviews on purchased items
10. **Chat** → Contact sellers

---

## API Routes

### User Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Homepage |
| `/auth/register` | GET, POST | User registration |
| `/auth/login` | GET, POST | User login |
| `/auth/profile` | GET, POST | Profile management |
| `/auth/biometric/setup` | GET, POST | Biometric enrollment |
| `/auth/biometric/verify` | GET, POST | Biometric verification |
| `/products/` | GET | Product catalog |
| `/products/<slug>` | GET | Product details |
| `/cart/` | GET, POST, DELETE | Shopping cart |
| `/payment/checkout` | GET, POST | Checkout |
| `/payment/pay/<id>` | GET, POST | Payment page |
| `/payment/orders` | GET | Order history |
| `/payment/transactions` | GET | Transaction history |
| `/payment/receipt/<id>` | GET | Payment receipt |

### Seller Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/seller/` | GET | Seller dashboard |
| `/seller/products` | GET | Product listing |
| `/seller/products/create` | GET, POST | Create product |
| `/seller/products/<id>/edit` | GET, POST | Edit product |
| `/seller/products/<id>/delete` | POST | Delete product |
| `/seller/orders` | GET | Order tracking |
| `/seller/ratings` | GET | Seller ratings |

### Admin Routes
| Route | Method | Purpose |
|-------|--------|---------|
| `/admin/` | GET | Admin dashboard |
| `/admin/users` | GET | User management |
| `/admin/sellers` | GET | Seller management |
| `/admin/sellers/<id>` | GET, POST | Seller verification |
| `/admin/products` | GET | Product management |
| `/admin/orders` | GET | Order management |
| `/admin/transactions` | GET | Transaction history |

---

## Deployment

### Production Checklist

- [ ] Update `SECRET_KEY` and `ENCRYPTION_KEY` with strong random values
- [ ] Change default admin password
- [ ] Set `FLASK_ENV=production`
- [ ] Generate production SSL certificates
- [ ] Configure database backup strategy
- [ ] Enable security headers (`SECURITY_HEADERS_ENABLED=true`)
- [ ] Set up rate limiting appropriately
- [ ] Configure email service for password resets
- [ ] Enable audit logging and monitoring
- [ ] Implement proper logging and error handling
- [ ] Store `.env` variables in a secrets manager (not in repository)

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--certfile=ssl/server.crt", "--keyfile=ssl/server.key", "--bind", "0.0.0.0:5000", "run:app"]
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- Follow PEP 8 style guide
- Add docstrings to functions
- Include unit tests for new features
- Update documentation as needed

---

## Troubleshooting

### SSL Certificate Issues

**Problem:** `SSL: CERTIFICATE_VERIFY_FAILED`

**Solution:**
```bash
# Regenerate certificates (requires mkcert)
cd ssl/
mkcert localhost 127.0.0.1 192.168.1.212
```

### Database Errors

**Problem:** Database locked or corrupted

**Solution:**
```bash
# Backup old database
mv ecommerce.db ecommerce.db.backup

# Reseed database
python seed.py
```

### WebAuthn Not Available

**Problem:** "WebAuthn not supported on this browser/device"

**Solution:**
- Use supported browsers: Chrome, Firefox, Edge, Safari (on macOS/iOS)
- Use supported authenticators: Windows Hello, Touch ID, Android fingerprint
- Fall back to PIN option during setup

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Support & Contact

For issues, questions, or feedback:
- **Issues:** [GitHub Issues](https://github.com/3lackcybr/smartTrade-e-commerce/issues)
- **Email:** support@smarttrade.africa
- **Documentation:** See [REPORT.md](REPORT.md) for detailed technical documentation

---

## Acknowledgments

- WebAuthn implementation: [webauthn.io](https://webauthn.io/)
- Design inspiration: Modern e-commerce platforms
- Security best practices: OWASP, CWE
- African payment methods integration

---

**SmartTrade Africa** — Building secure, trusted commerce for Africa 🌍

Made with ❤️ for the African e-commerce ecosystem
