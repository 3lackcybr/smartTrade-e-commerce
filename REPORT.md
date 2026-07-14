# SmartTrade Africa — Secure E-Commerce Platform

## System Report & Demo Documentation

---

## 1. Executive Summary

SmartTrade Africa is a full-featured secure e-commerce web application built with Python Flask, integrating WebAuthn biometric authentication, a mock payment gateway, trust management systems, and comprehensive seller/buyer role management. The platform addresses real-world challenges in online marketplaces: identity verification, payment security, fraud prevention, and trust assurance.

**Key differentiators:**
- Cryptographic WebAuthn biometric authentication (fingerprint/face) for login and payment authorization
- Role-based access: Buyers, Sellers, and Admins with distinct workflows
- Device trust fingerprinting with risk-based step-up authentication
- Trust score system (0–100) that grows with positive user behavior
- Mock payment gateway with configurable success/failure modes
- Field-level encryption (Fernet) for sensitive user data (phone, tax IDs)
- Comprehensive audit logging for all security events

---

## 2. Technology Stack

| Component | Technology |
|---|---|
| Backend | Python Flask 3.1 — Werkzeug 3.1 |
| Database | SQLite via SQLAlchemy ORM |
| Authentication | Flask-Login + WebAuthn (W3C standard) |
| Biometric | webauthn library (Python) — platform authenticator only |
| Encryption | Fernet (cryptography library) + PBKDF2 key derivation |
| Frontend | HTML5, CSS3 (Custom Properties), Vanilla JavaScript |
| Payment | Mock Payment Gateway (swappable to Stripe) |
| Rate Limiting | Flask-Limiter |
| OAuth | Auth0 SSO (optional, via httpx + PyJWT) |

---

## 3. System Architecture

### 3.1 Application Structure

```
ecommerce-platform/
├── app/
│   ├── __init__.py              # App factory, extensions, before-request hooks
│   ├── models.py                # 15 database models
│   ├── routes/
│   │   ├── auth.py              # Registration, login, biometric, profile
│   │   ├── main.py              # Home, about, privacy, trust, FAQ
│   │   ├── products.py          # Catalog, search, detail
│   │   ├── cart.py              # Cart management
│   │   ├── payment.py           # Checkout, payment, orders, transactions
│   │   ├── seller.py            # Seller dashboard, products, orders
│   │   ├── admin.py             # Admin dashboard, users, sellers, orders
│   │   ├── chat.py              # Buyer-seller messaging
│   │   ├── ratings.py           # Product and seller ratings
│   │   ├── notifications.py     # User notification system
│   │   └── auth0_bp.py          # Auth0 SSO integration
│   ├── services/
│   │   └── payment_gateway.py   # MockPaymentGateway class
│   ├── utils/
│   │   ├── security.py          # Encryption, audit, session binding
│   │   └── decorators.py        # @admin_required, @biometric_required, etc.
│   ├── templates/               # 30+ HTML templates
│   │   ├── admin/               # 9 admin templates
│   │   ├── seller/              # 5 seller templates
│   │   └── chat/                # 2 chat templates
│   └── static/
│       ├── css/style.css        # 2,950+ lines premium design system
│       ├── js/main.js           # Flash dismiss, cart, mobile menu
│       ├── js/fingerprint.js    # Device fingerprint generation
│       └── js/biometric.js      # WebAuthn helper library
├── config.py                    # All config from .env with defaults
├── run.py                       # HTTPS entry point (SSL certs in ssl/)
├── seed.py                      # Database seeder
├── .env                         # 20+ configurable settings
├── ssl/                         # mkcert certificates for HTTPS LAN
└── REQUIREMENTS.txt             # Python dependencies
```

---

## 4. Authentication & Security

### 4.1 Registration

The registration page supports two account types:

- **Buyer** — Basic fields (name, email, phone, password)
- **Seller** — Additional fields (store name, tax ID, company certificate upload)

**Security features:**
- Password strength meter (real-time client-side validation)
- Server-side password strength check (min 8 chars, uppercase, lowercase, digit, special)
- Phone number encrypted at rest using Fernet
- Tax ID and company certificate for sellers encrypted at rest
- Device fingerprint captured silently on submit

During registration, the user's device fingerprint is saved to the `TrustedDevice` table with `is_trusted=False`. This prevents the "New Device Login" notification from firing on the immediate post-registration login, while the device is not marked as formally trusted until biometric is set up.

> **Screenshot placeholder:** `![Registration form with role selector](screenshots/registration.png)`

### 4.2 Login

| Feature | Detail |
|---|---|
| Rate limiting | 10 attempts per minute |
| Account lockout | 5 failed attempts → 15-minute lock |
| Device trust check | Known device → "Verified from your trusted device"; new device → notification |
| Session fingerprint | HMAC-SHA256 of IP + User-Agent, verified on every request |
| Session regeneration | On every login (prevents fixation) |
| Session timeout | Configurable (default 30 min inactivity) |
| Risk scoring | Base 50; +30 trusted device; -20 recent failures |

> **Screenshot placeholder:** `![Login form with security indicators](screenshots/login.png)`

### 4.3 Biometric Authentication (WebAuthn)

Users can enroll either:

**1. Fingerprint / Face Recognition (WebAuthn)**
- Uses W3C WebAuthn standard (`navigator.credentials.create` / `get`)
- Platform authenticator only (Windows Hello, Touch ID, Android fingerprint)
- Public key stored server-side; raw biometric data never leaves the device
- Cryptographic assertion verification on every authentication

**2. Device PIN (4-digit fallback)**
- Stored as `pin:<pbkdf2:sha256:600000 hash>`
- Used when WebAuthn is unavailable or on LAN HTTP access (non-secure context)

**Biometric enforcement:**
- If enabled, user must verify biometric after every login (redirect to `/auth/biometric/verify`)
- 2-minute expiry window for payment authorization
- On biometric setup, the current device is marked as `is_trusted=True`

> **Screenshot placeholder:** `![Biometric setup page with fingerprint/PIN options](screenshots/biometric_setup.png)`

> **Screenshot placeholder:** `![Biometric verification prompt](screenshots/biometric_verify.png)`

### 4.4 Device Trust & Fingerprinting

**Client-side fingerprint (`fingerprint.js`):**
SHA-256 hash computed from: screen dimensions, timezone, platform, browser languages, CPU cores, touch support, canvas fingerprint.

**Server-side tracking (`TrustedDevice` model):**
- `is_trusted` flag distinguishes known-but-unverified devices from biometric-trusted devices
- Registration saves device silently (`is_trusted=False`)
- Biometric setup upgrades device to `is_trusted=True`
- New unknown devices trigger security notification

> **Screenshot placeholder:** `![Trusted device notification in dropdown](screenshots/device_trust.png)`

### 4.5 Password Management

- **Forgot password** — Email-based verification code (6-digit) with 1-hour expiry
- **Change password** — Two-step flow: send code → verify code → set new password
- **Token security** — `itsdangerous` timed signed tokens

### 4.6 Auth0 SSO (Optional)

- OAuth2 Authorization Code flow via Auth0
- Auto-creates local user on first SSO login
- Hidden route at `/auth0/login` (not shown on main login page)

---

## 5. User Features

### 5.1 Profile Management

- View and edit full name, phone number
- Change password with verification flow
- Set security question (hashed answer via PBKDF2)
- Enable/disable biometric authentication
- View trust score with breakdown

> **Screenshot placeholder:** `![User profile page with trust score](screenshots/profile.png)`

### 5.2 Trust Score System

**Score breakdown (0–100):**

| Action | Points |
|---|---|
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
- `trust_score < 30` → blocked from certain actions via `@trust_verified` decorator
- Shown in user dropdown and on profile page

### 5.3 Notification System

- Bell icon in navbar with unread count badge
- Real-time polling via `/notifications/api/count` (JSON)
- Notifications for: new device login, seller verification update, new messages, refund processed, new seller registration (admin)
- "Mark all read" and individual mark-read with link navigation

> **Screenshot placeholder:** `![Notification bell with unread badge](screenshots/notifications.png)`

### 5.4 Buyer-Seller Chat

- Product-specific conversations (linked from product detail page)
- Direct messaging between buyer and seller
- Unread count via `/chat/api/unread`
- Notification created on new message

> **Screenshot placeholder:** `![Chat conversation page](screenshots/chat.png)`

### 5.5 Ratings & Reviews

- Product ratings: 1–5 stars with optional review text
- Seller ratings: 1–5 stars with review
- Restricted to paid order purchasers only (prevents fake reviews)
- Unique constraint per user+order+product/seller (one rating per purchase)

> **Screenshot placeholder:** `![Product rating form](screenshots/ratings.png)`

---

## 6. Products & Shopping

### 6.1 Product Catalog

- Paginated listing (12 per page)
- Category filter
- Search by keyword (`?q=` parameter, AJAX search endpoint)
- Sorting: price (asc/desc), rating, newest, name
- Responsive bento-grid product cards with wishlist hearts and floating badges

> **Screenshot placeholder:** `![Product catalog with grid layout](screenshots/product_catalog.png)`

### 6.2 Product Detail Page

- Image gallery with multiple images
- Product info: price, original price with discount badge, stock status, rating stars
- Seller info with contact seller button
- Related products (4 items from same category)
- Reviews section with purchase-verified badge
- "Add to Cart" button with stock validation

> **Screenshot placeholder:** `![Product detail page with gallery](screenshots/product_detail.png)`

### 6.3 Shopping Cart

- Real-time quantity adjustment
- Stock validation on add (prevents overselling)
- Quantity merge (add same product increments, not duplicates)
- Cart count badge in navbar
- Remove individual items

> **Screenshot placeholder:** `![Shopping cart with items](screenshots/cart.png)`

---

## 7. Payment System

### 7.1 Mock Payment Gateway Architecture

```
┌─────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  Flask App   │────▶│ MockPaymentGateway   │────▶│  DB Transaction │
│  (payment.py)│     │  (in-memory intents) │     │  PaymentTxn     │
└─────────────┘     └──────────────────────┘     └─────────────────┘
                           │
                    ┌──────┴──────┐
                    │  Modes:     │
                    │ always_succeed  │
                    │ random_fail │
                    └─────────────┘
```

**Modes:**

| Mode | Behavior |
|---|---|
| `always_succeed` | All payments succeed (default) |
| `random_fail` | Fails at configured `MOCK_FAILURE_RATE` (0.0–1.0) |

**Processing fee:** 2.9% + $0.30 (shown on receipt)

### 7.2 Payment Flow

```
Cart → Checkout → Pay (biometric verify) → Confirm → Receipt
```

1. **Checkout** (`/payment/checkout`) — Shipping form → creates `Order` (status: `pending`, payment: `unpaid`)
2. **Pay** (`/payment/pay/<id>`) — Creates mock payment intent; enforces biometric enrollment; renders payment page with card/mobile money tabs + biometric verify step
3. **Confirm** (`POST /payment/confirm/<id>`) — Verifies biometric session (2-min expiry); calls gateway confirm; records `PaymentTransaction`; updates order to `paid`
4. **Receipt** (`/payment/receipt/<id>`) — Print-friendly receipt with transaction ID, fee breakdown, order summary

**Payment methods:**
- **Credit/Debit Card** — Test: `4242 4242 4242 4242`, Exp: `12/26`, CVV: `123`
- **Mobile Money** — M-Pesa, Tigo Pesa, Airtel Money, Halopesa

> **Screenshot placeholder:** `![Payment page with card and mobile money tabs](screenshots/payment.png)`

> **Screenshot placeholder:** `![Payment receipt print view](screenshots/receipt.png)`

### 7.3 Transaction History

Users can view all their payment transactions at `/payment/transactions`:
- Amount, status, payment method, date
- Total spent summary
- Link to receipt and order details
- Paginated (15 per page)

> **Screenshot placeholder:** `![My transactions page](screenshots/transactions.png)`

### 7.4 Admin Refunds

- Admin can issue full or partial refunds
- Refund creates refund ID (`rf_mock_*`)
- Order status → `cancelled`, payment → `refunded`
- User notified via notification system

---

## 8. Seller Features

### 8.1 Seller Registration & Verification Workflow

```
Register → Upload documents → Admin reviews → Verified → Can sell
```

- Seller submits: store name, tax ID, company registration certificate (PDF/PNG/JPG)
- Admin receives notification of new seller registration
- Admin reviews documents at `/admin/sellers/<id>`
- Admin verifies with optional notes
- Seller receives notification and dashboard unlocks

### 8.2 Seller Dashboard

- Protected by `@step_up_auth` (triggers biometric re-verification if risk score low)
- Stats: total products, orders, revenue, average rating
- Quick links to manage products, view orders, see ratings

> **Screenshot placeholder:** `![Seller dashboard with stats](screenshots/seller_dashboard.png)`

### 8.3 Seller Product Management

| Route | Function |
|---|---|
| `/seller/products` | List own products |
| `/seller/products/create` | Create product (only if verified) with image upload |
| `/seller/products/<id>/edit` | Edit product, add additional images |
| `/seller/products/<id>/delete` | Soft-delete (deactivate) product |

- Only verified sellers can create products
- Product images upload to `static/uploads/`
- Multiple images per product with sort order

> **Screenshot placeholder:** `![Seller product form with image upload](screenshots/seller_product_form.png)`

### 8.4 Seller Orders & Ratings

- View orders containing their products (only if verified)
- View ratings received on their products
- Unverified sellers see a pending verification alert

---

## 9. Admin Features

### 9.1 Admin Dashboard

- Protected by `@admin_required` + `@step_up_auth`
- KPIs: total users, products, orders, revenue
- Net revenue (after fees and refunds)
- Low stock alerts
- Pending seller verifications count
- Unpaid orders count
- Transaction stats: total, succeeded, failed, today's count and revenue
- Payment methods breakdown

> **Screenshot placeholder:** `![Admin dashboard with KPIs](screenshots/admin_dashboard.png)`

### 9.2 Seller Verification (Admin)

- View all sellers with verification status
- Seller detail page showing: products, orders, decrypted tax ID (viewable only by admin)
- Toggle verified/unverified with optional notes
- Notification sent to seller on status change

> **Screenshot placeholder:** `![Admin seller verification page](screenshots/admin_seller_verify.png)`

### 9.3 User Management (Admin)

- View all users with pagination
- User detail with: personal info, orders, audit logs
- Decrypt and view phone numbers and tax IDs (Fernet decryption)
- Toggle user active/inactive (cannot deactivate admins)

### 9.4 Order & Refund Management (Admin)

- View all orders with status/payment filters
- Update order status: pending → confirmed → processing → shipped → delivered → cancelled
- Issue full or partial refunds on paid orders

### 9.5 Transaction Management (Admin)

- View all payment transactions with filters:
- Status (succeeded, failed, pending, refunded)
- Payment method
- Date range
- Total transaction volume displayed
- Payment methods breakdown chart

> **Screenshot placeholder:** `![Admin transaction list with filters](screenshots/admin_transactions.png)`

### 9.6 Product Management (Admin)

- Create/edit any product
- Upload main image and additional gallery images
- Mark products as featured or active/inactive

---

## 10. Security Architecture

### 10.1 Defense Layers

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

### 10.2 Security Headers

| Header | Value |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `X-XSS-Protection` | `1; mode=block` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | Restricted (geo, mic, camera, payment) |
| `Content-Security-Policy` | Nonce-based scripts, restricted sources |
| `Strict-Transport-Security` | Production only (max-age 1 year) |

### 10.3 Database Models

| Model | Table | Purpose |
|---|---|---|
| `User` | `user` | Account management, roles, biometric keys, trust score |
| `Product` | `product` | Product catalog with pricing, stock, images |
| `ProductImage` | `product_image` | Multiple images per product |
| `Category` | `category` | Product categories |
| `CartItem` | `cart_item` | Shopping cart (unique user + product) |
| `Order` | `order` | Orders with shipping, payment, trust status |
| `OrderItem` | `order_item` | Line items within orders |
| `PaymentTransaction` | `payment_transaction` | Full payment records with gateway responses |
| `TrustedDevice` | `trusted_device` | Device fingerprints with trust flag |
| `Notification` | `notification` | User notification queue |
| `Message` | `message` | Buyer-seller chat messages |
| `ProductRating` | `product_rating` | Product reviews (unique user+order+product) |
| `SellerRating` | `seller_rating` | Seller reviews (unique user+order+seller) |
| `AuditLog` | `audit_log` | Security event audit trail |
| `PasswordResetToken` | `password_reset_token` | Timed password reset tokens |
| `VerificationCode` | `verification_code` | 6-digit verification codes |

---

## 11. UI/UX Design

### 11.1 Design System

- **Color palette:** Golden Amber (#D97706) primary, Emerald secondary, Deep Navy (#0F172A) backgrounds
- **Layout:** Bento-grid product cards, glass morphism navbar, consistent 90px section padding
- **Typography:** System font stack, clear hierarchy with 2xl border radius on cards
- **Animations:** Floating hero circle, hover-scale cards, skeleton loaders, fade-in transitions

### 11.2 Premium Components

- **Navbar:** Glass morphism with backdrop-filter blur, sticky, responsive
- **Product cards:** Wishlist hearts, floating discount badges, hover scale
- **Buttons:** Gradient backgrounds with glow shadows on hover
- **Hero:** Full-width with animated floating decorative circle
- **Forms:** Toggle switches, icon cards, steps progress indicators
- **Status:** Color-coded badges (pending/shipped/delivered/paid)
- **Empty states:** Icons + messaging + call-to-action for all empty lists

> **Screenshot placeholder:** `![Premium homepage hero section](screenshots/homepage.png)`

> **Screenshot placeholder:** `![Glass navbar with dropdown menu](screenshots/navbar.png)`

> **Screenshot placeholder:** `![Product card with wishlist and discount badge](screenshots/product_card.png)`

---

## 12. Configuration & Deployment

### 12.1 Environment Variables (`.env`)

```ini
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///ecommerce.db
ENCRYPTION_KEY=your-encryption-key
ADMIN_PASSWORD=Admin@123456
FLASK_ENV=development
HOST=0.0.0.0
PORT=5000
SESSION_TIMEOUT_MINUTES=30
MOCK_PAYMENT_MODE=always_succeed
MOCK_FAILURE_RATE=0.0
MOCK_PROCESSING_DELAY=0.5
SECURITY_HEADERS_ENABLED=true
```

### 12.2 HTTPS Setup (LAN Access)

The server serves HTTPS using mkcert-generated certificates covering:
- `localhost`, `127.0.0.1`, `192.168.1.212`

For Android/phone access:
1. Copy `ssl/mkcert-rootCA.pem` to phone
2. Install as CA certificate in Settings → Security → CA certificate
3. Access `https://192.168.1.212:5000`

> **Screenshot placeholder:** `![HTTPS certificate installed on Android](screenshots/android_https.png)`

### 12.3 Setup Instructions

```bash
# Install dependencies
pip install -r requirements.txt

# Seed database (deletes old data)
python seed.py

# Start server (HTTPS auto if certs exist in ssl/)
python run.py
```

### 12.4 Default Admin

- Username: `admin`
- Password: `Admin@123456`

---

## 13. Complete Route Map

### User Routes

| Route | Page |
|---|---|
| `/` | Homepage |
| `/auth/register` | Registration |
| `/auth/login` | Login |
| `/auth/profile` | Profile |
| `/auth/biometric/setup` | Biometric/PIN enrollment |
| `/auth/biometric/verify` | Biometric verification |
| `/products/` | Product catalog |
| `/products/<slug>` | Product detail |
| `/cart/` | Shopping cart |
| `/payment/checkout` | Checkout |
| `/payment/pay/<id>` | Payment page |
| `/payment/orders` | Order history |
| `/payment/transactions` | Transaction history |
| `/payment/receipt/<id>` | Payment receipt |
| `/notifications/` | Notifications |
| `/chat/` | Chat inbox |
| `/chat/with/<id>` | Conversation |

### Seller Routes

| Route | Page |
|---|---|
| `/seller/` | Dashboard |
| `/seller/products` | My products |
| `/seller/products/create` | New product |
| `/seller/orders` | Orders |
| `/seller/ratings` | Ratings |

### Admin Routes

| Route | Page |
|---|---|
| `/admin/` | Dashboard |
| `/admin/users` | All users |
| `/admin/sellers` | All sellers |
| `/admin/products` | All products |
| `/admin/orders` | All orders |
| `/admin/transactions` | All transactions |

---

## 14. Test User Flow

1. **Register** — Create account as buyer or seller
2. **Login** — Authenticate with credentials
3. **Set up biometric** — Enroll fingerprint/face or PIN
4. **Browse products** — Search, filter, view details
5. **Add to cart** — Select quantity, add items
6. **Checkout** — Enter shipping info
7. **Pay** — Verify biometric, select payment method, confirm
8. **View receipt** — Print-friendly receipt with transaction details
9. **Rate product/seller** — Leave review on purchased items
10. **Contact seller** — Send message via chat

**Admin flow:**
1. Login as admin (`admin` / `Admin@123456`)
2. View dashboard metrics
3. Verify pending sellers
4. Manage products, orders, refunds
5. View transaction history

---

## 15. Conclusion

SmartTrade Africa delivers a production-ready e-commerce platform with robust security, trust management, and role-based workflows. Key achievements:

- **Biometric authentication** using W3C WebAuthn standard with PIN fallback
- **Trust management** through device fingerprinting, risk scoring, and step-up auth
- **Role-based access** for buyers, sellers, and admins with distinct interfaces
- **Mock payment gateway** with configurable modes and complete transaction tracking
- **Field-level encryption** for sensitive data at rest
- **Comprehensive auditing** of all security events
- **Premium UI/UX** with consistent design system and responsive layout
- **Device trust** with registration-time binding and biometric upgrade
- **Secure context** via HTTPS for LAN access with trusted certificates
