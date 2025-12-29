# Demo Site Rebranding Complete ✓

## Changes Made

The demo site has been successfully rebranded from "Quebec Government Services" to **"Assurance Québec Plus"** (Quebec Insurance Plus), a fictional insurance company.

### Why the Change?

- **Politically safer**: Avoids suggesting that government websites have accessibility issues
- **More appropriate**: Insurance companies are a better target for demonstrating accessibility testing
- **Realistic scenario**: Insurance sites commonly have the types of issues we're demonstrating

## Updated Content

### Company Name
- **French**: Assurance Québec Plus
- **English**: Quebec Insurance Plus

### Products/Services
Changed from government services to insurance products:
- **Assurance Auto** / Auto Insurance
- **Assurance Habitation** / Home Insurance
- **Assurance Vie** / Life Insurance

### Navigation
- Accueil / Home
- Assurances / Insurance (was: Services)
- Réclamations / Claims (was: Resources)
- Contact

### Content Changes

**Hero Carousel**:
- "Protection Complète pour Votre Famille" / "Complete Protection for Your Family"
- "Assurance Habitation et Auto" / "Home and Auto Insurance"
- "Services en Ligne 24/7" / "Online Services 24/7"

**Service Cards**:
- Insurance quotes and policy management
- Insurance guides (PDFs)
- Life insurance products

**Footer**:
- Notre compagnie / Our Company
- Produits (Assurance auto, habitation, vie)
- Service à la clientèle / Customer Service

### Quick Access Sidebar
- Faire une réclamation / File a claim
- Mes polices / My policies
- Payer ma prime / Pay my premium

## Files Updated

✅ `index.html` - French homepage
✅ `index-en.html` - English homepage
✅ `services.html` - Services page (French)
✅ `css/styles.css` - Color scheme (#003366 → #004d99)
✅ `demo_site/README.md` - Documentation
✅ `DEMO_SITE_SETUP.md` - Setup instructions
✅ `auto_a11y/web/routes/demo.py` - Route descriptions

## Accessibility Issues (Unchanged)

All intentional accessibility issues remain the same:
- ✓ ErrMissingAccessibleName
- ✓ ErrTimersWithoutControls
- ✓ ErrDocumentLinkWrongLanguage
- ✓ WarnInfiniteAnimationSpinner
- ✓ ErrInappropriateMenuRole
- ✓ Interactive map with aria-hidden
- ✓ Language switcher buried in tab order
- ✓ Fake headings (AI detection)
- ✓ Mixed language content (AI detection)
- ✓ Color contrast issues (desktop only)

## PDF Names Updated

- `guide-services-en.pdf` → `guide-habitation-en.pdf` (Home insurance guide)
- `guide-permis-fr.pdf` → `guide-assurance-fr.pdf` (Insurance guide)

## Color Scheme

Updated from government blue to insurance company blue:
- **Primary color**: #004d99 (deeper insurance blue)
- Maintains professional, trustworthy appearance
- Suitable for financial services sector

## Testing URLs (Unchanged)

- French homepage: http://127.0.0.1:5001/demo/
- English homepage: http://127.0.0.1:5001/demo/index-en.html
- Services page: http://127.0.0.1:5001/demo/services.html
- Demo info: http://127.0.0.1:5001/demo/info

## Presentation Talking Points

### Updated Context

Instead of: *"We're testing a Quebec government website..."*

Say: *"We're demonstrating with a Quebec insurance company website that serves bilingual customers across the province. Insurance companies must comply with accessibility regulations to serve all Quebecers fairly."*

### Why Insurance Companies?

- Subject to accessibility regulations
- Serve diverse customer base
- Critical services (claims, policies, payments)
- Complex forms and documentation
- Must be accessible for compliance and customer service

### Quebec Context Remains

- Bilingual French/English requirements
- Language switching requirements
- Document language warnings required
- Serves Quebec market specifically

## Ready for Presentation

The demo site is now:
- ✅ Politically neutral
- ✅ Realistic business scenario
- ✅ All accessibility issues intact
- ✅ Properly branded and professional
- ✅ Ready for Quebec audience presentation

**Next step**: Restart the autoA11y server to load the rebranded demo!
