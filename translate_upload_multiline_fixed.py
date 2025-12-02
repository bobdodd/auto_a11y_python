#!/usr/bin/env python3
"""
Add French translations for remaining multiline strings in upload page
"""

MULTILINE_TRANSLATIONS = [
    {
        "english": '''msgid ""
"Numbered list of the most important accessibility issues found. Accepts "
"HTML or JSON format."
msgstr ""''',
        "french": '''msgid ""
"Numbered list of the most important accessibility issues found. Accepts "
"HTML or JSON format."
msgstr ""
"Liste numérotée des problèmes d'accessibilité les plus importants trouvés. "
"Accepte le format HTML ou JSON."'''
    },
    {
        "english": '''msgid ""
"User-focused description of difficulties experienced during testing. Accepts "
"HTML or JSON format."
msgstr ""''',
        "french": '''msgid ""
"User-focused description of difficulties experienced during testing. Accepts "
"HTML or JSON format."
msgstr ""
"Description centrée sur l'utilisateur des difficultés rencontrées pendant les "
"tests. Accepte le format HTML ou JSON."'''
    },
    {
        "english": '''msgid ""
"Direct quotes and observations from the tester with timecodes. Accepts "
"HTML or JSON format."
msgstr ""''',
        "french": '''msgid ""
"Direct quotes and observations from the tester with timecodes. Accepts "
"HTML or JSON format."
msgstr ""
"Citations directes et observations du testeur avec codes temporels. Accepte le "
"format HTML ou JSON."'''
    },
    {
        "english": '''msgid ""
"Optional: Select the test account used during this audit. Choose a project "
"first to see available test users."
msgstr ""''',
        "french": '''msgid ""
"Optional: Select the test account used during this audit. Choose a project "
"first to see available test users."
msgstr ""
"Facultatif : Sélectionnez le compte de test utilisé lors de cet audit. "
"Choisissez d'abord un projet pour voir les utilisateurs de test disponibles."'''
    },
    {
        "english": '''msgid ""
"Select the lived experience tester who performed this test. Choose a project "
"first to see available testers."
msgstr ""''',
        "french": '''msgid ""
"Select the lived experience tester who performed this test. Choose a project "
"first to see available testers."
msgstr ""
"Sélectionnez le testeur d'expérience vécue qui a effectué ce test. Choisissez "
"d'abord un projet pour voir les testeurs disponibles."'''
    },
    {
        "english": '''msgid ""
"Select the supervisor who oversaw this test. Choose a project first to see "
"available supervisors."
msgstr ""''',
        "french": '''msgid ""
"Select the supervisor who oversaw this test. Choose a project first to see "
"available supervisors."
msgstr ""
"Sélectionnez le superviseur qui a supervisé ce test. Choisissez d'abord un "
"projet pour voir les superviseurs disponibles."'''
    },
    {
        "english": '''msgid ""
"Optional: Select discovered pages related to this recording. Choose a "
"project first to see available pages."
msgstr ""''',
        "french": '''msgid ""
"Optional: Select discovered pages related to this recording. Choose a "
"project first to see available pages."
msgstr ""
"Facultatif : Sélectionnez les pages découvertes liées à cet enregistrement. "
"Choisissez d'abord un projet pour voir les pages disponibles."'''
    },
    {
        "english": '''msgid ""
"Optional: Describe the specific task being performed (e.g., \"Complete "
"checkout\", \"Navigate to settings\")."
msgstr ""''',
        "french": '''msgid ""
"Optional: Describe the specific task being performed (e.g., \"Complete "
"checkout\", \"Navigate to settings\")."
msgstr ""
"Facultatif : Décrivez la tâche spécifique effectuée (p. ex., « Terminer la "
"commande », « Naviguer vers les paramètres »)."'''
    },
    {
        "english": '''msgid ""
"Select the content types covered in this recording to determine applicable "
"WCAG criteria for compliance scoring."
msgstr ""''',
        "french": '''msgid ""
"Select the content types covered in this recording to determine applicable "
"WCAG criteria for compliance scoring."
msgstr ""
"Sélectionnez les types de contenu couverts dans cet enregistrement pour "
"déterminer les critères WCAG applicables pour le score de conformité."'''
    },
    {
        "english": '''msgid ""
"Dictaphone generates accessibility findings from audio/video recordings of "
"manual audits. The JSON format includes:"
msgstr ""''',
        "french": '''msgid ""
"Dictaphone generates accessibility findings from audio/video recordings of "
"manual audits. The JSON format includes:"
msgstr ""
"Dictaphone génère des constatations d'accessibilité à partir d'enregistrements "
"audio/vidéo d'audits manuels. Le format JSON comprend :"'''
    },
    {
        "english": '''msgid ""
"No test supervisors configured for this project. Add supervisors in project "
"settings."
msgstr ""''',
        "french": '''msgid ""
"No test supervisors configured for this project. Add supervisors in project "
"settings."
msgstr ""
"Aucun superviseur de test configuré pour ce projet. Ajoutez des superviseurs "
"dans les paramètres du projet."'''
    }
]

def update_po_file(po_path):
    """Update the .po file with multiline French translations"""
    with open(po_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translations_added = 0

    for item in MULTILINE_TRANSLATIONS:
        if item["english"] in content:
            content = content.replace(item["english"], item["french"])
            translations_added += 1
            first_line = item["english"].split('\n')[1].strip('"')
            print(f"✓ Added: {first_line[:60]}...")
        else:
            first_line = item["english"].split('\n')[1].strip('"')
            print(f"✗ Not found: {first_line[:60]}...")

    with open(po_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ Total: Added {translations_added} multiline translations")

if __name__ == '__main__':
    po_file = 'auto_a11y/web/translations/fr/LC_MESSAGES/messages.po'
    update_po_file(po_file)
