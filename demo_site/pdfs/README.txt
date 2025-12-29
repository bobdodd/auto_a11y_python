PDF Placeholder Files

For the demo, you can place actual PDF files here:
- guide-services-en.pdf (English guide - linked from French page without warning)
- guide-permis-fr.pdf (French guide)

These links will trigger the ErrDocumentLinkWrongLanguage error when:
1. A French page links to an English PDF without warning
2. The PDF link doesn't have a lang attribute or warning text

For the demo, the autoA11y system will detect:
- Missing language attributes on cross-language document links
- Missing warnings about document language
