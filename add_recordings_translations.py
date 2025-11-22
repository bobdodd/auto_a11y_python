#!/usr/bin/env python3
"""
Script to add French translations for recordings and edit templates
"""

# French translations for recordings and edit templates
TRANSLATIONS = {
    # Recordings
    "Recordings": "Enregistrements",
    "Manual Audit Recordings": "Enregistrements d'audits manuels",
    "Upload Recording": "Télécharger un enregistrement",
    "All Projects": "Tous les projets",
    "All Types": "Tous les types",
    "Audit": "Audit",
    "Lived Experience Website": "Expérience vécue - Site web",
    "Lived Experience App": "Expérience vécue - Application",
    "Lived Experience Tangible Device": "Expérience vécue - Appareil tangible",
    "Lived Experience Nav and Wayfinding": "Expérience vécue - Navigation et orientation",
    "No recordings found.": "Aucun enregistrement trouvé.",
    "Upload your first recording": "Téléchargez votre premier enregistrement",
    "to get started.": "pour commencer.",
    "Are you sure you want to delete this recording?": "Êtes-vous sûr de vouloir supprimer cet enregistrement ?",
    "Test Account": "Compte de test",
    "Issues": "Problèmes",
    "View Details": "Voir les détails",

    # Recording detail
    "Recording ID": "ID de l'enregistrement",
    "Auditor": "Auditeur",
    "Tester": "Testeur",
    "Test Supervisor": "Superviseur de test",
    "Test User Account": "Compte utilisateur de test",
    "Recording Date": "Date de l'enregistrement",
    "Duration": "Durée",
    "Recording Type": "Type d'enregistrement",
    "Project": "Projet",
    "Pages Covered": "Pages couvertes",
    "Discovered Pages": "Pages découvertes",
    "Common Components": "Composants communs",
    "App Screens / Views": "Écrans/Vues d'application",
    "Device Sections": "Sections de l'appareil",
    "Task Context": "Contexte de la tâche",
    "Media File": "Fichier média",
    "Issue Summary": "Résumé des problèmes",
    "Total Issues": "Total des problèmes",
    "High Impact": "Impact élevé",
    "Medium Impact": "Impact moyen",
    "Low Impact": "Impact faible",
    "Manual Testing Scores": "Scores des tests manuels",
    "Manual Accessibility Score": "Score d'accessibilité manuel",
    "Manual WCAG Compliance Score": "Score de conformité WCAG manuel",
    "Based on manually identified issue severity and impact": "Basé sur la gravité et l'impact des problèmes identifiés manuellement",
    "Level AA conformance based on manual testing scope": "Conformité niveau AA basée sur la portée des tests manuels",
    "Applicable": "Applicable",
    "Passed": "Réussi",
    "Failed": "Échoué",
    "Key Takeaways": "Points clés à retenir",
    "User Painpoints": "Points de douleur de l'utilisateur",
    "User Assertions": "Assertions de l'utilisateur",
    "Accessibility Issues": "Problèmes d'accessibilité",
    "No issues found in this recording.": "Aucun problème trouvé dans cet enregistrement.",

    # Issue details
    "User Quote:": "Citation de l'utilisateur :",
    "Timecode": "Code temporel",
    "Timecodes:": "Codes temporels :",
    "s": "s",
    "Start:": "Début :",
    "End:": "Fin :",
    "Context:": "Contexte :",
    "What:": "Quoi :",
    "Why:": "Pourquoi :",
    "Who is affected:": "Qui est affecté :",
    "How to fix:": "Comment corriger :",
    "Level": "Niveau",
    "Status:": "Statut :",
    "Open": "Ouvert",
    "In Progress": "En cours",
    "Resolved": "Résolu",
    "Verified": "Vérifié",
    "timecode(s)": "code(s) temporel(s)",

    # WCAG modal
    "WCAG Success Criteria Breakdown": "Répartition des critères de succès WCAG",
    "How Criteria Are Determined": "Comment les critères sont déterminés",
    "The compliance score is calculated based on WCAG 2.2 Level AA criteria": "Le score de conformité est calculé sur la base des critères WCAG 2.2 niveau AA",
    "Testing Scope": "Portée des tests",
    "Applicable Criteria": "Critères applicables",
    "Excluded Criteria": "Critères exclus",
    "Number": "Numéro",
    "Success Criterion": "Critère de succès",
    "View Criteria Details": "Voir les détails du critère",
    "View WCAG Quick Reference": "Voir la référence rapide WCAG",

    # Informational messages
    "No pages specified": "Aucune page spécifiée",
    "No discovered pages selected": "Aucune page découverte sélectionnée",
    "Loading discovered pages...": "Chargement des pages découvertes...",
    "Select discovered pages related to this recording": "Sélectionner les pages découvertes liées à cet enregistrement",
    "Enter one URL per line": "Entrez une URL par ligne",
    "Manual compliance score requires testing scope to be defined during upload.": "Le score de conformité manuel nécessite que la portée des tests soit définie lors du téléchargement.",

    # JavaScript messages
    "Failed to update status": "Échec de la mise à jour du statut",
    "Error updating status": "Erreur lors de la mise à jour du statut",
    "Status updated successfully": "Statut mis à jour avec succès",
    "Error saving recording:": "Erreur lors de l'enregistrement :",
    "Unknown error": "Erreur inconnue",
    "No project associated with this recording.": "Aucun projet associé à cet enregistrement.",
    "No discovered pages found for this project.": "Aucune page découverte trouvée pour ce projet.",
    "Error loading discovered pages.": "Erreur lors du chargement des pages découvertes.",

    # Edit website
    "Edit Website": "Modifier le site web",
    "Basic Information": "Informations de base",
    "Website Name": "Nom du site web",
    "Website URL": "URL du site web",
    "Optional display name": "Nom d'affichage optionnel",
    "Scraping Configuration": "Configuration de l'exploration",
    "Max Pages": "Pages maximum",
    "Maximum number of pages to discover (default: unlimited)": "Nombre maximum de pages à découvrir (par défaut : illimité)",
    "Max Depth": "Profondeur maximum",
    "How many clicks away from the starting page (default: 10)": "Combien de clics depuis la page de départ (par défaut : 10)",
    "Request Delay (seconds)": "Délai entre les requêtes (secondes)",
    "Delay between requests": "Délai entre les requêtes",
    "Follow external links": "Suivre les liens externes",
    "Include subdomains": "Inclure les sous-domaines",
    "Respect robots.txt": "Respecter robots.txt",
    "Update Website": "Mettre à jour le site web",

    # Edit page
    "Edit Page": "Modifier la page",
    "Page Information": "Informations sur la page",
    "Page Title": "Titre de la page",
    "Enter page title": "Entrer le titre de la page",
    "URL": "URL",
    "URL cannot be changed": "L'URL ne peut pas être modifiée",
    "Notes": "Notes",
    "Add any notes about this page": "Ajouter des notes sur cette page",
    "Save Changes": "Enregistrer les modifications",
    "Discovered:": "Découverte :",
    "Last Tested:": "Dernier test :",
    "Violations:": "Violations :",
    "Warnings:": "Avertissements :",

    # Common
    "breadcrumb": "fil d'ariane",
    "Page": "Page",
    "Discovered": "Découverte",
    "Testing": "Test en cours",
    "Tested": "Testé",
    "Unknown": "Inconnu",
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
