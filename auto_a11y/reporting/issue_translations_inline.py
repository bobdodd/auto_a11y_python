"""
Inline French translations for issue descriptions.
These translations are used when pybabel translations are missing or fail.
"""

ISSUE_DESCRIPTION_TRANSLATIONS_FR = {
    # Landmarks - Discovery
    "A banner landmark has been detected on this page": "Un repère de bannière a été détecté sur cette page",
    "A complementary region has been detected on this page": "Une région complémentaire a été détectée sur cette page",
    "A contentinfo landmark has been detected on this page": "Un repère contentinfo a été détecté sur cette page",
    "A form has been detected on this page": "Un formulaire a été détecté sur cette page",
    "A navigation region has been detected on this page": "Une région de navigation a été détectée sur cette page",
    "A search landmark has been detected on this page": "Un repère de recherche a été détecté sur cette page",
    "A section region has been detected on this page": "Une région de section a été détectée sur cette page",
    
    # ARIA
    "ARIA attribute references non-existent element ID": "L'attribut ARIA référence un ID d'élément inexistant",
    "Custom control is missing ARIA attributes": "Le contrôle personnalisé n'a pas d'attributs ARIA",
    "Interactive element lacks appropriate ARIA role": "L'élément interactif n'a pas de rôle ARIA approprié",
    
    # Accessibility general
    "Accessibility issue detected": "Problème d'accessibilité détecté",
    "Interactive element has accessibility issues": "L'élément interactif a des problèmes d'accessibilité",
    
    # Animation
    "Animation duration exceeds recommended time limit": "La durée de l'animation dépasse la limite de temps recommandée",
    "Animation runs infinitely without pause controls": "L'animation s'exécute indéfiniment sans contrôles de pause",
    "Animations do not respect prefers-reduced-motion setting": "Les animations ne respectent pas le paramètre prefers-reduced-motion",
    "Auto-playing media cannot be controlled": "Le média en lecture automatique ne peut pas être contrôlé",
    "Infinite animation cannot be paused": "L'animation infinie ne peut pas être mise en pause",
    "Loading spinner animation runs infinitely without controls": "L'animation du spinner de chargement s'exécute indéfiniment sans contrôles",
    "Potential flashing content detected": "Contenu clignotant potentiel détecté",
    
    # Modals/Dialogs
    "Background content behind modal is not properly inert": "Le contenu en arrière-plan derrière la modale n'est pas correctement inerte",
    "Dialog is missing an accessible name": "Le dialogue n'a pas de nom accessible",
    "Element appears to be a dialog or modal but lacks proper ARIA markup": "L'élément semble être un dialogue ou une modale mais n'a pas de balisage ARIA approprié",
    "Modal dialog is missing dialog role": "Le dialogue modal n'a pas de rôle dialog",
    "Modal has incorrect heading level for proper document structure": "La modale a un niveau de titre incorrect pour la structure du document",
    "Modal has no visible way to close it": "La modale n'a pas de moyen visible de la fermer",
    "Modal or dialog does not properly trap focus": "La modale ou le dialogue ne capture pas correctement le focus",
    "Modal or dialog has no heading to identify its purpose": "La modale ou le dialogue n'a pas de titre pour identifier son objectif",
    "La modale ne peut pas être fermée avec la touche Échap": "La modale ne peut pas être fermée avec la touche Échap",
    
    # Carousels/Sliders
    "Carousel or slider lacks proper ARIA markup and controls": "Le carrousel ou le curseur ne dispose pas du balisage ARIA et des contrôles appropriés",
    "Dropdown menu lacks proper ARIA markup": "Le menu déroulant n'a pas de balisage ARIA approprié",
    "Tab interface lacks proper ARIA markup": "L'interface à onglets n'a pas de balisage ARIA approprié",
    
    # Clickable/Interactive elements
    "Element has a mouse event handler but lacks tabindex, making it inaccessible to keyboard users": "L'élément a un gestionnaire d'événement souris mais n'a pas de tabindex, le rendant inaccessible aux utilisateurs de clavier",
    "Element has a title attribute that duplicates or overlaps with visible text content": "L'élément a un attribut title qui duplique ou chevauche le contenu textuel visible",
    "Non-semantic element used as a button": "Élément non sémantique utilisé comme bouton",
    "Non-semantic element used as a link": "Élément non sémantique utilisé comme lien",
    
    # Language
    "Element has invalid language code that is not a valid ISO 639 language code": "L'élément a un code de langue invalide qui n'est pas un code de langue ISO 639 valide",
    "Foreign language text is not marked with lang attribute": "Le texte en langue étrangère n'est pas marqué avec l'attribut lang",
    "Page language is not declared": "La langue de la page n'est pas déclarée",
    
    # Forms
    "Field is labeled using aria-label, which is valid but may have usability considerations": "Le champ est étiqueté avec aria-label, ce qui est valide mais peut avoir des considérations d'utilisabilité",
    "Single label contains multiple form fields": "Une seule étiquette contient plusieurs champs de formulaire",
    "Form field has no associated label": "Le champ de formulaire n'a pas d'étiquette associée",
    "Form input missing label": "Champ de formulaire sans étiquette",
    
    # Focus
    "Focus indicator is hard to see or missing": "L'indicateur de focus est difficile à voir ou manquant",
    "Non-interactive element with tabindex lacks visible focus indicator - review the purpose of tabindex on this element": "L'élément non interactif avec tabindex n'a pas d'indicateur de focus visible - vérifiez l'objectif du tabindex sur cet élément",
    "Non-modal floating element obscures interactive content that users may try to access": "Un élément flottant non modal masque du contenu interactif auquel les utilisateurs pourraient vouloir accéder",
    
    # Fonts
    "Font being used is known to be difficult to read": "La police utilisée est connue pour être difficile à lire",
    "Font is not included in the recommended list of accessibility-friendly fonts": "La police n'est pas incluse dans la liste recommandée des polices accessibles",
    "Font is used at multiple sizes on this page": "La police est utilisée à plusieurs tailles sur cette page",
    "Text size is below the recommended minimum of 16px for comfortable reading": "La taille du texte est inférieure au minimum recommandé de 16px pour une lecture confortable",
    "Line height ratio is below the recommended minimum for readability": "Le ratio de hauteur de ligne est inférieur au minimum recommandé pour la lisibilité",
    
    # Headings
    "Heading element contains only whitespace or special characters": "L'élément de titre ne contient que des espaces ou des caractères spéciaux",
    "Heading is approaching the recommended character limit": "Le titre approche de la limite de caractères recommandée",
    "Heading levels are not in sequential order": "Les niveaux de titre ne sont pas dans un ordre séquentiel",
    "Heading levels are skipped in the document hierarchy": "Des niveaux de titre sont ignorés dans la hiérarchie du document",
    "Heading structure has accessibility issues": "La structure des titres a des problèmes d'accessibilité",
    "Heading text exceeds the recommended character limit": "Le texte du titre dépasse la limite de caractères recommandée",
    "Page heading structure does not start with h1": "La structure des titres de la page ne commence pas par h1",
    "Page heading structure skips intermediate levels, breaking document hierarchy": "La structure des titres de la page ignore des niveaux intermédiaires, brisant la hiérarchie du document",
    "Text appears visually as a heading but is not marked up with proper heading tags": "Le texte apparaît visuellement comme un titre mais n'est pas balisé avec des balises de titre appropriées",
    "Visual heading sizes are inconsistent with their importance": "Les tailles visuelles des titres sont incohérentes avec leur importance",
    
    # Lists
    "Element contains list-like items but does not use proper list markup": "L'élément contient des éléments de type liste mais n'utilise pas de balisage de liste approprié",
    "List item uses custom styling for bullets instead of standard list-style-type": "L'élément de liste utilise un style personnalisé pour les puces au lieu du list-style-type standard",
    "List item uses icon font elements instead of CSS list-style-type property": "L'élément de liste utilise des éléments de police d'icônes au lieu de la propriété CSS list-style-type",
    
    # Multiple landmarks
    "Multiple landmarks of the same type exist, but this instance lacks a unique accessible name to distinguish it from the others": "Plusieurs repères du même type existent, mais cette instance n'a pas de nom accessible unique pour la distinguer des autres",
    "Page contains multiple banner landmarks, but should have at most one": "La page contient plusieurs repères de bannière, mais devrait en avoir au plus un",
    "Page contains multiple contentinfo landmarks, but should have at most one": "La page contient plusieurs repères contentinfo, mais devrait en avoir au plus un",
    "Page contains multiple h1 elements instead of just one": "La page contient plusieurs éléments h1 au lieu d'un seul",
    "Page contains multiple h1 elements, but best practice is to have exactly one h1 per page": "La page contient plusieurs éléments h1, mais la meilleure pratique est d'avoir exactement un h1 par page",
    "Page contains multiple main landmarks, but should have exactly one": "La page contient plusieurs repères principaux, mais devrait en avoir exactement un",
    
    # Page title
    "Multiple title elements found in the document head": "Plusieurs éléments title trouvés dans le head du document",
    "Multiple title elements found in the document head, which may cause unpredictable behavior": "Plusieurs éléments title trouvés dans le head du document, ce qui peut causer un comportement imprévisible",
    "Page title exceeds the recommended character limit": "Le titre de la page dépasse la limite de caractères recommandée",
    "Page title is potentially not descriptive enough": "Le titre de la page n'est potentiellement pas assez descriptif",
    
    # Responsive
    "Page defines responsive breakpoints in CSS media queries": "La page définit des points de rupture réactifs dans les requêtes média CSS",
    
    # Contrast
    "Large text fails WCAG AA contrast requirements": "Le texte large ne respecte pas les exigences de contraste WCAG AA",
    "Large text fails WCAG AAA contrast requirements": "Le texte large ne respecte pas les exigences de contraste WCAG AAA",
    "Normal text fails WCAG AA contrast requirements": "Le texte normal ne respecte pas les exigences de contraste WCAG AA",
    "Normal text fails WCAG AAA contrast requirements": "Le texte normal ne respecte pas les exigences de contraste WCAG AAA",
    "Text contrast requires manual verification": "Le contraste du texte nécessite une vérification manuelle",
    "Text fails contrast and overflows container boundaries": "Le texte ne respecte pas le contraste et déborde des limites du conteneur",
    "Text fails enhanced contrast and overflows container boundaries": "Le texte ne respecte pas le contraste amélioré et déborde des limites du conteneur",
    
    # Images
    "Image has no alt attribute": "L'image n'a pas d'attribut alt",
    "Image alt text is empty": "Le texte alternatif de l'image est vide",
    "Image alt contains filename": "Le texte alternatif de l'image contient un nom de fichier",
    
    # Buttons
    "Button has no accessible name": "Le bouton n'a pas de nom accessible",
    "Button uses browser default focus outline which may not meet contrast requirements on all backgrounds": "Le bouton utilise le contour de focus par défaut du navigateur qui peut ne pas respecter les exigences de contraste sur tous les arrière-plans",
    "Button relies on browser default focus outline": "Le bouton s'appuie sur le contour de focus par défaut du navigateur",
    
    # Interactive elements
    "Interactive element has no accessible name": "L'élément interactif n'a pas de nom accessible",
    "L'élément interactif n'a pas de nom accessible": "L'élément interactif n'a pas de nom accessible",
    
    # Tables
    "Table has no headers": "Le tableau n'a pas d'en-têtes",
    "Table header cells not properly associated with data cells": "Les cellules d'en-tête du tableau ne sont pas correctement associées aux cellules de données",
    
    # Page
    "Page has no main landmark": "La page n'a pas de repère principal",
    "Page language not specified": "La langue de la page n'est pas spécifiée",
    "Page title is missing": "Le titre de la page est manquant",
    
    # Keyboard
    "Element is not keyboard accessible": "L'élément n'est pas accessible au clavier",
    "Focus order is not logical": "L'ordre de focus n'est pas logique",
    "Keyboard trap detected": "Piège clavier détecté",
    
    # Color
    "Color alone used to convey information": "La couleur seule est utilisée pour transmettre des informations",
    
    # Landmarks
    "Multiple main landmarks": "Plusieurs repères principaux",
    "Banner landmark not at top level": "Le repère de bannière n'est pas au niveau supérieur",
    
    # Lists
    "List items not properly contained in list element": "Les éléments de liste ne sont pas correctement contenus dans un élément de liste",
    
    # Media
    "Video has no captions": "La vidéo n'a pas de sous-titres",
    "Audio has no transcript": "L'audio n'a pas de transcription",
    
    # Links
    "Link uses browser default focus styles which vary across browsers and may fail contrast requirements": "Le lien utilise les styles de focus par défaut du navigateur qui varient selon les navigateurs et peuvent ne pas respecter les exigences de contraste",
    
    # Color scheme
    "Site does not support prefers-color-scheme": "Le site ne prend pas en charge prefers-color-scheme",
    
    # Grouping
    "Related form fields not grouped with fieldset": "Les champs de formulaire liés ne sont pas regroupés avec fieldset",
    "Radio/checkbox group lacks fieldset and legend": "Le groupe de boutons radio/cases à cocher n'a pas de fieldset et legend",
}
