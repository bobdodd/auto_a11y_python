#!/usr/bin/env python3
"""
Script to add French translations for JavaScript strings in projects/create.html
"""

# French translations for JavaScript-embedded strings
TRANSLATIONS = {
    # Loading states
    "Loading...": "Chargement...",
    "Loading test details...": "Chargement des détails du test...",
    "Refreshing...": "Actualisation...",
    "Updating...": "Mise à jour...",

    # Production ready status
    "Production Ready": "Prêt pour la production",
    "Pending Review": "En attente de révision",

    # Documentation status
    "Documentation Status:": "Statut de la documentation :",
    "This test has production-ready documentation.": "Ce test a une documentation prête pour la production.",
    "This test documentation is pending review and may be incomplete.": "Cette documentation de test est en attente de révision et peut être incomplète.",
    "Mark as": "Marquer comme",
    "Pending": "En attente",
    "Ready": "Prêt",

    # Test detail sections
    "What This Test Detects": "Ce que ce test détecte",
    "Why It Matters": "Pourquoi c'est important",
    "Who It Affects": "Qui cela affecte",
    "How to Fix": "Comment corriger",

    # Violation message templates
    "Violation Message Templates": "Modèles de messages de violation",
    "These are the actual message templates shown to users when violations are detected. Placeholders like {totalCount}, {role}, {element}, etc. are filled in dynamically.": "Ce sont les modèles de messages réels montrés aux utilisateurs lorsque des violations sont détectées. Les espaces réservés comme {totalCount}, {role}, {element}, etc. sont remplis dynamiquement.",
    "Title Template:": "Modèle de titre :",
    "What (Description) Template:": "Modèle Quoi (Description) :",
    "Why (Rationale) Template:": "Modèle Pourquoi (Justification) :",
    "Remediation Template:": "Modèle de remédiation :",

    # Error messages
    "Test Information Not Available": "Informations sur le test non disponibles",
    "Details for test": "Détails pour le test",
    "are not available in the catalog.": "ne sont pas disponibles dans le catalogue.",
    "Error Loading Test Details": "Erreur lors du chargement des détails du test",
    "An error occurred while loading the test details. Please try again.": "Une erreur s'est produite lors du chargement des détails du test. Veuillez réessayer.",

    # Drupal audit loading
    "Auto-match by project name": "Correspondance automatique par nom de projet",
    "Error:": "Erreur :",
    "No Drupal audits found": "Aucun audit Drupal trouvé",
    "Could not load audits (Drupal may not be configured)": "Impossible de charger les audits (Drupal n'est peut-être pas configuré)",
}

def update_po_file(po_path):
    """Update the .po file with French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    translations_added = 0

    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # Check if this is a msgid line
        if line.startswith('msgid "') and not line.startswith('msgid ""'):
            # Extract the msgid value
            msgid = line[7:-2]  # Remove 'msgid "' and '"\n'

            # Check if next line is msgstr ""
            if i + 1 < len(lines) and lines[i + 1] == 'msgstr ""\n':
                # Check if we have a translation for this
                if msgid in TRANSLATIONS:
                    new_lines.append(f'msgstr "{TRANSLATIONS[msgid]}"\n')
                    translations_added += 1
                    i += 2  # Skip the empty msgstr line
                    continue

        i += 1

    # Write back
    with open(po_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"✓ Added {translations_added} French translations to {po_path}")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
