#!/usr/bin/env python3
"""
Script to add ALL remaining French translations for projects/create.html
Based on the actual visible English text from the page
"""

# French translations for ALL remaining untranslated strings
TRANSLATIONS = {
    # Page title and headers
    "Create New Project": "Créer un nouveau projet",

    # Test availability notice
    "Test Availability:": "Disponibilité des tests :",
    "Only tests that passed fixture validation are enabled.": "Seuls les tests ayant réussi la validation des fixtures sont activés.",
    "View Fixture Status": "Voir l'état des fixtures",

    # Form fields
    "Project Name": "Nom du projet",
    "Choose a unique name for your project": "Choisissez un nom unique pour votre projet",
    "Optional project description": "Description optionnelle du projet",
    "Project Type": "Type de projet",
    "Select the type of project you are testing": "Sélectionnez le type de projet que vous testez",

    # Drupal audit
    "Drupal Audit (Optional)": "Audit Drupal (optionnel)",
    'Select the corresponding audit in Drupal for synchronization. Leave as "Auto-match" to use the project name.':
        'Sélectionnez l\'audit correspondant dans Drupal pour la synchronisation. Laissez "Correspondance automatique" pour utiliser le nom du projet.',
    "Loading audits...": "Chargement des audits...",

    # WCAG Level
    "WCAG Compliance Level": "Niveau de conformité WCAG",
    "Level AA:": "Niveau AA :",
    "Standard compliance (4.5:1 contrast for normal text, 3:1 for large text)":
        "Conformité standard (contraste 4.5:1 pour le texte normal, 3:1 pour le texte large)",
    "Level AAA:": "Niveau AAA :",
    "Enhanced compliance (7:1 contrast for normal text, 4.5:1 for large text)":
        "Conformité renforcée (contraste 7:1 pour le texte normal, 4.5:1 pour le texte large)",

    # Page load strategy
    "Page Load Strategy": "Stratégie de chargement de page",
    "Controls when testing begins after navigating to a page:":
        "Contrôle quand les tests commencent après la navigation vers une page :",
    "Network Idle 2": "Network Idle 2",
    "Wait until network has ≤2 connections (best for dynamic sites)":
        "Attendre jusqu'à ce que le réseau ait ≤2 connexions (idéal pour les sites dynamiques)",
    "Network Idle 0": "Network Idle 0",
    "Wait until network is completely idle (very thorough but slow)":
        "Attendre que le réseau soit complètement inactif (très complet mais lent)",
    "DOM Content Loaded": "DOM Content Loaded",
    "Test as soon as DOM is ready (use for BBC News, sites with continuous ads/analytics)":
        "Tester dès que le DOM est prêt (à utiliser pour BBC News, sites avec publicités/analytics en continu)",
    "Load Event": "Load Event",
    "Wait for load event (faster than network idle)":
        "Attendre l'événement de chargement (plus rapide que network idle)",

    # Browser display mode
    "Browser Display Mode": "Mode d'affichage du navigateur",
    "Headless": "Sans interface",
    "Run browser invisibly (faster, less resource intensive)":
        "Exécuter le navigateur de manière invisible (plus rapide, moins de ressources)",
    "Visible Browser": "Navigateur visible",
    "Show the Chrome window (useful for debugging)":
        "Afficher la fenêtre Chrome (utile pour le débogage)",

    # Stealth mode
    "Enable Stealth Mode (for Cloudflare-protected sites)":
        "Activer le mode furtif (pour les sites protégés par Cloudflare)",
    "Enables advanced bot detection bypass techniques. Use for sites protected by Cloudflare or similar services.":
        "Active les techniques avancées de contournement de détection de bot. À utiliser pour les sites protégés par Cloudflare ou des services similaires.",
    "Stealth mode significantly slows down page discovery and testing (~5-15 seconds per page).":
        "Le mode furtif ralentit considérablement la découverte et les tests de pages (~5-15 secondes par page).",

    # Touchpoint tests
    "Touchpoint Tests Configuration": "Configuration des tests de points de contact",
    "Configure which accessibility tests to run. Tests are organized by touchpoint (testing category).":
        "Configurez les tests d'accessibilité à exécuter. Les tests sont organisés par point de contact (catégorie de test).",

    # AI testing
    "AI-Assisted Testing": "Tests assistés par IA",
    "Enable AI-assisted accessibility testing":
        "Activer les tests d'accessibilité assistés par IA",
    "AI testing uses Claude to analyze screenshots and HTML for issues that automated tests might miss.":
        "Les tests IA utilisent Claude pour analyser les captures d'écran et le HTML afin de détecter les problèmes que les tests automatisés pourraient manquer.",
    "AI testing incurs API costs based on usage.":
        "Les tests IA entraînent des coûts d'API en fonction de l'utilisation.",
}

def update_po_file(po_path):
    """Update the .po file with French translations, handling multi-line msgid entries"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translations_added = 0

    # Process each translation
    for english, french in TRANSLATIONS.items():
        # Escape quotes in both english and french
        english_escaped = english.replace('"', '\\"')
        french_escaped = french.replace('"', '\\"')

        # Try to find and replace empty msgstr for this msgid
        # Pattern 1: Single-line msgid
        pattern1 = f'msgid "{english_escaped}"\nmsgstr ""'
        replacement1 = f'msgid "{english_escaped}"\nmsgstr "{french_escaped}"'

        if pattern1 in content:
            content = content.replace(pattern1, replacement1)
            translations_added += 1
            print(f"✓ Added translation (single-line): {english[:60]}...")
            continue

        # Pattern 2: Multi-line msgid (split with escaped quotes)
        # Need to match the actual multi-line format in the file
        lines = content.split('\n')
        i = 0
        found = False
        while i < len(lines) and not found:
            if lines[i].startswith('msgid "'):
                # Collect full msgid (might be multi-line)
                msgid_parts = []
                j = i

                # Handle msgid "" followed by continuation lines
                if lines[j] == 'msgid ""' and j + 1 < len(lines) and lines[j + 1].startswith('"'):
                    j += 1
                    while j < len(lines) and lines[j].startswith('"') and not lines[j].startswith('msgstr'):
                        msgid_parts.append(lines[j][1:-1])  # Remove quotes
                        j += 1
                elif lines[j].startswith('msgid "') and not lines[j].endswith('""'):
                    # Single line msgid
                    msgid_parts.append(lines[j][7:-1])  # Remove 'msgid "' and '"'
                    j += 1

                # Reconstruct the full msgid string (unescape quotes)
                full_msgid = ''.join(msgid_parts).replace('\\"', '"')

                # Check if this matches our translation
                if full_msgid == english and j < len(lines) and lines[j] == 'msgstr ""':
                    # Found a match with empty translation
                    lines[j] = f'msgstr "{french_escaped}"'
                    translations_added += 1
                    print(f"✓ Added translation (multi-line): {english[:60]}...")
                    found = True
                    i = j + 1
                    continue

            i += 1

        if found:
            content = '\n'.join(lines)

    # Write back
    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Total: Added {translations_added} French translations to {po_path}")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
