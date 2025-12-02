#!/usr/bin/env python3
"""
Add French translations for testing and reports dashboards
"""

TRANSLATIONS = {
    # Testing Dashboard
    "Testing Dashboard": "Tableau de bord des tests",
    "Active Tests": "Tests actifs",
    "Queued Tests": "Tests en attente",
    "Completed Today": "Complétés aujourd'hui",
    "Failed Tests": "Tests échoués",
    "Quick Test": "Test rapide",
    "URL to test": "URL à tester",
    "Enter URL to test (e.g., https://example.com)": "Entrez l'URL à tester (ex : https://example.com)",
    "Recent Test Results": "Résultats de test récents",
    "Test Date": "Date du test",
    "Duration": "Durée",
    "Complete": "Terminé",
    "No recent test results": "Aucun résultat de test récent",
    "Please enter a URL to test": "Veuillez entrer une URL à tester",
    "Quick test functionality will be implemented": "La fonctionnalité de test rapide sera implémentée",

    # Reports Dashboard
    "Reports": "Rapports",
    "Accessibility Report": "Rapport d'accessibilité",
    "Comprehensive accessibility testing results": "Résultats complets des tests d'accessibilité",
    "Discovery Report": "Rapport de découverte",
    "Discover content requiring manual inspection": "Découvrir le contenu nécessitant une inspection manuelle",
    "Generate Discovery Report": "Générer un rapport de découverte",
    "Site Structure": "Structure du site",
    "Hierarchical view of website organization": "Vue hiérarchique de l'organisation du site Web",
    "Generate Structure": "Générer la structure",
    "Offline Report (Static HTML)": "Rapport hors ligne (HTML statique)",
    "Multi-page offline report with filters, scores, and full issue details (ZIP download)": "Rapport hors ligne multi-pages avec filtres, scores et détails complets des problèmes (téléchargement ZIP)",
    "Generate Offline Report": "Générer un rapport hors ligne",
    "Deduplicated Offline Report": "Rapport hors ligne dédupliqué",
    "Single-page offline report with issues grouped by common components (ZIP download)": "Rapport hors ligne sur une seule page avec problèmes groupés par composants communs (téléchargement ZIP)",
    "Generate Deduplicated Report": "Générer un rapport dédupliqué",
    "Recordings Report": "Rapport des enregistrements",
    "Manual accessibility audit findings from recorded testing sessions": "Résultats d'audit d'accessibilité manuel des sessions de test enregistrées",
    "Generate Recordings Report": "Générer un rapport des enregistrements",
    "Recent Reports": "Rapports récents",
    "Report Name": "Nom du rapport",
    "Type": "Type",
    "Generated": "Généré",
    "Size": "Taille",
    "No reports generated yet. Click \"Generate Report\" to create your first report.": "Aucun rapport généré pour le moment. Cliquez sur « Générer un rapport » pour créer votre premier rapport.",

    # Modal forms
    "Report Type": "Type de rapport",
    "Date Range": "Plage de dates",
    "Include in Report": "Inclure dans le rapport",
    "Accessibility Violations": "Violations d'accessibilité",
    "AI Analysis Results": "Résultats de l'analyse IA",
    "Executive Summary": "Résumé exécutif",

    # Common strings
    "Cancel": "Annuler",
    "All Projects": "Tous les projets",
    "Select a project first...": "Sélectionnez d'abord un projet...",
    "All Websites": "Tous les sites Web",
}

def update_po_file(po_path):
    """Update the .po file with French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translations_added = 0

    for english, french in TRANSLATIONS.items():
        english_escaped = english.replace('"', '\\"')
        french_escaped = french.replace('"', '\\"')

        pattern1 = f'msgid "{english_escaped}"\nmsgstr ""'
        replacement1 = f'msgid "{english_escaped}"\nmsgstr "{french_escaped}"'

        if pattern1 in content:
            content = content.replace(pattern1, replacement1)
            translations_added += 1
            print(f"✓ Added: {english}")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Total: Added {translations_added} translations")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
