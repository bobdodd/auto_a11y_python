"""
Touchpoint test modules for comprehensive accessibility testing
"""

from .test_headings import test_headings, TEST_DOCUMENTATION as HEADINGS_DOCS
from .test_images import test_images, TEST_DOCUMENTATION as IMAGES_DOCS
from .test_forms import test_forms, TEST_DOCUMENTATION as FORMS_DOCS
from .test_accessible_names import test_accessible_names, TEST_DOCUMENTATION as ACCESSIBLE_NAMES_DOCS
from .test_aria import test_aria, TEST_DOCUMENTATION as ARIA_DOCS
from .test_animations import test_animations, TEST_DOCUMENTATION as ANIMATIONS_DOCS
from .test_buttons import test_buttons, TEST_DOCUMENTATION as BUTTONS_DOCS
from .test_links import test_links, TEST_DOCUMENTATION as LINKS_DOCS
from .test_colors import test_colors, TEST_DOCUMENTATION as COLORS_DOCS
from .test_text_contrast import test_text_contrast, TEST_DOCUMENTATION as TEXT_CONTRAST_DOCS
from .test_document_links import test_document_links, TEST_DOCUMENTATION as DOCUMENT_LINKS_DOCS
from .test_event_handlers import test_event_handlers, TEST_DOCUMENTATION as EVENT_HANDLERS_DOCS
from .test_floating_dialogs import test_floating_dialogs, TEST_DOCUMENTATION as FLOATING_DIALOGS_DOCS
from .test_focus_management import test_focus_management, TEST_DOCUMENTATION as FOCUS_MANAGEMENT_DOCS
from .test_fonts import test_fonts, TEST_DOCUMENTATION as FONTS_DOCS
from .test_styles import test_styles, TEST_DOCUMENTATION as STYLES_DOCS
from .test_landmarks import test_landmarks, TEST_DOCUMENTATION as LANDMARKS_DOCS
from .test_lists import test_lists, TEST_DOCUMENTATION as LISTS_DOCS
from .test_maps import test_maps, TEST_DOCUMENTATION as MAPS_DOCS
from .test_menus import test_menus, TEST_DOCUMENTATION as MENUS_DOCS
from .test_modals import test_modals, TEST_DOCUMENTATION as MODALS_DOCS
from .test_read_more_links import test_read_more_links, TEST_DOCUMENTATION as READ_MORE_LINKS_DOCS
from .test_tabindex import test_tabindex, TEST_DOCUMENTATION as TABINDEX_DOCS
from .test_tables import test_tables, TEST_DOCUMENTATION as TABLES_DOCS
from .test_timers import test_timers, TEST_DOCUMENTATION as TIMERS_DOCS
from .test_title_attribute import test_title_attribute, TEST_DOCUMENTATION as TITLE_ATTRIBUTE_DOCS
from .test_videos import test_videos, TEST_DOCUMENTATION as VIDEOS_DOCS
from .test_page import test_page, TEST_DOCUMENTATION as PAGE_DOCS
from .test_language import test_language, TEST_DOCUMENTATION as LANGUAGE_DOCS
from .test_semantic_structure import test_semantic_structure, TEST_DOCUMENTATION as SEMANTIC_STRUCTURE_DOCS

# Map touchpoint IDs to test functions
TOUCHPOINT_TESTS = {
    'headings': test_headings,
    'images': test_images,
    'forms': test_forms,
    'accessible_names': test_accessible_names,
    'aria': test_aria,
    'animations': test_animations,
    'buttons': test_buttons,
    'links': test_links,
    'colors': test_colors,
    'colors_contrast': test_text_contrast,
    'document_links': test_document_links,
    'event_handlers': test_event_handlers,
    'floating_dialogs': test_floating_dialogs,
    'focus_management': test_focus_management,
    'fonts': test_fonts,
    'styles': test_styles,
    'landmarks': test_landmarks,
    'lists': test_lists,
    'maps': test_maps,
    # NOTE: Only 'navigation' is used - 'menus' removed to prevent duplicate test runs
    # The test_menus function handles all navigation/menu testing
    'navigation': test_menus,
    'modals': test_modals,
    'read_more_links': test_read_more_links,
    'tabindex': test_tabindex,
    'tables': test_tables,
    'timers': test_timers,
    'title_attribute': test_title_attribute,
    'videos': test_videos,
    'page': test_page,
    'language': test_language,
    'semantic_structure': test_semantic_structure,
}

# Export all test documentation
TEST_DOCUMENTATION = {
    'headings': HEADINGS_DOCS,
    'images': IMAGES_DOCS,
    'forms': FORMS_DOCS,
    'accessible_names': ACCESSIBLE_NAMES_DOCS,
    'aria': ARIA_DOCS,
    'animations': ANIMATIONS_DOCS,
    'buttons': BUTTONS_DOCS,
    'links': LINKS_DOCS,
    'colors': COLORS_DOCS,
    'colors_contrast': TEXT_CONTRAST_DOCS,
    'document_links': DOCUMENT_LINKS_DOCS,
    'event_handlers': EVENT_HANDLERS_DOCS,
    'floating_dialogs': FLOATING_DIALOGS_DOCS,
    'focus_management': FOCUS_MANAGEMENT_DOCS,
    'fonts': FONTS_DOCS,
    'styles': STYLES_DOCS,
    'landmarks': LANDMARKS_DOCS,
    'lists': LISTS_DOCS,
    'maps': MAPS_DOCS,
    'menus': MENUS_DOCS,
    'modals': MODALS_DOCS,
    'read_more_links': READ_MORE_LINKS_DOCS,
    'tabindex': TABINDEX_DOCS,
    'tables': TABLES_DOCS,
    'timers': TIMERS_DOCS,
    'title_attribute': TITLE_ATTRIBUTE_DOCS,
    'videos': VIDEOS_DOCS,
    'page': PAGE_DOCS,
    'language': LANGUAGE_DOCS,
    'semantic_structure': SEMANTIC_STRUCTURE_DOCS,
}

__all__ = [
    'test_headings',
    'test_images',
    'test_forms',
    'test_accessible_names',
    'test_aria',
    'test_animations',
    'test_buttons',
    'test_links',
    'test_colors',
    'test_text_contrast',
    'test_document_links',
    'test_event_handlers',
    'test_floating_dialogs',
    'test_focus_management',
    'test_fonts',
    'test_styles',
    'test_landmarks',
    'test_lists',
    'test_maps',
    'test_menus',
    'test_modals',
    'test_read_more_links',
    'test_tabindex',
    'test_tables',
    'test_timers',
    'test_title_attribute',
    'test_videos',
    'test_page',
    'test_language',
    'test_semantic_structure',
    'TOUCHPOINT_TESTS',
    'TEST_DOCUMENTATION'
]