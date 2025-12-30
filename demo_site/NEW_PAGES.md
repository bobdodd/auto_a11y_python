# New Login and Dashboard Pages

Added user login and dashboard functionality to the demo site.

## New Pages Created

### 1. login.html / login-en.html (French/English)

**Purpose**: User login page

**URL**: 
- http://127.0.0.1:5001/demo/login.html (French)
- http://127.0.0.1:5001/demo/login-en.html (English)

**Intentional Accessibility Issues**:
- **Missing label on email field**: Input has placeholder but no associated label
- **Poor contrast on "Remember me" checkbox**: Label has color: #999 on light background
- **Mixed language content**: English and French mixed without lang attributes
- **Fake headings**: "Avantages de votre espace client" uses div instead of h2

**Features**:
- Email and password inputs
- Remember me checkbox
- Forgot password / Create account links
- Security notice
- Benefits list

**Form Action**: Submits to dashboard.html / dashboard-en.html

---

### 2. dashboard.html (French)

**Purpose**: User account dashboard with summary data

**URL**: http://127.0.0.1:5001/demo/dashboard.html

**Account Summary Data**:
- **User**: Marie Tremblay
- **Active Policies**: 3 policies
  - Auto Insurance (Toyota Camry 2022) - AUTO-2024-789456
  - Home Insurance (1234 Rue Principale) - HOME-2024-123789  
  - Life Insurance ($500,000 coverage) - LIFE-2024-456123

- **Payment Status**:
  - Next payment: $289.45 due January 15, 2026
  - Payment method: Automatic withdrawal
  - Status: Up to date

- **Recent Claims**:
  - Auto - Minor collision
  - Claim #: CLM-2025-998877
  - Filed: December 15, 2025
  - Status: In progress

- **Coverage Summary Table**:
  - Auto: $1,000,000 coverage, $124.99/month, expires June 30, 2026
  - Home: $350,000 coverage, $89.99/month, expires August 15, 2026
  - Life: $500,000 coverage, $74.47/month, expires December 1, 2026

- **Account Information**:
  - Name: Marie Tremblay
  - Email: marie.tremblay@example.com
  - Phone: (514) 555-0123
  - Address: 1234 Rue Principale, Montréal, QC H3B 1A1
  - Member since: January 2020

**Intentional Accessibility Issues**:
- **Fake headings throughout**: All section titles use div with .fake-heading class
- **Mixed language content**: English and French mixed without lang attributes
- **Data table without proper headers**: Coverage table uses <td> for headers instead of <th>
- **Icon buttons without accessible names**: Quick actions buttons missing aria-labels

**Dashboard Cards**:
1. Active Policies (3 policies listed)
2. Payment Status (next payment info)
3. Recent Claims (1 claim in progress)
4. Quick Actions (icon buttons for new claim, documents, help)
5. Coverage Summary (data table)
6. Account Information (personal details)

---

## CSS Added

New styles in `styles.css` for:
- Login page layout (2-column grid)
- Form inputs and styling
- Security notice banner
- Dashboard grid layout
- Dashboard cards
- Status badges (good/warning)
- Data tables
- Icon buttons
- Responsive mobile layout

---

## Integration

**Navigation Links**:
- "Connexion" / "Login" added to main nav on homepages
- Dashboard accessible after "login" (no actual authentication)

**Language Switching**:
- Both login and dashboard have FR/EN switchers
- Consistent with rest of site

---

## Intentional Issues Summary

### Login Pages
1. Missing form label (email field)
2. Low contrast text (remember me label: #999)
3. Mixed languages without lang attributes
4. Fake heading instead of semantic h2

### Dashboard Page
1. Multiple fake headings (divs styled as headings)
2. Mixed languages throughout without lang attributes
3. Data table without <th> headers (uses <td>)
4. Icon buttons in quick actions without accessible names

---

## Demo Flow

1. User visits homepage → clicks "Connexion"
2. Arrives at login page with form
3. Submits form (any input works, no validation)
4. Redirected to dashboard with account summary
5. Dashboard shows realistic insurance data:
   - 3 active policies
   - Payment status
   - Recent claim
   - Coverage details
   - Account information

This provides a complete user journey for accessibility testing!
