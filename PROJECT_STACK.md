# SmartTrade Africa — Technical Architecture Report

---

## 1. Technologies Used & Why

### Programming Language: Python 3.13
- **Why**: Mature ecosystem for full-stack web apps, excellent library support (Flask, cryptography, pyotp), rapid development, strong typing in 3.12+ improves code quality. SQLAlchemy ORM + WebAuthn integration both have mature Python libraries.

### Web Framework: Flask 3.1.0
- **Why**: Lightweight, explicit, no auto-magic. Blueprint-based modular routing (separate files for auth, products, admin, seller, chat, etc.). Simple enough to maintain solo yet extensible. No heavy ORM lock-in (SQLAlchemy is separate). Low overhead for a LAN-scale application.

### Key Flask Extensions

| Extension | Version | Purpose |
|-----------|---------|---------|
| Flask-SQLAlchemy | 3.1.1 | ORM — declarative models, automatic table creation, relationship loading |
| Flask-Login | 0.6.3 | Session-based auth — `current_user` proxy, `@login_required`, `login_remember` |
| Flask-WTF | 1.2.2 | CSRF token generation/validation on every HTML form + AJAX via `X-CSRFToken` header |
| Flask-Limiter | >=4.1.1 | Rate limiting — 200/day, 50/hour per IP, memory-backed |
| Flask-Migrate | 4.1.0 | Schema migrations (used sparingly — most changes use startup ALTER TABLE) |
| WTForms | 3.2.1 | Form validation (used indirectly via Flask-WTF) |

### Database: SQLite via SQLAlchemy
- **Why**: Zero-config, file-based, sufficient for a LAN-scale app. No separate DB server to install. SQLAlchemy ORM makes future migration to PostgreSQL straightforward (change URI in `config.py`). File at `instance/ecommerce.db`.

### Frontend

| Layer | Technology | Why |
|-------|-----------|-----|
| Templates | Jinja2 (Flask built-in) | Server-rendered HTML — no client framework needed for this scale |
| CSS | Custom CSS (3,825 lines) | No framework bloat — CSS custom properties (`--primary`, `--radius`) for theming, responsive with media queries |
| JavaScript | Vanilla JS | No framework needed — AJAX for cart/wishlist/filter toggles, WebAuthn API calls, flash dismiss |
| Icons | HTML entities + emoji (`&#128722;`, `&#10003;`) | Zero external dependencies, no icon library to load |
| i18n | Custom JSON-based | Homegrown system — `app/utils/i18n.py` loads `en.json`/`sw.json` -> `_()` function -> Jinja2 global |

### Why no frontend framework?
- Application targets LAN (low latency), single-dev/small-team admin, simplicity of maintenance. Server-rendered Jinja2 eliminates JS build toolchain. All interactivity is progressively enhanced vanilla JS.

---

## 2. Authentication System

### 2.1 Authentication Methods (4 total)

| Method | Route | Implementation |
|--------|-------|----------------|
| **Password** | `POST /auth/login` | `pbkdf2:sha256:600000` via Werkzeug's `generate_password_hash`/`check_password_hash`. Rate-limited: 5 attempts -> 30s lockout, 10 -> 5min, 20 -> 30min |
| **WebAuthn Biometric** | `POST /auth/biometric/verify` | FIDO2 WebAuthn via `webauthn` Python library. Fingerprint/face on device. Challenge stored in session. Validated against stored credential ID + public key |
| **TOTP (Time-based OTP)** | `POST /auth/totp/verify` | `pyotp` library, `valid_window=1` (+-30s skew). QR code setup (`otpauth://` URI). Manual secret entry fallback. Disable with password confirmation |
| **Auth0 SSO** | `GET /auth0/login` -> Auth0 -> callback | OAuth2/OIDC. Redirects to Auth0 hosted login, callback at `/auth0/callback`. Configured via `AUTH0_CLIENT_ID`/`AUTH0_DOMAIN`/`AUTH0_CLIENT_SECRET` |

### 2.2 Session Management
- **Flask-Login** with `session_protection="basic"` (verifies IP + User-Agent)
- **Custom session fingerprint** in `before_request` (`session_security_check`): compares stored fingerprint (IP hash + User-Agent hash) against current request. Mismatch -> logs `SESSION_HIJACK_DETECTED`, clears session, logs out
- **Session timeout**: 20 minutes inactivity (`app.permanent_session_lifetime`), tracked via `session["last_activity"]`
- **Biometric gate**: Biometric-enabled users who haven't verified in this session are blocked from all routes except `biometric.*`, `logout`, and `static`. Redirected to `/auth/biometric-verify`
- **Step-up auth**: Payment requires fresh biometric verification within 2-minute window

### 2.3 Password Security
- Algorithm: `pbkdf2:sha256:600000` (600,000 iterations)
- Failed attempts tracked on `User` model (`failed_attempts`, `locked_until`)
- Account lockout thresholds: 5 -> 30s, 10 -> 5min, 20 -> 30min

### 2.4 CSRF Protection
- Flask-WTF generates per-session token, validated on every `POST`/`PUT`/`DELETE`
- AJAX endpoints accept token via `X-CSRFToken` header or `csrf_token()` in inline scripts with CSP nonce
- Full coverage: every `<form>` includes `{{ csrf_token() }}` hidden input

### 2.5 Rate Limiting
- Global: 200 requests/day, 50/hour per IP
- Login endpoint: additional 5/minute limit via `@limiter.limit()`
- Storage: `memory://` (in-process dict, resets on server restart)

---

## 3. Payment Gateway

### Implementation: Mock/Simulated
- **File**: `app/services/payment_gateway.py`
- **Mode**: Configurable via `Config.MOCK_PAYMENT_MODE = "always_succeed"` (default) or `"random_fail"`
- **Random failure rate**: `Config.MOCK_FAILURE_RATE = 0.1` (10%)
- **Card types accepted (mock)**: Visa, Mastercard, M-Pesa (simulated)
- **Refunds**: Simulated -- marks `PaymentTransaction.status = "refunded"`, sets `refund_amount`/`refund_id`
- **Order cancellation**: Stock restored, mock refund processed
- **Security**: Payment route requires step-up biometric auth (fresh verification within 2 minutes). Transaction amounts recalculated server-side (not trusted from client). Idempotency key (`order.uuid`) prevents duplicate charges.

### Why mock?
- Development/LAN environment -- no real payment processor needed. Design allows drop-in replacement: swap `app/services/payment_gateway.py` with Stripe/dLocal API calls.

---

## 4. All API Endpoints & Security

### Blueprint Routing Table

#### Auth (`app/routes/auth.py`, prefix `/auth`)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/auth/login` | No | Login page |
| POST | `/auth/login` | No | Login with credentials (rate-limited 10/min) |
| GET | `/auth/logout` | Yes | Logout |
| GET | `/auth/register` | No | Registration page |
| POST | `/auth/register` | No | Register new user |
| GET | `/auth/biometric-setup` | Yes | WebAuthn registration page |
| POST | `/auth/biometric-setup/begin` | Yes | Start WebAuthn registration (returns challenge) |
| POST | `/auth/biometric-setup/complete` | Yes | Complete WebAuthn registration (store credential) |
| GET | `/auth/biometric-verify` | Yes | WebAuthn authentication page |
| POST | `/auth/biometric-verify/begin` | Yes | Start WebAuthn auth challenge |
| POST | `/auth/biometric-verify/complete` | Yes | Complete WebAuthn auth (verify signature) |
| GET | `/auth/disable-biometric` | Yes | Disable biometric page |
| POST | `/auth/disable-biometric` | Yes | Disable with password confirm |
| GET | `/auth/profile` | Yes | User profile page |
| POST | `/auth/profile` | Yes | Update profile |
| GET | `/auth/totp-setup` | Yes | TOTP setup page |
| POST | `/auth/totp-setup` | Yes | Enable TOTP |
| POST | `/auth/totp-disable` | Yes | Disable TOTP |
| GET | `/auth/totp-verify` | Yes | TOTP verify page |
| POST | `/auth/totp-verify` | Yes | Verify TOTP code |
| GET | `/auth/verify-email/<token>` | No | Email verification link |
| POST | `/auth/resend-verification` | Yes | Resend verification email |
| GET | `/auth/forgot-password` | No | Forgot password page |
| POST | `/auth/forgot-password` | No | Send reset link |
| GET | `/auth/reset-password/<token>` | No | Reset password page |
| POST | `/auth/reset-password/<token>` | No | Execute password reset |

#### Main (`app/routes/main.py`, prefix `/`)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/` | No | Homepage |
| POST | `/contact` | No | Submit contact form |
| GET | `/about` | No | About page |

#### Products (`app/routes/products.py`, prefix `/products`)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/products` | No | Product listing (filters, search, sort, pagination) |
| GET | `/products/<slug>` | No | Product detail page |

#### Cart (`app/routes/cart.py`, prefix `/cart`)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/cart` | Yes | View cart |
| POST | `/cart/add/<int:product_id>` | Yes | Add item |
| POST | `/cart/update/<int:item_id>` | Yes | Update quantity (AJAX) |
| POST | `/cart/remove/<int:item_id>` | Yes | Remove item (AJAX) |
| GET | `/cart/count` | Yes | Cart item count (AJAX) |

#### Payment (`app/routes/payment.py`, prefix `/payment`)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/payment/checkout` | Yes | Checkout page |
| POST | `/payment/checkout` | Yes | Place order + process payment |
| GET | `/payment/order-confirmation/<int:id>` | Yes | Order confirmation |
| GET | `/payment/order-history` | Yes | User's order history |
| POST | `/payment/order/<int:id>/cancel` | Yes | Cancel order |
| POST | `/payment/apply-coupon` | Yes | Apply coupon (AJAX) |
| POST | `/payment/remove-coupon` | Yes | Remove coupon (AJAX) |
| GET | `/payment/my-transactions` | Yes | Transaction history |

#### Admin (`app/routes/admin.py`, prefix `/admin`) -- all require Login + Admin

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/admin` | Dashboard |
| GET/POST | `/admin/products` | Product list |
| GET/POST | `/admin/products/create` | Create product |
| GET/POST | `/admin/products/<int:id>/edit` | Edit product |
| POST | `/admin/products/<int:id>/delete` | Delete product |
| GET | `/admin/sellers` | Seller list |
| GET | `/admin/sellers/<int:id>` | Seller detail |
| POST | `/admin/sellers/<int:id>/verify` | Toggle seller verification |
| GET | `/admin/users` | User list |
| GET | `/admin/users/<int:id>` | User detail |
| GET | `/admin/orders` | Order list |
| GET/POST | `/admin/orders/<int:id>` | Order detail + update status |
| GET | `/admin/transactions` | Transaction list |
| GET/POST | `/admin/coupons` | Coupon list + create |
| POST | `/admin/coupons/<int:id>/delete` | Delete coupon |
| GET/POST | `/admin/shipping-zones` | Shipping zone list + create |
| GET | `/admin/reviews` | Review moderation list |
| POST | `/admin/reviews/<int:id>/hide` | Hide review |
| POST | `/admin/reviews/<int:id>/unhide` | Unhide review |
| POST | `/admin/reviews/<int:id>/delete` | Delete review |
| GET | `/admin/contact-messages` | Contact messages list |
| GET/POST | `/admin/contact-messages/<int:id>` | Message detail + reply |
| POST | `/admin/contact-messages/<int:id>/delete` | Delete message |

#### Seller (`app/routes/seller.py`, prefix `/seller`) -- Login + Seller role

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/seller` | Dashboard |
| GET | `/seller/products` | Product list (own) |
| GET/POST | `/seller/products/create` | Create product |
| GET/POST | `/seller/products/<int:id>/edit` | Edit product |
| POST | `/seller/products/<int:id>/delete` | Deactivate product |
| GET | `/seller/orders` | Orders for seller's products |
| GET | `/seller/ratings` | Ratings page |

#### Chat (`app/routes/chat.py`, prefix `/chat`)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/chat` | Yes | Inbox |
| GET | `/chat/with/<int:user_id>` | Yes | Conversation |
| GET | `/chat/with/<int:user_id>/<int:product_id>` | Yes | Product conversation |
| POST | `/chat/send` | Yes | Send message |
| GET | `/chat/api/unread` | Yes | Unread count (AJAX) |

#### Notifications (`app/routes/notifications.py`, prefix `/notifications`)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/notifications` | Yes | List all |
| GET/POST | `/notifications/read/<int:id>` | Yes | Read + redirect to link |
| POST | `/notifications/read-all` | Yes | Mark all read |
| POST | `/notifications/delete/<int:id>` | Yes | Delete one |
| POST | `/notifications/delete-all` | Yes | Delete all |

#### Support Tickets (`app/routes/support.py`, prefix `/support`)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/support` | Login (buyer) | My tickets |
| GET/POST | `/support/create` | Login (buyer) | Create ticket |
| GET | `/support/<int:id>` | Login (buyer) | Ticket detail |
| POST | `/support/<int:id>/reply` | Login (buyer) | Reply |
| POST | `/support/<int:id>/close` | Login (buyer) | Close |
| GET | `/support/admin` | Login + Admin | All tickets |
| GET | `/support/admin/<int:id>` | Login + Admin | Ticket detail |
| POST | `/support/admin/<int:id>/reply` | Login + Admin | Reply |
| POST | `/support/admin/<int:id>/status` | Login + Admin | Change status |

#### Wishlist (`app/routes/wishlist.py`, prefix `/wishlist`)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/wishlist/toggle/<int:product_id>` | Yes | Toggle (AJAX) |
| GET | `/wishlist` | Yes | View |
| POST | `/wishlist/remove/<int:product_id>` | Yes | Remove |
| GET | `/wishlist/count` | Yes | Count (AJAX) |

#### Auth0 (`app/routes/auth0_bp.py`, prefix `/auth0`)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/auth0/login` | No | Initiate Auth0 SSO |
| GET | `/auth0/callback` | No | Auth0 OAuth callback |

#### Ratings (`app/routes/ratings.py`, prefix `/ratings`)

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/ratings/product/<int:product_id>` | Yes | Submit rating |
| POST | `/ratings/product/<int:product_id>/vote/<int:rating_id>` | Yes | Vote on review |

### 4.1 Authentication Summary
- **Public routes**: Home, product listing/detail, login/register page, password reset
- **User routes**: Cart, payment, orders, profile, chat, notifications, wishlist -- require `@login_required`
- **Seller routes**: All `/seller/*` require `@login_required` + `role == "seller"` in `before_request`
- **Admin routes**: All `/admin/*` require `@login_required` + `@admin_required` via `before_request`
- **AJAX endpoints**: Protected by `@login_required` and CSRF via `X-CSRFToken` header

### 4.2 Security Per Endpoint
- **CSRF**: Every `POST`/`PUT`/`DELETE` protected by Flask-WTF
- **Rate limiting**: Auth endpoints per-IP; global 200/day, 50/hour
- **Input sanitization**: `sanitize_input()` strips HTML, trims whitespace, limits length
- **Authorization**: Seller/admin `before_request` guards; owner checks on tickets, products, orders
- **Biometric gate**: Step-up auth for payment; full gate for biometric users after login
- **Audit logging**: `log_audit()` on all security events

---

## 5. Security Architecture

### Content Security Policy
```
default-src 'self'
script-src 'self' 'nonce-{nonce}' https://cdnjs.cloudflare.com
script-src-attr 'unsafe-inline'
style-src 'self' 'unsafe-inline'
img-src 'self' data: https:{auth0_domain}
font-src 'self'
connect-src 'self'
frame-ancestors 'none'
```
- Nonce generated per-request (`secrets.token_hex(16)`) -- all `<script>` tags include `nonce="{{ nonce }}"`
- Inline event handlers (`onclick`, etc.) allowed via `script-src-attr 'unsafe-inline'`

### HTTP Security Headers
| Header | Value |
|--------|-------|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `X-XSS-Protection` | `1; mode=block` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `geolocation=(), microphone=(), camera=(), payment=()` |
| `Strict-Transport-Security` | Production only: `max-age=31536000; includeSubDomains` |

### Request-Level Security
- **Session fingerprinting**: HMAC-SHA256 of `{remote_addr}|{user_agent}` verified on every request via `before_request`
- **CSRF**: Flask-WTF global, all POST forms + AJAX fetch use token
- **Rate limiting**: 200/day global, 10/min on login, 10/min on biometric verify
- **Input sanitization**: `bleach` library strips dangerous HTML from all user inputs
- **File uploads**: Extension whitelist (png/jpg/jpeg/jfif/jfi/gif/webp/pdf), 16MB limit, UUID rename
- **Field-level encryption**: PBKDF2-Fernet encrypts `phone` and `tax_id` columns
- **Biometric gate**: Blocks navigation until re-authenticated (3 failures = logout)

### HTTPS
- mkcert auto-generates certs on every startup for: `localhost`, `127.0.0.1`, `{hostname}.local`, LAN IP
- Development: self-signed (browser warning expected)
- Production target: gunicorn with proper CA-signed cert

---

## 6. Database Models (22 tables)

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `user` | Core user accounts (all roles) | id, uuid, username, email, password_hash, role, store_name, is_admin, is_seller_verified, biometric_enabled, totp_secret, trust_score, failed_login_attempts, locked_until |
| `category` | Product categories | id, name, slug |
| `product` | Products with pricing/stock | id, uuid, name, slug, price, stock, image_url, seller_id, category_id, is_active, free_shipping, rating |
| `product_image` | Additional product images (gallery) | id, product_id, image_url, sort_order, is_primary |
| `cart_item` | Shopping cart items | id, user_id, product_id, quantity -- unique per user+product |
| `order` | Orders with payment/shipping | id, uuid, user_id, total_amount, status, payment_status, payment_method, coupon_id, shipping_cost |
| `order_item` | Line items within orders | id, order_id, product_id, product_name, quantity, unit_price |
| `password_reset_token` | Password reset tokens | id, user_id, token, expires_at, used |
| `verification_code` | Email verification codes | id, user_id, code, purpose, expires_at, used |
| `audit_log` | All security + admin actions | id, user_id, action, details, ip_address, user_agent, timestamp |
| `notification` | System-generated alerts (bell) | id, user_id, title, message, link, is_read, created_at |
| `message` | User-to-user chat | id, sender_id, receiver_id, product_id, subject, body, is_read |
| `trusted_device` | Device fingerprint records | id, user_id, device_fingerprint, is_trusted -- unique per device |
| `payment_transaction` | Payment gateway records | id, order_id, transaction_id, amount, status, payment_method, refund_id |
| `product_rating` | Product reviews (with moderation) | id, product_id, user_id, order_id, rating, review, is_hidden, hidden_by, hide_reason |
| `seller_rating` | Seller ratings | id, seller_id, user_id, order_id, rating, review |
| `contact_message` | Contact form submissions | id, name, email, subject, message, is_read, is_replied, reply_message, replied_by_id |
| `wishlist_item` | User wishlist | id, user_id, product_id -- unique per user+product |
| `coupon` | Discount coupons | id, code, discount_type, discount_value, min_order_amount, max_uses, used_count, is_active |
| `shipping_zone` | Shipping cost rules by country | id, name, countries (JSON), base_rate, free_threshold, estimated_days |
| `support_ticket` | Customer support tickets | id, user_id, subject, message, status, priority |
| `ticket_reply` | Replies on support tickets | id, ticket_id, user_id, message |

---

## 7. Audit Trail (56+ event types)

All logged to `AuditLog` table with user_id, action, details, IP, user_agent, timestamp:

| Category | Events |
|----------|--------|
| Auth | REGISTER, LOGIN_SUCCESS, LOGIN_FAILED, LOGIN_LOCKED, LOGOUT, SESSION_HIJACK_DETECTED, AUTH0_LOGIN |
| Biometric | BIOMETRIC_ENABLE, BIOMETRIC_VERIFY, BIOMETRIC_DISABLE |
| TOTP | TOTP_ENABLED, TOTP_DISABLED |
| Password | PASSWORD_CHANGE, PASSWORD_RESET, CHANGE_PW_REQUEST |
| Admin | ADMIN_SELLER_VERIFY, ADMIN_USER_TOGGLE, ADMIN_PRODUCT_*, ADMIN_ORDER_UPDATE, ADMIN_REFUND, ADMIN_REVIEW_*, ADMIN_TICKET_* |
| Seller | SELLER_PRODUCT_CREATE, SELLER_PRODUCT_UPDATE, SELLER_PRODUCT_DELETE |
| Payment | PAYMENT_SUCCESS, ORDER_CANCELLED, ORDER_CREATED |
| Messaging | MESSAGE_SENT |
| Support | TICKET_CREATE, TICKET_REPLY, TICKET_CLOSE |

---

## 8. Key Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| JSON i18n (not Flask-Babel) | Avoid `.po`/`.mo` compilation toolchain |
| SQLite (not PostgreSQL) | Zero-config for dev; same ORM code works with Postgres in production |
| Custom CSS (no Bootstrap) | Lightweight; full visual control; no unused CSS |
| Mock payment (not real Stripe) | Demo/testing; swappable via `MockPaymentGateway` class |
| mkcert HTTPS (not Let's Encrypt) | LAN-only dev; no public domain needed |
| Session fingerprinting | Prevents session hijacking even if cookies stolen |
| Biometric gate after login | Ensures user is who they claim; can't skip if enabled |
| ALTER TABLE at startup | Avoids migration tooling; lazy column addition for evolving schema |
| `step_up_auth` decorator | Extra verification for sensitive pages (dashboard, payment) |
| `@admin_required` decorator | Separate admin role check from `@login_required` |
| Vanilla JS (no framework) | Server-rendered app; no JS build toolchain needed |
