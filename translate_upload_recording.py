#!/usr/bin/env python3
"""
Add French translations for recordings upload page
"""

TRANSLATIONS = {
    # Page title and heading
    "Upload Recording - Auto A11y": "Télécharger un enregistrement - Auto A11y",
    "Upload Manual Audit Recording": "Télécharger un enregistrement d'audit manuel",
    "Upload a Dictaphone JSON file containing accessibility findings from manual audits or lived experience testing.": "Télécharger un fichier JSON Dictaphone contenant les constatations d'accessibilité provenant d'audits manuels ou de tests d'expérience vécue.",

    # Form labels
    "Dictaphone JSON File *": "Fichier JSON Dictaphone *",
    "Recording Content (Optional)": "Contenu de l'enregistrement (facultatif)",
    "Key Takeaways (HTML or JSON)": "Points clés (HTML ou JSON)",
    "User Painpoints (HTML or JSON)": "Points douloureux de l'utilisateur (HTML ou JSON)",
    "User Assertions (HTML or JSON)": "Affirmations de l'utilisateur (HTML ou JSON)",
    "Project *": "Projet *",
    "Test User Account Used": "Compte utilisateur de test utilisé",
    "Lived Experience Tester": "Testeur d'expérience vécue",
    "Test Supervisor": "Superviseur de test",
    "Recording Title": "Titre de l'enregistrement",
    "Description": "Description",
    "Auditor Name": "Nom de l'auditeur",
    "Auditor Role": "Rôle de l'auditeur",
    "Recording Type": "Type d'enregistrement",
    "Page URLs Covered": "URLs des pages couvertes",
    "Discovered Pages": "Pages découvertes",
    "Common Components": "Composants communs",
    "App Screens / Views": "Écrans / Vues de l'application",
    "Device Sections": "Sections de l'appareil",
    "Task Description": "Description de la tâche",
    "Testing Scope": "Portée des tests",
    "Media File Path": "Chemin du fichier média",

    # Help text
    "Select the JSON file exported from Dictaphone containing accessibility issues and timecodes.": "Sélectionnez le fichier JSON exporté de Dictaphone contenant les problèmes d'accessibilité et les codes temporels.",
    "Upload HTML or JSON files for key takeaways, user painpoints, and user assertions. Both formats are supported.": "Téléchargez des fichiers HTML ou JSON pour les points clés, les points douloureux de l'utilisateur et les affirmations de l'utilisateur. Les deux formats sont pris en charge.",
    "Numbered list of the most important accessibility issues found. Accepts HTML or JSON format.": "Liste numérotée des problèmes d'accessibilité les plus importants trouvés. Accepte le format HTML ou JSON.",
    "User-focused description of difficulties experienced during testing. Accepts HTML or JSON format.": "Description centrée sur l'utilisateur des difficultés rencontrées pendant les tests. Accepte le format HTML ou JSON.",
    "Direct quotes and observations from the tester with timecodes. Accepts HTML or JSON format.": "Citations directes et observations du testeur avec codes temporels. Accepte le format HTML ou JSON.",
    "Which project should this recording be associated with?": "À quel projet cet enregistrement devrait-il être associé?",
    "Optional: Select the test account used during this audit. Choose a project first to see available test users.": "Facultatif : Sélectionnez le compte de test utilisé lors de cet audit. Choisissez d'abord un projet pour voir les utilisateurs de test disponibles.",
    "Select the lived experience tester who performed this test. Choose a project first to see available testers.": "Sélectionnez le testeur d'expérience vécue qui a effectué ce test. Choisissez d'abord un projet pour voir les testeurs disponibles.",
    "Select the supervisor who oversaw this test. Choose a project first to see available supervisors.": "Sélectionnez le superviseur qui a supervisé ce test. Choisissez d'abord un projet pour voir les superviseurs disponibles.",
    "Optional: A descriptive title for this recording.": "Facultatif : Un titre descriptif pour cet enregistrement.",
    "Optional: Enter one URL per line for specific pages discussed in this recording.": "Facultatif : Entrez une URL par ligne pour les pages spécifiques discutées dans cet enregistrement.",
    "Optional: Select discovered pages related to this recording. Choose a project first to see available pages.": "Facultatif : Sélectionnez les pages découvertes liées à cet enregistrement. Choisissez d'abord un projet pour voir les pages disponibles.",
    "Optional: Enter one component name per line (e.g., header, nav, footer, modal, carousel).": "Facultatif : Entrez un nom de composant par ligne (p. ex., en-tête, nav, pied de page, modal, carrousel).",
    "Optional: For app projects - enter one screen/view name per line.": "Facultatif : Pour les projets d'application - entrez un nom d'écran/vue par ligne.",
    "Optional: For tangible devices - enter one section name per line.": "Facultatif : Pour les appareils tangibles - entrez un nom de section par ligne.",
    "Optional: Describe the specific task being performed (e.g., \"Complete checkout\", \"Navigate to settings\").": "Facultatif : Décrivez la tâche spécifique effectuée (p. ex., « Terminer la commande », « Naviguer vers les paramètres »).",
    "Select the content types covered in this recording to determine applicable WCAG criteria for compliance scoring.": "Sélectionnez les types de contenu couverts dans cet enregistrement pour déterminer les critères WCAG applicables pour le score de conformité.",
    "Optional: Path or URL to the actual video/audio recording file for reference.": "Facultatif : Chemin ou URL vers le fichier d'enregistrement vidéo/audio réel pour référence.",

    # Placeholder text
    "e.g., Main Website Screen Reader Audit": "p. ex., Audit du lecteur d'écran du site Web principal",
    "Brief description of what was tested and key findings...": "Brève description de ce qui a été testé et des principales constatations...",
    "e.g., Jane Smith": "p. ex., Jane Dupont",
    "e.g., Screen Reader User, Expert Auditor": "p. ex., Utilisateur de lecteur d'écran, Auditeur expert",
    "Complete checkout process": "Terminer le processus de commande",
    "/path/to/recording.mp4 or https://videos.example.com/audit.mp4": "/chemin/vers/enregistrement.mp4 ou https://videos.example.com/audit.mp4",

    # Dropdown options
    "Select a project...": "Sélectionnez un projet...",
    "Select a test user...": "Sélectionnez un utilisateur de test...",
    "Select a tester...": "Sélectionnez un testeur...",
    "Select a supervisor...": "Sélectionnez un superviseur...",
    "Audit": "Audit",
    "Lived Experience Website": "Site Web d'expérience vécue",
    "Lived Experience App": "Application d'expérience vécue",
    "Lived Experience Tangible Device": "Appareil tangible d'expérience vécue",
    "Lived Experience Nav and Wayfinding": "Navigation et orientation d'expérience vécue",

    # Testing scope checkboxes
    "Forms": "Formulaires",
    "Video (prerecorded)": "Vidéo (préenregistrée)",
    "Live Multimedia": "Multimédia en direct",
    "Multilingual Content": "Contenu multilingue",
    "Orientation Changes": "Changements d'orientation",
    "Zoom / Text Resize": "Zoom / Redimensionnement du texte",
    "Timeouts / Re-authentication": "Délais d'expiration / Réauthentification",
    "Motion Actuation": "Actionnement par mouvement",
    "Drag and Drop": "Glisser-déposer",

    # Buttons
    "Upload Recording": "Télécharger l'enregistrement",
    "Cancel": "Annuler",

    # Sidebar - About Dictaphone Format
    "About Dictaphone Format": "À propos du format Dictaphone",
    "Dictaphone generates accessibility findings from audio/video recordings of manual audits. The JSON format includes:": "Dictaphone génère des constatations d'accessibilité à partir d'enregistrements audio/vidéo d'audits manuels. Le format JSON comprend :",
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
    "What, why, who, and how to fix": "Quoi, pourquoi, qui et comment réparer",
    "Example JSON Structure": "Exemple de structure JSON",

    # JavaScript dynamic messages
    "Select a project to see discovered pages.": "Sélectionnez un projet pour voir les pages découvertes.",
    "Loading discovered pages...": "Chargement des pages découvertes...",
    "No discovered pages found for this project.": "Aucune page découverte trouvée pour ce projet.",
    "Optional: No discovered pages available for this project.": "Facultatif : Aucune page découverte disponible pour ce projet.",
    "Error loading discovered pages.": "Erreur lors du chargement des pages découvertes.",
    "Optional: Select which test account was used during this audit.": "Facultatif : Sélectionnez quel compte de test a été utilisé lors de cet audit.",
    "Manage project users": "Gérer les utilisateurs du projet",
    "No test users configured for this project.": "Aucun utilisateur de test configuré pour ce projet.",
    "Add test users": "Ajouter des utilisateurs de test",
    "No lived experience testers configured for this project. Add testers in project settings.": "Aucun testeur d'expérience vécue configuré pour ce projet. Ajoutez des testeurs dans les paramètres du projet.",
    "No test supervisors configured for this project. Add supervisors in project settings.": "Aucun superviseur de test configuré pour ce projet. Ajoutez des superviseurs dans les paramètres du projet.",
    "Error loading testers.": "Erreur lors du chargement des testeurs.",
    "Error loading supervisors.": "Erreur lors du chargement des superviseurs.",
}

def update_po_file(po_path):
    """Update the .po file with French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translations_added = 0

    for english, french in TRANSLATIONS.items():
        # First try to match with empty msgstr
        pattern = f'msgid "{english}"\nmsgstr ""'
        replacement = f'msgid "{english}"\nmsgstr "{french}"'

        if pattern in content:
            content = content.replace(pattern, replacement)
            translations_added += 1
            print(f"✓ Added: {english}")
        else:
            # Try to update existing translation
            import re
            pattern_existing = f'msgid "{re.escape(english)}"\nmsgstr "[^"]*"'
            replacement_existing = f'msgid "{english}"\nmsgstr "{french}"'
            if re.search(pattern_existing, content):
                content = re.sub(pattern_existing, replacement_existing, content)
                translations_added += 1
                print(f"✓ Updated: {english}")
            else:
                print(f"✗ Not found: {english}")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Total: Added/Updated {translations_added} translations")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
