# Drupal Multilingual Content Translation Research

**Date:** 2026-01-27
**Status:** Research Phase - Not Implemented
**Decision:** Upload English-only content for now; French translation support deferred

## Problem Statement

The current Drupal upload process (as of commit 5e86549) concatenates English and French content into the same submission body field. This approach does not utilize Drupal's proper Content Translation system, resulting in:

- Loss of language negotiation features (e.g., `/en/node/123` vs `/fr/node/123`)
- No proper language switching capability
- Cannot use Drupal's translation management tools
- Cannot query content by specific language
- Both languages appear in the same view, rather than switching based on user's language preference

## Current Implementation (Commit 5e86549)

The recording exporter extracts English and French versions separately and generates HTML sections for each:

```python
# Extract English and French separately
key_takeaways_en = recording.get_key_takeaways('en')
key_takeaways_fr = recording.get_key_takeaways('fr')

# Generate separate HTML sections
key_takeaways_html = self._generate_key_takeaways_html(key_takeaways_en, language='en')
key_takeaways_html_fr = self._generate_key_takeaways_html(key_takeaways_fr, language='fr')

# Concatenate both into single body field
html_parts.append(key_takeaways_html)
html_parts.append(key_takeaways_html_fr)
```

This places both English and French content in a single field, treating it as one piece of content rather than separate translations.

## Drupal's Proper Translation Architecture

In Drupal's Content Translation system:

1. Create a node in the primary language (English)
2. Add translations using `$entity->addTranslation('fr', [...])`
3. Each translation is stored as a separate entity record linked to the original
4. Drupal automatically handles language negotiation and fallbacks

### Example PHP Code

```php
// Create English node
$node = Node::create([
  'type' => 'issue',
  'langcode' => 'en',
  'title' => 'English Title',
  'body' => ['value' => 'English description', 'format' => 'unfiltered'],
]);
$node->save();

// Add French translation
$node_fr = $node->addTranslation('fr', [
  'title' => 'Titre français',
  'body' => ['value' => 'Description française', 'format' => 'unfiltered'],
]);
$node_fr->save();
```

### Benefits of Proper Translation System

- **URL-based language negotiation:** `/en/node/123` and `/fr/node/123` serve different content
- **Language switcher blocks:** Users can toggle between languages
- **Translation management:** Track translation status, outdated translations
- **Language-specific queries:** Filter content by langcode
- **Interface integration:** Works with Drupal's translation UI and workflows

## JSON:API Translation Limitations

Drupal's JSON:API has **severe limitations** for creating translations:

### What JSON:API CAN Do

1. **Create with langcode:** You can POST with `{attributes: {langcode: "fr"}}` to create French content directly
2. **Read translations:** GET `/fr/jsonapi/node/article/UUID` returns the French translation
3. **Language filtering:** Can filter content by langcode in queries

### What JSON:API CANNOT Do

1. **Cannot attach translations:** JSON:API does NOT support creating translations linked to existing entities
2. **PATCH doesn't create translations:** PATCHing with `Content-Language: fr` header updates the entity, it doesn't create a separate translation
3. **No translation relationship:** Cannot POST a reference to say "this is a translation of that entity"

### Why This Limitation Exists

From [Drupal.org issue #2794431](https://www.drupal.org/project/drupal/issues/2794431):

> "We don't know which entity to attach the translation to unless we send some sort of reference"

The JSON:API spec doesn't have a clear pattern for expressing "create this as a translation of that entity." This has been an ongoing limitation since 2017 with no resolution as of 2024-2026.

### Related Drupal Issues

- [#2794431 - [META] Formalize translations support](https://www.drupal.org/project/drupal/issues/2794431) - Main tracking issue since 2017
- [#2897230 - [PP-1] Creating translations (via PATCHing entities?)](https://www.drupal.org/project/jsonapi/issues/2897230)
- [#2135829 - EntityResource: translations support](https://www.drupal.org/project/drupal/issues/2135829) - Core REST API translation support
- [#3037804 - Document the extent of JSON:API's multilingual support](https://www.drupal.org/project/jsonapi/issues/3037804)

## Potential Solutions (For Future Implementation)

### Option 1: Custom REST Endpoint (Best Practice)

Create a custom Drupal REST resource that accepts both languages and properly creates translations using Drupal's Entity API.

#### Drupal Side Implementation

Create a custom REST resource plugin:

```php
<?php

namespace Drupal\custom_api\Plugin\rest\resource;

use Drupal\rest\Plugin\ResourceBase;
use Drupal\rest\ResourceResponse;
use Drupal\node\Entity\Node;
use Symfony\Component\HttpKernel\Exception\BadRequestHttpException;

/**
 * Provides a resource to create content with translations.
 *
 * @RestResource(
 *   id = "custom_translation_create",
 *   label = @Translation("Custom Translation Creator"),
 *   uri_paths = {
 *     "create" = "/api/create-with-translation"
 *   }
 * )
 */
class CustomTranslationResource extends ResourceBase {

  /**
   * Responds to POST requests.
   *
   * @param array $data
   *   The request data.
   *
   * @return \Drupal\rest\ResourceResponse
   *   The HTTP response object.
   */
  public function post($data) {
    if (empty($data['type'])) {
      throw new BadRequestHttpException('Content type is required');
    }

    // Create English node
    $node_data = [
      'type' => $data['type'],
      'langcode' => 'en',
      'title' => $data['title_en'],
      'status' => $data['status'] ?? TRUE,
    ];

    // Add English fields
    foreach ($data as $key => $value) {
      if (str_ends_with($key, '_en') && $key !== 'title_en') {
        $field_name = substr($key, 0, -3); // Remove '_en' suffix
        $node_data[$field_name] = $value;
      }
    }

    $node = Node::create($node_data);
    $node->save();

    // Add French translation if provided
    if (!empty($data['title_fr'])) {
      $translation_data = [
        'title' => $data['title_fr'],
      ];

      // Add French fields
      foreach ($data as $key => $value) {
        if (str_ends_with($key, '_fr') && $key !== 'title_fr') {
          $field_name = substr($key, 0, -3); // Remove '_fr' suffix
          $translation_data[$field_name] = $value;
        }
      }

      $node_fr = $node->addTranslation('fr', $translation_data);
      $node_fr->save();
    }

    return new ResourceResponse([
      'success' => TRUE,
      'uuid' => $node->uuid(),
      'nid' => $node->id(),
      'langcode' => 'en',
      'has_translation' => !empty($data['title_fr']),
    ], 201);
  }
}
```

#### Python Side Implementation

Modify the exporters to send structured data with separate language fields:

```python
def export_issue(
    self,
    title_en: str,
    description_en: str,
    title_fr: Optional[str] = None,
    description_fr: Optional[str] = None,
    # ... other parameters
) -> Dict[str, Any]:
    """
    Export an issue to Drupal with optional French translation.
    """
    payload = {
        'type': 'issue',
        'status': True,

        # English fields
        'title_en': title_en,
        'body_en': {
            'value': description_en,
            'format': 'unfiltered'
        },

        # French fields (optional)
        'title_fr': title_fr,
        'body_fr': {
            'value': description_fr,
            'format': 'unfiltered'
        } if description_fr else None,

        # Shared fields (not language-specific)
        'field_impact': impact,
        # ... other fields
    }

    response = self.client.post_custom('/api/create-with-translation', payload)
    return response
```

#### Advantages

- ✅ Properly uses Drupal's translation system
- ✅ Maintains clean separation between English and French
- ✅ Enables proper language negotiation
- ✅ Future-proof for multilingual features
- ✅ Works with Drupal's translation management UI
- ✅ Supports language-specific URLs

#### Disadvantages

- ❌ Requires Drupal-side development (custom module)
- ❌ Needs configuration of REST resource permissions
- ❌ More complex than direct JSON:API calls

### Option 2: Two-Step JSON:API Process

1. POST English content to create the node via JSON:API
2. Use Drupal's REST API or custom endpoint to attach French translation

#### Example Flow

```python
# Step 1: Create English node
english_payload = {
    'data': {
        'type': 'node--issue',
        'attributes': {
            'title': 'English Title',
            'langcode': 'en',
            'body': {'value': 'English description', 'format': 'unfiltered'}
        }
    }
}
response = client.post('node/issue', english_payload)
node_uuid = response['data']['id']

# Step 2: Add French translation (requires custom endpoint or workaround)
# This part is not natively supported by JSON:API
```

#### Disadvantages

- ❌ Still requires custom Drupal code for step 2
- ❌ Two API calls instead of one
- ❌ More complex error handling (what if step 2 fails?)

### Option 3: Keep Current Approach (Simplest)

Continue concatenating both languages in the body field with language markers.

#### Advantages

- ✅ No Drupal-side development required
- ✅ Works with standard JSON:API
- ✅ Simple implementation
- ✅ Both languages always visible

#### Disadvantages

- ❌ Not using Drupal's translation system
- ❌ No language negotiation
- ❌ Cannot filter by language
- ❌ Cluttered output (both languages always shown)
- ❌ Not following Drupal best practices

### Option 4: English-Only Upload (Current Decision)

Upload only English content for now, defer French translation support.

#### Implementation

```python
# Generate only English sections
key_takeaways_en = recording.get_key_takeaways('en')
key_takeaways_html = self._generate_key_takeaways_html(key_takeaways_en, language='en')
html_parts.append(key_takeaways_html)

# Do NOT include French sections
# French data exists in the database but is not uploaded to Drupal
```

#### Advantages

- ✅ Simplest immediate solution
- ✅ Clean English-only output
- ✅ No multilingual complexity
- ✅ Works with standard JSON:API
- ✅ Easy to extend later with proper translation support

#### Disadvantages

- ❌ Loses French content (even though it's available)
- ❌ Requires future work to add multilingual support
- ❌ May need re-upload of historical content when translations are implemented

## Recommendation for Future Implementation

**When ready to implement proper multilingual support, use Option 1 (Custom REST Endpoint):**

1. Create custom Drupal module with REST resource
2. Modify Python exporters to send separate `_en` and `_fr` fields
3. Benefits: proper translation architecture, language negotiation, future-proof

**Short-term workaround:**
- Continue with English-only uploads (Option 4)
- Store French data in local database for future use
- Re-evaluate when Drupal JSON:API translation support improves or when business needs require multilingual content

## Resources and Documentation

### Official Drupal Documentation

- [Translations | JSON:API module](https://www.drupal.org/docs/core-modules-and-themes/core-modules/jsonapi-module/translations)
- [Entity Translation API](https://www.drupal.org/docs/drupal-apis/entity-api/entity-translation-api)
- [Translation API Overview](https://www.drupal.org/docs/8/api/translation-api/overview)
- [Custom REST Resources](https://www.drupal.org/docs/develop/drupal-apis/restful-web-services-api/custom-rest-resources)

### Community Tutorials

- [Create and translate multilingual nodes programmatically](https://www.drupal8.ovh/en/tutoriels/50/create-and-translate-a-multilingual-nodes-programmatically)
- [Translate programmatically with Drupal 8 | Flocon de toile](https://www.flocondetoile.fr/blog/translate-programmatically-drupal-8)
- [Drupal Entity Translation guide](https://www.bramvandenbulcke.be/en/article/drupal-entity-translation-guide)

### GitHub Resources

- [drupal-jsonapi-translations](https://github.com/gabesullice/drupal-jsonapi-translations/blob/master/index.md) - Community documentation on JSON:API translation workarounds

### Related Issues

- [#2794431 - [META] Formalize translations support](https://www.drupal.org/project/drupal/issues/2794431) - Main tracking issue
- [#2897230 - [PP-1] Creating translations (via PATCHing entities?)](https://www.drupal.org/project/jsonapi/issues/2897230)
- [#2135829 - EntityResource: translations support](https://www.drupal.org/project/drupal/issues/2135829)
- [#3037804 - Document the extent of JSON:API's multilingual support](https://www.drupal.org/project/jsonapi/issues/3037804)
- [#3066113 - How to translate an entity programmatically](https://www.drupal.org/project/drupal/issues/3066113)

## Conclusion

Drupal's JSON:API does not currently support creating content translations via standard POST/PATCH operations. The recommended approach for proper multilingual support is to create a custom REST endpoint that uses Drupal's Entity Translation API (`addTranslation()` method).

For now, the decision is to **upload English content only** and revisit multilingual support when:
1. Business requirements explicitly need French content in Drupal
2. Resources are available for Drupal-side custom development
3. JSON:API translation support improves (monitor issue #2794431)

The French content remains in the local Auto A11y database and can be:
- Exported separately if needed
- Used for future re-uploads when translation support is implemented
- Displayed in local reports that support language switching
