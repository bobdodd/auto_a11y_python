#!/usr/bin/env python3
"""
Script to add French translations for user management templates
"""

# French translations for user management templates
TRANSLATIONS = {
    # User management general
    "Project-Level Test Users:": "Utilisateurs de test au niveau du projet :",
    "Manage lived experience testers and test supervisors for %s": "Gérer les testeurs d'expérience vécue et superviseurs de test pour %s",
    "User Roles in Use": "Rôles d'utilisateur utilisés",

    # User form fields
    "Friendly name for this test user (optional)": "Nom convivial pour cet utilisateur de test (optionnel)",
    "Username for login (stored securely)": "Nom d'utilisateur pour la connexion (stocké en toute sécurité)",
    "Password for login (stored securely)": "Mot de passe pour la connexion (stocké en toute sécurité)",
    "Comma-separated list of user roles for testing role-based content": "Liste de rôles d'utilisateur séparés par des virgules pour tester le contenu basé sur les rôles",
    "Roles help you test content that varies based on user permissions.": "Les rôles vous aident à tester le contenu qui varie en fonction des autorisations utilisateur.",
    "- User is active and can be used for testing": "- L'utilisateur est actif et peut être utilisé pour les tests",
    "User is active and can be used for testing": "L'utilisateur est actif et peut être utilisé pour les tests",
    "Leave blank to keep current password": "Laisser vide pour conserver le mot de passe actuel",
    "Leave the password field blank to keep the current password unchanged.": "Laissez le champ mot de passe vide pour conserver le mot de passe actuel inchangé.",
    "Only enter a password if you want to change it": "Entrez un mot de passe uniquement si vous souhaitez le modifier",

    # Authentication
    "Auth Method": "Méthode d'auth.",
    "Auth Method:": "Méthode d'authentification :",
    "Authentication Method": "Méthode d'authentification",
    "Login URL:": "URL de connexion :",
    "Full URL of the login page": "URL complète de la page de connexion",
    "Username Field Selector": "Sélecteur du champ nom d'utilisateur",
    "CSS selector for username input": "Sélecteur CSS pour l'entrée du nom d'utilisateur",
    "CSS selector for password input": "Sélecteur CSS pour l'entrée du mot de passe",
    "CSS selector for login button": "Sélecteur CSS pour le bouton de connexion",
    "Success Indicator:": "Indicateur de succès :",
    "CSS selector that appears after successful login": "Sélecteur CSS qui apparaît après une connexion réussie",
    "Logout URL": "URL de déconnexion",
    "URL to visit for logout (optional if using button)": "URL à visiter pour la déconnexion (optionnel si utilisation d'un bouton)",
    "Logout Success Indicator Selector": "Sélecteur d'indicateur de succès de déconnexion",
    "CSS selector for logout button/link (optional)": "Sélecteur CSS pour le bouton/lien de déconnexion (optionnel)",
    "%s minutes": "%s minutes",
    "How long the session stays valid": "Durée de validité de la session",

    # Login status
    "Login Successful": "Connexion réussie",
    "User authenticated successfully": "Utilisateur authentifié avec succès",
    "Success": "Succès",
    "Not attempted yet": "Pas encore tenté",
    "Not used yet": "Pas encore utilisé",

    # CSS Selectors help
    "Use browser DevTools to find selectors:": "Utiliser les DevTools du navigateur pour trouver les sélecteurs :",
    "Right-click in the HTML panel": "Clic droit dans le panneau HTML",
    "By ID:": "Par ID :",
    "By class:": "Par classe :",

    # Role examples
    "e.g., student, premium, member": "par ex., étudiant, premium, membre",
    "e.g., Student User, John Doe": "par ex., Utilisateur étudiant, John Doe",
    "e.g., student123": "par ex., étudiant123",

    # Participants - Testers
    "Full name of the lived experience tester": "Nom complet du testeur d'expérience vécue",
    "e.g., Jane Smith": "par ex., Jane Dupont",
    "Contact email for the tester (optional)": "Email de contact du testeur (optionnel)",
    "e.g., jane.smith@example.com": "par ex., jane.dupont@exemple.fr",
    "Assistive Technologies": "Technologies d'assistance",
    "Comma-separated list of assistive technologies used": "Liste des technologies d'assistance utilisées, séparées par des virgules",
    "e.g., JAWS, ZoomText, Dragon NaturallySpeaking": "par ex., JAWS, ZoomText, Dragon NaturallySpeaking",
    "Optional notes (e.g., availability, special requirements)": "Notes optionnelles (par ex., disponibilité, exigences particulières)",
    "Additional information about this tester...": "Informations supplémentaires sur ce testeur...",

    # Disability types
    "Common Disability Types": "Types de handicap courants",
    "e.g., Blind, Low Vision, Deaf, Motor Disability": "par ex., Aveugle, Malvoyant, Sourd, Handicap moteur",
    "Blind": "Aveugle",
    "Low Vision": "Malvoyant",
    "Deaf": "Sourd",
    "Hard of Hearing": "Malentendant",
    "Deaf / Hard of Hearing": "Sourd / Malentendant",
    "Motor Disability": "Handicap moteur",
    "Cognitive Disability": "Handicap cognitif",
    "Multiple Disabilities": "Handicaps multiples",

    # Assistive technologies
    "Common Assistive Technologies": "Technologies d'assistance courantes",
    "Voice Control:": "Contrôle vocal :",
    "Alternative Input:": "Saisie alternative :",
    "built-in magnifiers": "loupes intégrées",

    # Participants - Supervisors
    "e.g., Dr. Sarah Johnson": "par ex., Dr. Sarah Dubois",
    "Contact email for the supervisor (optional)": "Email de contact du superviseur (optionnel)",
    "e.g., sarah.johnson@example.com": "par ex., sarah.dubois@exemple.fr",
    "Job title or role (optional)": "Titre du poste ou rôle (optionnel)",
    "e.g., Accessibility Specialist, Research Lead": "par ex., Spécialiste en accessibilité, Responsable de recherche",
    "Organization or company name (optional)": "Nom de l'organisation ou de l'entreprise (optionnel)",
    "Optional notes (e.g., areas of expertise, contact preferences)": "Notes optionnelles (par ex., domaines d'expertise, préférences de contact)",
    "Additional information about this supervisor...": "Informations supplémentaires sur ce superviseur...",

    # Supervisor roles
    "Research Lead": "Responsable de recherche",
    "UX Researcher": "Chercheur UX",
    "Quality Assurance Lead": "Responsable assurance qualité",
    "Teacher/instructor": "Enseignant/instructeur",
    "Free tier user": "Utilisateur niveau gratuit",
    "Paid member": "Membre payant",

    # Supervisor responsibilities
    "Supervisor Responsibilities": "Responsabilités du superviseur",
    "Coordinate testing sessions": "Coordonner les sessions de test",
    "Ensure ethical testing practices": "Garantir des pratiques de test éthiques",
    "Provide technical support": "Fournir un support technique",
    "Document findings": "Documenter les résultats",
    "Communicate with stakeholders": "Communiquer avec les parties prenantes",

    # Already translated but appearing in new contexts
    "An error occurred while loading the test details. Please try again.": "Une erreur s'est produite lors du chargement des détails du test. Veuillez réessayer.",
    "Clear cookies and storage before testing to ensure a clean starting state": "Effacer les cookies et le stockage avant les tests pour garantir un état de départ propre",
    "Define the actions to perform. Steps execute in order from top to bottom.": "Définir les actions à effectuer. Les étapes s'exécutent dans l'ordre de haut en bas.",
    "DOM Content Loaded (Fast, for sites with heavy background activity)": "Contenu DOM chargé (rapide, pour les sites avec beaucoup d'activité en arrière-plan)",
    "Enhanced compliance (7:1 contrast for normal text, 4.5:1 for large text)": "Conformité renforcée (contraste 7:1 pour le texte normal, 4.5:1 pour le texte large)",
    "Enter font names, one per line (e.g., 'Custom Font Name')": "Entrez les noms de police, un par ligne (par ex., 'Nom de police personnalisée')",
    "No test users configured. Discovery will run as guest.": "Aucun utilisateur de test configuré. La découverte s'exécutera en tant qu'invité.",
    "No test users configured. Testing will run as guest.": "Aucun utilisateur de test configuré. Les tests s'exécuteront en tant qu'invité.",
    "No violations found! The page passes all automated accessibility checks.": "Aucune violation trouvée ! La page réussit tous les tests d'accessibilité automatisés.",
    "No websites added yet. Add a website to start testing.": "Aucun site web ajouté pour le moment. Ajoutez un site web pour commencer les tests.",
    "Please add at least one step to the script.": "Veuillez ajouter au moins une étape au script.",
    "Please select at least one test user (or Guest) to continue.": "Veuillez sélectionner au moins un utilisateur de test (ou Invité) pour continuer.",
    "Please select at least one user for discovery (or Guest).": "Veuillez sélectionner au moins un utilisateur pour la découverte (ou Invité).",
    "Real browser testing with Puppeteer ensures accurate DOM-based results": "Les tests avec un navigateur réel via Puppeteer garantissent des résultats précis basés sur le DOM",
    "Recommended for cookie banner testing - ensures banner appears": "Recommandé pour les tests de bannière de cookies - garantit l'apparition de la bannière",
    "Run browser invisibly (faster, less resource intensive)": "Exécuter le navigateur de manière invisible (plus rapide, moins de ressources)",
    "Standard compliance (4.5:1 contrast for normal text, 3:1 for large text)": "Conformité standard (contraste 4.5:1 pour le texte normal, 3:1 pour le texte large)",
    "The accessibility test is running. The page will refresh when complete.": "Le test d'accessibilité est en cours. La page se rafraîchira une fois terminé.",
    "The compliance score is calculated based on WCAG 2.2 Level AA criteria": "Le score de conformité est calculé sur la base des critères WCAG 2.2 niveau AA",
    "This will also delete all test results for this page.": "Cela supprimera également tous les résultats de test pour cette page.",
    "Usually checked - test the page in its final state after setup": "Généralement coché - tester la page dans son état final après la configuration",
    "Verifies logical reading sequence matches visual layout": "Vérifie que la séquence de lecture logique correspond à la disposition visuelle",
    "Wait until network has ≤2 connections (best for dynamic sites)": "Attendre jusqu'à ce que le réseau ait ≤2 connexions (idéal pour les sites dynamiques)",
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
