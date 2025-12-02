#!/usr/bin/env python3
"""
Add French translations for recordings/upload page
"""

TRANSLATIONS = {
    # Page header
    "Upload Recording": "Téléverser un enregistrement",
    "Upload Manual Audit Recording": "Téléverser un enregistrement d'audit manuel",
    "Upload a Dictaphone JSON file containing accessibility findings from manual audits or lived experience testing.":
        "Téléverser un fichier JSON Dictaphone contenant des constatations d'accessibilité provenant d'audits manuels ou de tests d'expérience vécue.",

    # JSON File section
    "Dictaphone JSON File": "Fichier JSON Dictaphone",
    "Select the JSON file exported from Dictaphone containing accessibility issues and timecodes.":
        "Sélectionner le fichier JSON exporté de Dictaphone contenant les problèmes d'accessibilité et les codes temporels.",

    # Recording Content section
    "Recording Content (Optional)": "Contenu de l'enregistrement (facultatif)",
    "Upload HTML or JSON files for key takeaways, user painpoints, and user assertions. Both formats are supported.":
        "Téléverser des fichiers HTML ou JSON pour les points clés, les difficultés des utilisateurs et les assertions des utilisateurs. Les deux formats sont supportés.",
    "Key Takeaways (HTML or JSON)": "Points clés (HTML ou JSON)",
    "Numbered list of the most important accessibility issues found. Accepts HTML or JSON format.":
        "Liste numérotée des problèmes d'accessibilité les plus importants trouvés. Accepte les formats HTML ou JSON.",
    "User Painpoints (HTML or JSON)": "Difficultés des utilisateurs (HTML ou JSON)",
    "User-focused description of difficulties experienced during testing. Accepts HTML or JSON format.":
        "Description axée sur l'utilisateur des difficultés rencontrées pendant les tests. Accepte les formats HTML ou JSON.",
    "User Assertions (HTML or JSON)": "Assertions des utilisateurs (HTML ou JSON)",
    "Direct quotes and observations from the tester with timecodes. Accepts HTML or JSON format.":
        "Citations directes et observations du testeur avec codes temporels. Accepte les formats HTML ou JSON.",

    # Project section
    "Project": "Projet",
    "Select a project...": "Sélectionner un projet...",
    "Which project should this recording be associated with?":
        "À quel projet cet enregistrement devrait-il être associé ?",

    # Test User section
    "Test User Account Used": "Compte utilisateur de test utilisé",
    "Select a test user...": "Sélectionner un utilisateur de test...",
    "Optional: Select the test account used during this audit. Choose a project first to see available test users.":
        "Facultatif : Sélectionner le compte de test utilisé pendant cet audit. Choisir d'abord un projet pour voir les utilisateurs de test disponibles.",

    # Lived Experience Tester section
    "Lived Experience Tester": "Testeur d'expérience vécue",
    "Select a tester...": "Sélectionner un testeur...",
    "Select the lived experience tester who performed this test. Choose a project first to see available testers.":
        "Sélectionner le testeur d'expérience vécue qui a effectué ce test. Choisir d'abord un projet pour voir les testeurs disponibles.",

    # Test Supervisor section
    "Test Supervisor": "Superviseur de test",
    "Select a supervisor...": "Sélectionner un superviseur...",
    "Select the supervisor who oversaw this test. Choose a project first to see available supervisors.":
        "Sélectionner le superviseur qui a supervisé ce test. Choisir d'abord un projet pour voir les superviseurs disponibles.",

    # Recording Metadata
    "Recording Title": "Titre de l'enregistrement",
    "e.g., Main Website Screen Reader Audit": "p. ex., Audit de lecteur d'écran du site Web principal",
    "Optional: A descriptive title for this recording.": "Facultatif : Un titre descriptif pour cet enregistrement.",
    "Description": "Description",
    "Brief description of what was tested and key findings...": "Brève description de ce qui a été testé et des constatations clés...",

    # Auditor Information
    "Auditor Name": "Nom de l'auditeur",
    "e.g., Jane Smith": "p. ex., Jane Dupont",
    "Auditor Role": "Rôle de l'auditeur",
    "e.g., Screen Reader User, Expert Auditor": "p. ex., Utilisateur de lecteur d'écran, Auditeur expert",

    # Recording Type
    "Recording Type": "Type d'enregistrement",
    "Audit": "Audit",
    "Lived Experience Website": "Expérience vécue - Site Web",
    "Lived Experience App": "Expérience vécue - Application",
    "Lived Experience Tangible Device": "Expérience vécue - Appareil tangible",
    "Lived Experience Nav and Wayfinding": "Expérience vécue - Navigation et orientation",

    # Page URLs
    "Page URLs Covered": "URLs de pages couvertes",
    "Optional: Enter one URL per line for specific pages discussed in this recording.":
        "Facultatif : Entrer une URL par ligne pour les pages spécifiques discutées dans cet enregistrement.",

    # Discovered Pages
    "Discovered Pages": "Pages découvertes",
    "Optional: Select discovered pages related to this recording. Choose a project first to see available pages.":
        "Facultatif : Sélectionner les pages découvertes liées à cet enregistrement. Choisir d'abord un projet pour voir les pages disponibles.",
    "Select a project to see discovered pages.": "Sélectionner un projet pour voir les pages découvertes.",
    "Loading discovered pages...": "Chargement des pages découvertes...",
    "No discovered pages found for this project.": "Aucune page découverte trouvée pour ce projet.",
    "Optional: No discovered pages available for this project.": "Facultatif : Aucune page découverte disponible pour ce projet.",
    "Error loading discovered pages.": "Erreur lors du chargement des pages découvertes.",

    # Common Components
    "Common Components": "Composants communs",
    "header": "en-tête",
    "navigation": "navigation",
    "footer": "pied de page",
    "search bar": "barre de recherche",
    "Optional: Enter one component name per line (e.g., header, nav, footer, modal, carousel).":
        "Facultatif : Entrer un nom de composant par ligne (p. ex., en-tête, nav, pied de page, modal, carrousel).",

    # App Screens
    "App Screens / Views": "Écrans / Vues d'application",
    "Login screen": "Écran de connexion",
    "Home dashboard": "Tableau de bord d'accueil",
    "Settings page": "Page de paramètres",
    "Optional: For app projects - enter one screen/view name per line.":
        "Facultatif : Pour les projets d'application - entrer un nom d'écran/vue par ligne.",

    # Device Sections
    "Device Sections": "Sections de l'appareil",
    "Main screen": "Écran principal",
    "Keypad": "Clavier",
    "Card reader": "Lecteur de carte",
    "Optional: For tangible devices - enter one section name per line.":
        "Facultatif : Pour les appareils tangibles - entrer un nom de section par ligne.",

    # Task Description
    "Task Description": "Description de la tâche",
    "Complete checkout process": "Compléter le processus de paiement",
    "Optional: Describe the specific task being performed (e.g., \"Complete checkout\", \"Navigate to settings\").":
        "Facultatif : Décrire la tâche spécifique effectuée (p. ex., \"Compléter le paiement\", \"Naviguer vers les paramètres\").",

    # Testing Scope
    "Testing Scope": "Portée des tests",
    "Select the content types covered in this recording to determine applicable WCAG criteria for compliance scoring.":
        "Sélectionner les types de contenu couverts dans cet enregistrement pour déterminer les critères WCAG applicables pour l'évaluation de la conformité.",
    "Forms": "Formulaires",
    "Video (prerecorded)": "Vidéo (préenregistrée)",
    "Live Multimedia": "Multimédia en direct",
    "Multilingual Content": "Contenu multilingue",
    "Orientation Changes": "Changements d'orientation",
    "Zoom / Text Resize": "Zoom / Redimensionnement du texte",
    "Timeouts / Re-authentication": "Délais d'expiration / Réauthentification",
    "Motion Actuation": "Activation par mouvement",
    "Drag and Drop": "Glisser-déposer",

    # Media File Path
    "Media File Path": "Chemin du fichier média",
    "/path/to/recording.mp4 or https://videos.example.com/audit.mp4":
        "/chemin/vers/enregistrement.mp4 ou https://videos.exemple.com/audit.mp4",
    "Optional: Path or URL to the actual video/audio recording file for reference.":
        "Facultatif : Chemin ou URL vers le fichier d'enregistrement vidéo/audio réel pour référence.",

    # Action Buttons
    "Upload Recording": "Téléverser l'enregistrement",
    "Cancel": "Annuler",

    # Sidebar - About Dictaphone Format
    "About Dictaphone Format": "À propos du format Dictaphone",
    "Dictaphone generates accessibility findings from audio/video recordings of manual audits. The JSON format includes:":
        "Dictaphone génère des constatations d'accessibilité à partir d'enregistrements audio/vidéo d'audits manuels. Le format JSON comprend :",
    "Recording ID:": "ID d'enregistrement :",
    "Unique identifier": "Identifiant unique",
    "Issues:": "Problèmes :",
    "List of accessibility problems found": "Liste des problèmes d'accessibilité trouvés",
    "Timecodes:": "Codes temporels :",
    "Start/end times in the recording": "Heures de début/fin dans l'enregistrement",
    "Impact Levels:": "Niveaux d'impact :",
    "High, Medium, Low": "Élevé, Moyen, Faible",
    "WCAG Criteria:": "Critères WCAG :",
    "Relevant guidelines": "Directives pertinentes",
    "Detailed Descriptions:": "Descriptions détaillées :",
    "What, why, who, and how to fix": "Quoi, pourquoi, qui et comment corriger",
    "Example JSON Structure": "Exemple de structure JSON",

    # JavaScript strings
    "No test users configured for this project.": "Aucun utilisateur de test configuré pour ce projet.",
    "Add test users": "Ajouter des utilisateurs de test",
    "Manage project users": "Gérer les utilisateurs du projet",
    "Optional: Select which test account was used during this audit.":
        "Facultatif : Sélectionner le compte de test qui a été utilisé pendant cet audit.",
    "Optional: Select the test account used during this audit.": "Facultatif : Sélectionner le compte de test utilisé pendant cet audit.",
    "No lived experience testers configured for this project. Add testers in project settings.":
        "Aucun testeur d'expérience vécue configuré pour ce projet. Ajouter des testeurs dans les paramètres du projet.",
    "Select the lived experience tester who performed this test.": "Sélectionner le testeur d'expérience vécue qui a effectué ce test.",
    "No test supervisors configured for this project. Add supervisors in project settings.":
        "Aucun superviseur de test configuré pour ce projet. Ajouter des superviseurs dans les paramètres du projet.",
    "Select the supervisor who oversaw this test.": "Sélectionner le superviseur qui a supervisé ce test.",
    "Error loading testers.": "Erreur lors du chargement des testeurs.",
    "Error loading supervisors.": "Erreur lors du chargement des superviseurs.",
}

def update_po_file(po_path):
    """Update the .po file with French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translations_added = 0

    for english, french in TRANSLATIONS.items():
        english_escaped = english.replace('"', '\\"').replace('\n', '\\n')
        french_escaped = french.replace('"', '\\"').replace('\n', '\\n')

        # First try to match with empty msgstr
        pattern = f'msgid "{english_escaped}"\nmsgstr ""'
        replacement = f'msgid "{english_escaped}"\nmsgstr "{french_escaped}"'

        if pattern in content:
            content = content.replace(pattern, replacement)
            translations_added += 1
            print(f"✓ Added: {english[:80]}...")
        else:
            # Try without escaping for simple strings
            pattern2 = f'msgid "{english}"\nmsgstr ""'
            replacement2 = f'msgid "{english}"\nmsgstr "{french}"'
            if pattern2 in content:
                content = content.replace(pattern2, replacement2)
                translations_added += 1
                print(f"✓ Added: {english[:80]}...")
            else:
                # Try to update existing translation (with any msgstr value)
                import re
                pattern3 = f'msgid "{re.escape(english)}"\nmsgstr "[^"]*"'
                replacement3 = f'msgid "{english}"\nmsgstr "{french}"'
                if re.search(pattern3, content):
                    content = re.sub(pattern3, replacement3, content)
                    translations_added += 1
                    print(f"✓ Updated: {english[:80]}...")
                else:
                    print(f"✗ Not found: {english[:80]}...")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Total: Added {translations_added} translations")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
