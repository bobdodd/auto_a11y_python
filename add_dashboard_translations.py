#!/usr/bin/env python3
"""
Script to add French translations for the reports/dashboard.html page
"""

import polib

# Load the .po file
po = polib.pofile('auto_a11y/web/translations/fr/LC_MESSAGES/messages.po')

# Dictionary of English to French translations
translations = {
    # Main headings and buttons
    "Reports": "Rapports",
    "Generate Report": "Générer un rapport",

    # Report cards
    "Accessibility Report": "Rapport d'accessibilité",
    "Comprehensive accessibility testing results": "Résultats complets des tests d'accessibilité",
    "Discovery Report": "Rapport de découverte",
    "Discover content requiring manual inspection": "Découvrir le contenu nécessitant une inspection manuelle",
    "Site Structure": "Structure du site",
    "Hierarchical view of website organization": "Vue hiérarchique de l'organisation du site web",
    "Generate Structure": "Générer la structure",

    # Offline reports
    "Offline Report (Static HTML)": "Rapport hors ligne (HTML statique)",
    "Multi-page offline report with filters, scores, and full issue details (ZIP download)": "Rapport hors ligne multi-pages avec filtres, scores et détails complets des problèmes (téléchargement ZIP)",
    "Generate Offline Report": "Générer un rapport hors ligne",
    "Deduplicated Offline Report": "Rapport hors ligne dédupliqué",
    "Single-page offline report with issues grouped by common components (ZIP download)": "Rapport hors ligne d'une seule page avec les problèmes regroupés par composants communs (téléchargement ZIP)",
    "Generate Deduplicated Report": "Générer un rapport dédupliqué",
    "Recordings Report": "Rapport d'enregistrements",
    "Manual accessibility audit findings from recorded testing sessions": "Résultats d'audit d'accessibilité manuel issus de sessions de test enregistrées",
    "Generate Recordings Report": "Générer un rapport d'enregistrements",

    # Table headers
    "Recent Reports": "Rapports récents",
    "Report Name": "Nom du rapport",
    "Type": "Type",
    "Project": "Projet",
    "Generated": "Généré",
    "Size": "Taille",
    "Actions": "Actions",

    # Table values
    "All Projects": "Tous les projets",
    "Unknown": "Inconnu",
    "N/A": "N/D",
    "Download": "Télécharger",
    "Delete": "Supprimer",

    # Empty state
    'No reports generated yet. Click "Generate Report" to create your first report.': 'Aucun rapport généré pour le moment. Cliquez sur "Générer un rapport" pour créer votre premier rapport.',

    # Generate Report Modal
    "Report Type": "Type de rapport",
    "PDF Report": "Rapport PDF",
    "Excel Spreadsheet": "Feuille de calcul Excel",
    "JSON Export": "Export JSON",
    "HTML Report": "Rapport HTML",
    "Website": "Site web",
    "Select a project first...": "Sélectionnez d'abord un projet...",
    "Date Range": "Plage de dates",
    "Include in Report": "Inclure dans le rapport",
    "Accessibility Violations": "Violations d'accessibilité",
    "Warnings": "Avertissements",
    "AI Analysis Results": "Résultats de l'analyse IA",
    "Screenshots (increases file size)": "Captures d'écran (augmente la taille du fichier)",
    "Executive Summary": "Résumé exécutif",
    "Cancel": "Annuler",

    # Site Structure Modal
    "Generate Site Structure Report": "Générer un rapport de structure de site",
    "Select Project": "Sélectionner un projet",
    "Choose a project...": "Choisissez un projet...",
    "Select the project containing the website": "Sélectionnez le projet contenant le site web",
    "Select Website": "Sélectionner un site web",
    "First select a project...": "Sélectionnez d'abord un projet...",
    "Select the website to analyze its structure": "Sélectionnez le site web pour analyser sa structure",
    "Export Format": "Format d'export",
    "HTML (Interactive)": "HTML (Interactif)",
    "JSON (Data)": "JSON (Données)",
    "CSV (Spreadsheet)": "CSV (Feuille de calcul)",
    "This report will generate a hierarchical tree view of all pages in the selected website, organized by URL structure.": "Ce rapport génèrera une vue arborescente hiérarchique de toutes les pages du site web sélectionné, organisées par structure d'URL.",
    "Generate Structure Report": "Générer un rapport de structure",

    # Discovery Report Modal
    "Generate Discovery Report": "Générer un rapport de découverte",
    "This report discovers pages with content requiring manual accessibility inspection, including:": "Ce rapport découvre les pages avec du contenu nécessitant une inspection manuelle d'accessibilité, notamment :",
    "Discovery issues (content requiring human judgment)": "Problèmes de découverte (contenu nécessitant un jugement humain)",
    "Informational notices": "Avis informatifs",
    "Accessible name issues (forms, links, buttons)": "Problèmes de nom accessible (formulaires, liens, boutons)",
    "Elements with poor or missing labels": "Éléments avec des étiquettes manquantes ou insuffisantes",
    "Scope": "Portée",
    "Single Website": "Site web unique",
    "Entire Project": "Projet entier",
    "Select a project first": "Sélectionnez d'abord un projet",
    "All websites in the project will be included": "Tous les sites web du projet seront inclus",
    "Select the specific website to analyze": "Sélectionnez le site web spécifique à analyser",
    "HTML (Recommended)": "HTML (Recommandé)",
    "PDF": "PDF",

    # Static HTML Modal
    "Generate Offline Report (Static HTML)": "Générer un rapport hors ligne (HTML statique)",
    "This report generates a complete offline website with:": "Ce rapport génère un site web hors ligne complet avec :",
    "Index page with all tested pages": "Page d'index avec toutes les pages testées",
    "Summary page with statistics and charts": "Page de résumé avec statistiques et graphiques",
    "Individual page detail reports with full issue accordions": "Rapports détaillés de pages individuelles avec accordéons complets des problèmes",
    "Client-side filters and search": "Filtres et recherche côté client",
    "All CSS, JS, and images (ZIP download)": "Tous les CSS, JS et images (téléchargement ZIP)",
    "WCAG Level": "Niveau WCAG",
    "Level A": "Niveau A",
    "Level AA (Recommended)": "Niveau AA (Recommandé)",
    "Level AAA": "Niveau AAA",
    "Options": "Options",
    "Include Screenshots": "Inclure les captures d'écran",
    "Include Discovery Items": "Inclure les éléments de découverte",
    "Note:": "Note :",
    "Large reports may take several minutes to generate. The report will appear in the list below when complete.": "Les rapports volumineux peuvent prendre plusieurs minutes à générer. Le rapport apparaîtra dans la liste ci-dessous une fois terminé.",

    # Deduplicated Modal
    "This report generates a single-page offline HTML report with:": "Ce rapport génère un rapport HTML hors ligne d'une seule page avec :",
    "Issues deduplicated and grouped by common components": "Problèmes dédupliqués et regroupés par composants communs",
    "Common components table (navigation, headers, footers, forms, etc.)": "Tableau des composants communs (navigation, en-têtes, pieds de page, formulaires, etc.)",
    "Statistics dashboard with violation, warning, and info counts": "Tableau de bord des statistiques avec nombres de violations, d'avertissements et d'informations",
    "Client-side filters by component, type, and impact": "Filtres côté client par composant, type et impact",
    "Test user information for authenticated testing": "Informations sur les utilisateurs de test pour les tests authentifiés",

    # Recordings Modal
    "This report includes manual accessibility findings from:": "Ce rapport inclut les résultats manuels d'accessibilité issus de :",
    "Accessibility audit recordings": "Enregistrements d'audit d'accessibilité",
    "Lived experience testing sessions": "Sessions de test d'expérience vécue",
    "All issues organized by touchpoint and impact": "Tous les problèmes organisés par point de contact et impact",
    "Key takeaways and user painpoints": "Points clés et points de douleur des utilisateurs",
    "WCAG criteria mappings and remediation guidance": "Correspondances des critères WCAG et conseils de remédiation",
    "All recordings from this project will be included": "Tous les enregistrements de ce projet seront inclus",
    "Excel Spreadsheet": "Feuille de calcul Excel",
    "Timecodes": "Codes temporels",
    "WCAG Criteria": "Critères WCAG",
    "Group Issues by Touchpoint": "Regrouper les problèmes par point de contact",

    # JavaScript strings
    "Accessibility Report": "Rapport d'accessibilité",
    "Loading websites...": "Chargement des sites web...",
    "All Websites": "Tous les sites web",
    "No websites in this project": "Aucun site web dans ce projet",
    "Error loading websites": "Erreur lors du chargement des sites web",
    "Generating...": "Génération en cours...",
    "Failed to generate report: ": "Échec de la génération du rapport : ",
    "Unknown error": "Erreur inconnue",
    "Error generating report: ": "Erreur lors de la génération du rapport : ",
    "Are you sure you want to delete this report?": "Êtes-vous sûr de vouloir supprimer ce rapport ?",
    "Failed to delete report": "Échec de la suppression du rapport",
    "No projects available": "Aucun projet disponible",
    "Error loading projects": "Erreur lors du chargement des projets",
    "Please select a project and website": "Veuillez sélectionner un projet et un site web",
    "Please select a project": "Veuillez sélectionner un projet",
    "Please select a website": "Veuillez sélectionner un site web",
}

# Add translations to the .po file
for english, french in translations.items():
    entry = po.find(english)
    if entry:
        entry.msgstr = french
        # Remove fuzzy flag if present
        if 'fuzzy' in entry.flags:
            entry.flags.remove('fuzzy')
        print(f"✓ Translated: {english[:50]}...")
    else:
        print(f"✗ Not found: {english[:50]}...")

# Save the updated .po file
po.save('auto_a11y/web/translations/fr/LC_MESSAGES/messages.po')
print("\n✓ Translations saved successfully!")
