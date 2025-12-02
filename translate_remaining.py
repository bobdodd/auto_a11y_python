#!/usr/bin/env python3
"""
Script to translate all remaining untranslated strings in the French catalog.
This focuses on application-specific strings, not library/framework strings.
"""

# Comprehensive French translations for all remaining strings
TRANSLATIONS = {
    # Help/About page strings
    "The WCAG Success Criteria data used in this application is sourced from:":
        "Les données des critères de succès WCAG utilisées dans cette application proviennent de :",
    "Auto A11y provides two types of scores based on your testing approach:":
        "Auto A11y fournit deux types de scores basés sur votre approche de test :",
    "Within each testing type (automated or manual), you'll see two scores:":
        "Dans chaque type de test (automatisé ou manuel), vous verrez deux scores :",
    "Why is my compliance score so much lower than my accessibility score?":
        "Pourquoi mon score de conformité est-il beaucoup plus bas que mon score d'accessibilité ?",
    "Real browser testing with Puppeteer ensures accurate DOM-based results":
        "Les tests dans un navigateur réel avec Puppeteer garantissent des résultats précis basés sur le DOM",

    # Testing/Configuration strings
    "The accessibility test is running. The page will refresh when complete.":
        "Le test d'accessibilité est en cours. La page se rafraîchira une fois terminé.",
    "Comma-separated list of user roles for testing role-based content":
        "Liste séparée par des virgules des rôles d'utilisateur pour tester le contenu basé sur les rôles",
    "Roles help you test content that varies based on user permissions.":
        "Les rôles aident à tester le contenu qui varie selon les permissions utilisateur.",
    "Leave the password field blank to keep the current password unchanged.":
        "Laissez le champ mot de passe vide pour conserver le mot de passe actuel inchangé.",
    "Standard compliance (4.5:1 contrast for normal text, 3:1 for large text)":
        "Conformité standard (contraste 4,5:1 pour le texte normal, 3:1 pour le texte large)",
    "Enhanced compliance (7:1 contrast for normal text, 4.5:1 for large text)":
        "Conformité renforcée (contraste 7:1 pour le texte normal, 4,5:1 pour le texte large)",
    "DOM Content Loaded (Fast, for sites with heavy background activity)":
        "Chargement du contenu DOM (Rapide, pour les sites avec beaucoup d'activité en arrière-plan)",
    "Wait until network has ≤2 connections (best for dynamic sites)":
        "Attendre jusqu'à ce que le réseau ait ≤2 connexions (idéal pour les sites dynamiques)",
    "Run browser invisibly (faster, less resource intensive)":
        "Exécuter le navigateur de manière invisible (plus rapide, moins de ressources)",
    "Verifies logical reading sequence matches visual layout":
        "Vérifie que la séquence de lecture logique correspond à la disposition visuelle",
    "This test documentation is pending review and may be incomplete.":
        "Cette documentation de test est en attente de révision et peut être incomplète.",
    "An error occurred while loading the test details. Please try again.":
        "Une erreur s'est produite lors du chargement des détails du test. Veuillez réessayer.",
    "Enter font names, one per line (e.g., 'Custom Font Name')":
        "Entrez les noms de police, un par ligne (ex : 'Nom de police personnalisée')",

    # Website/Discovery strings
    "No websites added yet. Add a website to start testing.":
        "Aucun site web ajouté pour le moment. Ajoutez un site web pour commencer les tests.",
    "Please select at least one user for discovery (or Guest).":
        "Veuillez sélectionner au moins un utilisateur pour la découverte (ou Invité).",
    "The compliance score is calculated based on WCAG 2.2 Level AA criteria":
        "Le score de conformité est calculé selon les critères WCAG 2.2 Niveau AA",
    "Usually checked - test the page in its final state after setup":
        "Généralement coché - teste la page dans son état final après la configuration",
    "Clear cookies and storage before testing to ensure a clean starting state":
        "Effacer les cookies et le stockage avant les tests pour assurer un état de départ propre",
    "Recommended for cookie banner testing - ensures banner appears":
        "Recommandé pour tester les bannières de cookies - garantit l'apparition de la bannière",

    # Script/Action strings
    "Define the actions to perform. Steps execute in order from top to bottom.":
        "Définissez les actions à effectuer. Les étapes s'exécutent dans l'ordre de haut en bas.",
    "Please add at least one step to the script.":
        "Veuillez ajouter au moins une étape au script.",

    # Results/Status strings
    "No violations found! The page passes all automated accessibility checks.":
        "Aucune violation trouvée ! La page réussit toutes les vérifications d'accessibilité automatisées.",
    "No test users configured. Discovery will run as guest.":
        "Aucun utilisateur de test configuré. La découverte s'exécutera en tant qu'invité.",
    "No test users configured. Testing will run as guest.":
        "Aucun utilisateur de test configuré. Les tests s'exécuteront en tant qu'invité.",
    "Please select at least one test user (or Guest) to continue.":
        "Veuillez sélectionner au moins un utilisateur de test (ou Invité) pour continuer.",
    "This will also delete all test results for this page.":
        "Ceci supprimera également tous les résultats de test pour cette page.",
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
            print(f"✓ Added translation: {english[:70]}...")
            continue

        # Pattern 2: Multi-line msgid (split with escaped quotes)
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
                    print(f"✓ Added translation (multi-line): {english[:70]}...")
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
