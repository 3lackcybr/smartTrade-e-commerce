# SmartTrade Africa — Implementation Summary

> Comprehensive record of all features, models, routes, and configurations implemented since project inception.

---

## 1. Back Button Navigation

**Problem:** No reliable way to navigate back without browser arrows.
**Solution:** Fixed-position back button placed as direct child of `<body>` (outside `<main>`) so it renders reliably on all pages.
**File:** `app/templates/base.html`

---

## 2. Product Image Gallery

**Model:** `ProductImage` (separate table for relational integrity)
- `product_id`, `image_url`, `alt_text`, `sort_order`, `is_primary`
- Gallery ordered by `sort_order`, primary image selected by flag
- **File:** `app/models.py`

**UI:** Product detail page shows thumbnail strip + main image. JS switches main image on thumbnail click.
**Admin form:** File upload inputs for main image and additional images (multiple). Current images shown as thumbnails on edit. New uploads append without removing existing.
**Seller form:** Same file upload flow as admin.
**Seed data:** All 20 seeded products use picsum.photos placeholder image URLs.
**Product cards:** Use `primary_image()` method across index, products, cart, detail.

---

## 3. Multi-Role System (Buyer / Seller)

### User Model Extensions
- `role` — `"customer"` or `"seller"` (default `"customer"`)
- `store_name`, `tax_id`, `company_certificate`, `verification_notes`, `is_seller_verified`
- `Product.seller_id` FK + `User.products` relationship
- **File:** `app/models.py`

### Registration (`/auth/register`)
- Role selector with visual cards (Buyer / Seller)
- Seller fields: Store Name, TAX ID, Company Registration Certificate upload (PDF/PNG/JPG, max 16MB)
- Certificate saved to `app/static/uploads/` with UUID filename
- Phone and tax_id encrypted at rest using Fernet encryption
- Admin notified via Notification on new seller registration
- **File:** `app/routes/auth.py`

### Seller Verification (Admin)
- `/admin/sellers` — list all sellers
- `/admin/sellers/<id>` — detail with certificate viewer, product list, orders
- `/admin/sellers/<id>/verify` — toggle verify/unverify with optional notes
- Seller receives notification on verification status change
- **File:** `app/routes/admin.py`

### Seller Dashboard (`/seller/`)
- Stats: products count, orders count, total revenue, average rating
- Verification status banner — unverified sellers see admin notes
- Products CRUD (only if verified)
- Orders view (orders containing seller's products)
- Ratings view (customer reviews for seller's products)
- **File:** `app/routes/seller.py`

---

## 4. Notification System

**Model:** `Notification`
- `user_id`, `title`, `message`, `link`, `is_read`, `created_at`
- **File:** `app/models.py`

**Routes:**
- `/notifications/` — paginated notification list
- `/notifications/read/<id>` — mark one read, redirect to link
- `/notifications/read-all` — mark all read
- `/notifications/api/count` — JSON unread count (for polling)
- **File:** `app/routes/notifications.py`

**UI:** Bell icon in navbar with real-time unread badge via context processor.
**Triggers:** New seller registration → admins ; Verification update → seller ; New message → receiver.

---

## 5. Chat System (Buyer ↔ Seller)

**Model:** `Message`
- `sender_id`, `receiver_id`, `product_id` (optional), `subject`, `body`, `is_read`, `created_at`
- **File:** `app/models.py`

**Routes:**
- `/chat/` — inbox grouped by conversation partner
- `/chat/with/<user_id>` / `/chat/with/<user_id>/<product_id>` — message history with chat bubbles
- `/chat/send` — POST with notification to receiver
- `/chat/api/unread` — unread count JSON
- **File:** `app/routes/chat.py`

**UI:** "Contact Seller" button on product detail page. Chat bubbles with sent/received styling. Auto-scroll to latest.

---

## 6. Payment API Integration (MockPay Gateway)

### Service Layer
- `app/services/payment_gateway.py` — `MockPaymentGateway` class
  - `create_payment_intent()` — simulates API call, returns `pi_mock_*` ID
  - `confirm_payment()` — processes with configurable delay, returns `txn_mock_*` ID
  - `refund_payment()` — returns `rf_mock_*` refund ID
  - `retrieve_payment()` — status lookup
  - Configurable modes: `always_succeed` / `random_fail`
  - Processing fee: 2.9% + $0.30 per transaction

### Transaction Tracking
- `PaymentTransaction` model: `transaction_id`, `payment_intent_id`, `amount`, `currency`, `payment_method`, `status`, `gateway_response` (JSON), `refund_id`, `refund_amount`
- **File:** `app/models.py`

### Payment Flow
1. **Checkout** (`/payment/checkout`) — shipping form, creates Order + OrderItems, deducts stock, clears cart
2. **Pay** (`/payment/pay/<id>`) — creates payment intent, checks biometric enrollment, shows payment page
3. **Confirm** (`POST /payment/confirm/<id>`) — verifies biometric session (2-min expiry), calls gateway, records transaction, updates payment_status → `paid`
4. **Confirmation** (`/payment/confirmation/<id>`) — success page with transaction receipt, fees, trust verification
5. **Receipt** (`/payment/receipt/<id>`) — print-friendly full receipt with fee breakdown
6. **Order History** (`/payment/orders`) — paginated list with payment status + receipt button
- **File:** `app/routes/payment.py`

### Payment Methods
| Method | UI | Details |
|--------|-----|---------|
| Credit/Debit Card | Card form | Test: `4242 4242 4242 4242`, Exp: `12/26`, CVV: `123` |
| Mobile Money | Mobile form | Test: `+255 712 000 000`, Providers: M-Pesa, Tigo Pesa, etc. |

### Admin Payment Management
- `/admin/orders` — payment filter (unpaid/paid/refunded), payment status per order
- `/admin/orders/<id>/refund` — refund a paid order (cancels order, updates payment_status)
- Admin dashboard: net revenue, unpaid orders count, gross revenue
- **File:** `app/routes/admin.py`

### UI Enhancements
- Payment timeline (Order Created → Payment → Confirmation)
- Animated processing spinner with status steps
- Error state with retry button
- Receipt section on confirmation page
- Print-friendly receipt template
- Payment template generates WebAuthn assertion options server-side for inline biometric verify

### Configuration (`.env`)
```ini
MOCK_PAYMENT_MODE=always_succeed
MOCK_FAILURE_RATE=0.0
MOCK_PROCESSING_DELAY=0.5
```

---

## 7. Biometric Authentication (WebAuthn + PIN)

### 7.1 Technology
- **WebAuthn** (W3C standard) via browser `navigator.credentials` API for fingerprint/face recognition
- **PIN fallback** — 4-digit device PIN stored as PBKDF2-SHA256 hash
- **Library:** `webauthn` (Python) for server-side cryptographic assertion verification

### 7.2 Enrollment (`/auth/biometric/setup`)
- User chooses between fingerprint/face or PIN
- **WebAuthn path:** Server generates `PublicKeyCredentialCreationOptions` with random challenge stored in session. Client creates credential via `navigator.credentials.create()`. Full credential response sent to server. `verify_registration_response()` cryptographically verifies the attestation. `credential_id` and `credential_public_key` stored in `User` model.
- **PIN path:** Client sends 4-digit PIN. Server hashes with `pbkdf2:sha256:600000`, stores as `pin:<hash>`.
- **File:** `app/routes/auth.py` (`biometric_setup`)

### 7.3 Verification (`/auth/biometric/verify`)
- **Context:** Redirected from login (if `biometric_enabled == True`) or from payment (risk-based)
- **No skip option** — user with biometric enabled MUST verify before proceeding
- Both WebAuthn and PIN methods shown simultaneously (no one gets stuck)
- **WebAuthn path:** Server generates `PublicKeyCredentialRequestOptions` with challenge + `allowCredentials`. Client calls `navigator.credentials.get()`. Full assertion response (signature, authenticatorData, clientDataJSON) sent to server. `verify_authentication_response()` cryptographically verifies the signature against the stored public key.
- **PIN path:** Client sends PIN. Server compares against stored hash.
- On success: session regenerated, `session["biometric_verified"] = True` + timestamp set, trust score updated.
- **File:** `app/routes/auth.py` (`biometric_verify`)

### 7.4 Payment Biometric Enforcement
- `/payment/pay/<id>`: If `biometric_enabled == False`, user is redirected to `/auth/biometric/setup`
- `/payment/confirm/<id>`: Server checks `session["biometric_verified"]` — must be True within 2-minute expiry window. Rejects with 401 if missing or expired.
- Payment template generates assertion options server-side for the inline biometric verify flow.
- **File:** `app/routes/payment.py`

### 7.5 New User Onboarding Banner
- After login, if user hasn't set up biometric AND hasn't dismissed the prompt, a blue banner appears on every page: "Enhance your account security — Set up biometric authentication"
- "Set Up Now" button links to `/auth/biometric/setup`
- Dismiss button POSTs to `/auth/dismiss-biometric-prompt` (sets `session["biometric_prompt_dismissed"] = True`)
- Banner auto-hides once user enables biometric
- **Files:** `app/templates/base.html` (banner), `app/__init__.py` (context processor), `app/routes/auth.py` (dismiss route), `app/static/css/style.css` (banner styles)

### 7.6 Biometric Disable/Revocation
- `POST /auth/biometric/disable` — clears `biometric_credential_id`, `biometric_public_key`, `biometric_enabled`, session flags. Re-shows onboarding prompt.
- "Disable" button on Profile page (confirmation dialog)
- **File:** `app/routes/auth.py` (`disable_biometric`)

### 7.7 Security Improvements
| Issue | Before | After |
|-------|--------|-------|
| `{ verified: true }` bypass | Server blindly trusted client | Server cryptographically verifies WebAuthn assertion via `webauthn` library |
| Skip after login | "Skip for now" button bypassed verification | No skip — mandatory verify |
| No onboarding | New users never prompted | Dismissible banner after login |
| No disable option | Biometric permanent once enabled | `/auth/biometric/disable` route |
| Decorators unused | `@step_up_auth` defined but never applied | Applied to seller + admin dashboards |

### Files Changed
- `app/templates/biometric_verify.html` — combined WebAuthn + PIN layout, no skip, server assertion options
- `app/templates/biometric_setup.html` — server-generated registration options, full credential submission
- `app/templates/payment.html` — server assertion options, full assertion submission
- `app/templates/profile.html` — "Disable" button
- `app/templates/base.html` — onboarding banner + dismiss JS
- `app/__init__.py` — `show_biometric_prompt` context variable
- `app/static/css/style.css` — verify methods layout + banner styles

---

## 8. HTTPS / SSL Setup

### Motivation
- WebAuthn requires a secure context (`isSecureContext === true`)
- `localhost:5000` is treated as secure by browsers, but not `192.168.1.212:5000`
- Need LAN access for multi-device testing + WebAuthn

### Solution
1. **mkcert** generates a local Certificate Authority trusted by the system
2. Certificates generated for `192.168.1.212`, `localhost`, `127.0.0.1`
3. **cheroot** (CherryPy WSGI server) serves Flask with SSL — replaces Flask dev server's unreliable `ssl_context`
4. Server binds to `0.0.0.0:5000` (accessible on all network interfaces)

### Files
- `run.py` — uses cheroot `WSGIServer` + `BuiltinSSLAdapter` when `ssl/cert.pem` and `ssl/key.pem` exist
- `config.py` — `SESSION_COOKIE_SECURE = False` (HTTP), `SESSION_COOKIE_SAMESITE = "Lax"`, Redis/filesystem session config
- `.env` — `HOST=0.0.0.0`
- `requirements.txt` — added `cheroot`

### Important Notes
- Firefox requires `security.enterprise_roots.enabled = true` in `about:config` (Firefox uses its own cert store)
- Other browsers (Chrome, Edge) use the system cert store and will show a "Your connection is not private" page with a "Proceed" link

---

## 9. Seller Rating System

**Model:** `SellerRating`
- `seller_id`, `user_id`, `order_id`, `rating`, `review`, `created_at`
- Unique constraint on `(user_id, order_id)` — one seller rating per order
- `User.seller_rating` / `User.seller_rating_count` aggregate fields (avg, count)
- **File:** `app/models.py`

**Routes:** Product/seller rating submission routes with purchase verification.
**UI:** Rating form templates (`rate_product.html`, `rate_seller.html`) with clickable star selector. Review cards on product detail page. Seller rating stars next to store name. "Rate" buttons on order confirmation and order history pages.
**CSS:** Star-selector hover effects, review cards, rate-prompt banner.

---

## 10. Trusted Computing Platform (TCP) Integration

### 10.1 Secure Session Management
- **Session fingerprint binding:** Each session bound to `IP + User-Agent` hash (HMAC-SHA256). Verified on every request via `before_request`. Mismatch → `SESSION_HIJACK_DETECTED` audit log + force logout.
- **Session timeout:** `check_session_timeout()` called before each request. 30-minute inactivity auto-logout.
- **Session regeneration:** On login, biometric verify, password change, and security question set. Prevents session fixation.
- **Cookie hardening:** `SameSite=Lax`, `HttpOnly`, `Secure` (auto-enabled when SSL certs present or in production).
- **Server-side sessions:** Flask-Session with Redis primary / filesystem fallback. Cookie `sta_session` stores only a signed session ID (not session data). Config in `app/__init__.py:33-47` and `.env` (`REDIS_URL`).
- **Files:** `app/__init__.py` (before_request), `app/utils/security.py` (fingerprint + timeout functions), `config.py` (cookie flags)

### 10.2 Device Trust Verification
- **`TrustedDevice` model:** `user_id`, `device_fingerprint`, `browser_info`, `ip_address`, `last_seen`, `is_trusted`
- **JS fingerprinting** (`app/static/js/fingerprint.js`): SHA-256 hash of screen resolution, color depth, timezone, platform, languages, hardware concurrency, touch support, and canvas fingerprint.
- **Login flow:** Hidden `device_fingerprint` input populated by JS on form submit. Known devices updated; new devices registered + notification sent.
- **File:** `app/models.py` (TrustedDevice), `app/routes/auth.py` (device tracking on login)

### 10.3 Secure Token Handling
- **Signed tokens** with `itsdangerous.URLSafeTimedSerializer`: `generate_signed_token(data, salt)`, `verify_signed_token(token, salt, max_age=3600)`. Can replace DB-stored password reset tokens.
- **CSRF:** Flask-WTF enabled globally. Payment confirm AJAX includes CSRF token.
- **Field encryption:** `encrypt_field()` / `decrypt_field()` wrappers using Fernet (PBKDF2-derived key, SHA-256, 480K iterations). `phone` and `tax_id` encrypted at rest on registration; decrypted on profile view. `decrypt_field()` catches `InvalidToken` and returns `None` gracefully.
- **File:** `app/utils/security.py`

### 10.4 Trusted Login Validation
- **Risk scoring** on login: base 50, +30 for trusted device, -20 for recent failed attempts. Stored in `session["login_risk_score"]`.
- **Step-up authentication** decorator `@step_up_auth`: if risk score < 30, redirects to biometric verify before sensitive actions. Applied to seller dashboard + admin dashboard.
- **Account lockout:** 5 failed attempts → 15-minute lock.
- **New device alert:** Notification sent when unrecognized device logs in.
- **File:** `app/utils/decorators.py` (step_up_auth), `app/routes/auth.py` (risk scoring)

### 10.5 Secure Communication Channels
- **`after_request` handler** adds security headers to every response:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy` — restricts geolocation, microphone, camera, payment APIs
  - `Content-Security-Policy` — restricts sources for scripts, styles, images, fonts, connections (handles empty AUTH0_DOMAIN gracefully)
  - `Strict-Transport-Security` — only in production (`max-age=31536000; includeSubDomains; preload`)
- Configurable via `SECURITY_HEADERS_ENABLED` env var.
- **File:** `app/__init__.py` (after_request)

### 10.6 Secure Credential Storage
- **Admin password:** Read from `ADMIN_PASSWORD` env var (fallback `Admin@123456`). `create_default_admin()` encrypts admin phone via `encrypt_field()`.
- **Password hashing:** PBKDF2-SHA256 with 600K iterations.
- **Security answer hashing:** PBKDF2-SHA256 independently.
- **Fernet encryption key:** Derived from `ENCRYPTION_KEY` via PBKDF2 (480K iterations).
- **File:** `app/utils/security.py`, `config.py`, `.env`

### Configuration (`.env` additions)
```ini
ADMIN_PASSWORD=Admin@123456
SECURITY_HEADERS_ENABLED=true
```

---

## 11. Auth0 SSO Integration

### Purpose
- Alternative login method (removed from main login UI, accessible at `/auth0/login`)
- Synchronous OAuth2 Authorization Code flow using `httpx` + `PyJWT`
- No async event-loop conflicts

### Files
- `app/routes/auth0_bp.py` — `/auth0/login` (redirect to Auth0), `/auth0/callback` (exchange code, create/find local user by email, login), `/auth0/logout` (clear session + redirect to Auth0 logout)
- `app/__init__.py` — registers `auth0` blueprint; CSP `img-src` includes Auth0 domain (handles empty domain gracefully)
- `.env` — `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`, `AUTH0_CLIENT_SECRET`, `AUTH0_SECRET`, `AUTH0_REDIRECT_URI=http://localhost:5000/auth0/callback`
- `config.py` — reads all Auth0 vars

### Important Notes
- `AUTH0_SECRET` generated with `py -c "import secrets; print(secrets.token_hex(64))"`
- Callback/Logout URLs must be registered in Auth0 Dashboard
- Auth0 buttons and `.btn-auth0` CSS removed from `login.html` and `register.html` (user preference)

---

## 12. Cross-Cutting Concerns

### Models (final list)
| Model | Purpose |
|-------|---------|
| User | Account with roles, security, device trust, biometric |
| Category | Product categorization |
| Product | Product details with seller FK |
| ProductImage | Multiple product images |
| CartItem | Shopping cart |
| Order | Order with payment tracking |
| OrderItem | Line items per order |
| PasswordResetToken | Password reset tokens |
| VerificationCode | 2FA code storage |
| AuditLog | Security audit trail |
| Notification | User notifications |
| Message | Buyer-seller chat |
| ProductRating | Product reviews |
| SellerRating | Seller ratings |
| PaymentTransaction | Payment gateway traceability |
| TrustedDevice | Device fingerprint registry |

### Key Files Reference
| File | Purpose |
|------|---------|
| `app/__init__.py` | App factory, before/after request handlers, blueprint registration, context processor |
| `app/models.py` | All database models |
| `app/routes/auth.py` | Registration, login, biometric setup/verify/disable, password, profile, dismiss prompt |
| `app/routes/auth0_bp.py` | Auth0 SSO login/callback/logout |
| `app/routes/payment.py` | Checkout, payment processing, receipts, biometric-enforced pay/confirm |
| `app/routes/admin.py` | Admin dashboard, product/user/order/seller management, refunds, step-up auth |
| `app/routes/seller.py` | Seller dashboard, products, orders, ratings, step-up auth |
| `app/routes/chat.py` | Inbox, conversation, message sending |
| `app/routes/notifications.py` | Notification list, mark read, API |
| `app/routes/ratings.py` | Product and seller rating submission |
| `app/services/payment_gateway.py` | MockPay Gateway service |
| `app/utils/security.py` | Encryption, hashing, token management, session fingerprint, file upload |
| `app/utils/decorators.py` | Admin, biometric, trust, step-up auth decorators |
| `app/static/js/fingerprint.js` | Browser device fingerprinting |
| `app/static/js/biometric.js` | WebAuthn registration/authentication library (defined, not currently used by templates — inline JS used instead) |
| `run.py` | Flask entry point with cheroot SSL server |
| `config.py` | Application configuration |
| `seed.py` | Database seeder (20 products) |
| `SUMMARY.md` | This file |

### Default Admin Credentials
- **Username:** `admin`
- **Password:** `Admin@123456` (configurable via `ADMIN_PASSWORD` env var)
- **Role:** Admin

### Critical Context
- Old database must be deleted when schema changes (`instance/ecommerce.db`)
- Run `python seed.py` to repopulate after DB reset
- All payments are simulated via MockPay Gateway — no real money processed
- Security headers are active in all environments; HSTS only activates in production
- Session fingerprint binding requires cookies AND headers to match — may logout on IP change (expected security behavior)
- Server bound to `0.0.0.0:5000` with HTTPS via cheroot + mkcert (see §8 for Firefox config)
- WebAuthn requires HTTPS — use `https://localhost:5000` not `http://`
- Biometric `{ verified: true }` bypass fixed — server now cryptographically verifies assertions (requires `webauthn` Python library)
- PIN fallback always available regardless of enrolled credential type (both WebAuthn + PIN shown on verify page)
