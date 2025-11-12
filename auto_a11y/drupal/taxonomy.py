"""
Drupal Taxonomy Management

Handles caching and lookup of Drupal taxonomy terms, particularly:
- "interested_in_because" - Why pages are interesting (75 terms)
- "page_elements" - Areas of display (16 terms)
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TaxonomyCache:
    """
    Cache for Drupal taxonomy terms with automatic refresh.

    Caches taxonomy terms by vocabulary and provides efficient lookup by name or UUID.
    """

    def __init__(self, client, cache_duration_hours: int = 24):
        """
        Initialize taxonomy cache.

        Args:
            client: DrupalJSONAPIClient instance
            cache_duration_hours: How long to cache terms before refresh (default: 24 hours)
        """
        self.client = client
        self.cache_duration = timedelta(hours=cache_duration_hours)

        # Cache structure: {vocabulary_name: {'terms': [...], 'last_updated': datetime, 'by_name': {}, 'by_uuid': {}}}
        self._cache: Dict[str, dict] = {}

    def get_terms(self, vocabulary: str, force_refresh: bool = False) -> List[Dict]:
        """
        Get all terms for a vocabulary.

        Args:
            vocabulary: Vocabulary machine name (e.g., "interested_in_because")
            force_refresh: Force refresh from Drupal even if cached

        Returns:
            List of term dictionaries with 'uuid', 'name', 'tid', 'weight', etc.
        """
        # Check if we need to refresh
        if force_refresh or vocabulary not in self._cache or self._is_cache_expired(vocabulary):
            self._refresh_vocabulary(vocabulary)

        return self._cache.get(vocabulary, {}).get('terms', [])

    def get_uuid_by_name(self, vocabulary: str, term_name: str) -> Optional[str]:
        """
        Look up a term UUID by its name.

        Args:
            vocabulary: Vocabulary machine name
            term_name: Term name to look up (case-insensitive)

        Returns:
            Term UUID or None if not found
        """
        # Ensure vocabulary is cached
        if vocabulary not in self._cache:
            self._refresh_vocabulary(vocabulary)

        by_name = self._cache.get(vocabulary, {}).get('by_name', {})
        return by_name.get(term_name.lower())

    def get_name_by_uuid(self, vocabulary: str, term_uuid: str) -> Optional[str]:
        """
        Look up a term name by its UUID.

        Args:
            vocabulary: Vocabulary machine name
            term_uuid: Term UUID to look up

        Returns:
            Term name or None if not found
        """
        # Ensure vocabulary is cached
        if vocabulary not in self._cache:
            self._refresh_vocabulary(vocabulary)

        by_uuid = self._cache.get(vocabulary, {}).get('by_uuid', {})
        return by_uuid.get(term_uuid)

    def get_term_details(self, vocabulary: str, term_name: str) -> Optional[Dict]:
        """
        Get full term details by name.

        Args:
            vocabulary: Vocabulary machine name
            term_name: Term name to look up

        Returns:
            Full term dictionary or None if not found
        """
        # Ensure vocabulary is cached
        if vocabulary not in self._cache:
            self._refresh_vocabulary(vocabulary)

        terms = self._cache.get(vocabulary, {}).get('terms', [])
        term_name_lower = term_name.lower()

        for term in terms:
            if term.get('name', '').lower() == term_name_lower:
                return term

        return None

    def lookup_uuids(self, vocabulary: str, term_names: List[str]) -> List[str]:
        """
        Look up UUIDs for multiple term names.

        Args:
            vocabulary: Vocabulary machine name
            term_names: List of term names to look up

        Returns:
            List of UUIDs (skips terms not found, logs warning)
        """
        uuids = []

        for name in term_names:
            uuid = self.get_uuid_by_name(vocabulary, name)
            if uuid:
                uuids.append(uuid)
            else:
                logger.warning(f"Term '{name}' not found in vocabulary '{vocabulary}'")

        return uuids

    def lookup_names(self, vocabulary: str, term_uuids: List[str]) -> List[str]:
        """
        Look up names for multiple term UUIDs.

        Args:
            vocabulary: Vocabulary machine name
            term_uuids: List of term UUIDs to look up

        Returns:
            List of term names (skips UUIDs not found, logs warning)
        """
        names = []

        for uuid in term_uuids:
            name = self.get_name_by_uuid(vocabulary, uuid)
            if name:
                names.append(name)
            else:
                logger.warning(f"UUID '{uuid}' not found in vocabulary '{vocabulary}'")

        return names

    def refresh_all(self):
        """Refresh all cached vocabularies."""
        vocabularies = list(self._cache.keys())
        for vocab in vocabularies:
            self._refresh_vocabulary(vocab)

    def clear_cache(self):
        """Clear all cached taxonomy data."""
        self._cache.clear()
        logger.info("Taxonomy cache cleared")

    def _is_cache_expired(self, vocabulary: str) -> bool:
        """Check if cached vocabulary has expired."""
        if vocabulary not in self._cache:
            return True

        last_updated = self._cache[vocabulary].get('last_updated')
        if not last_updated:
            return True

        return datetime.now() - last_updated > self.cache_duration

    def _refresh_vocabulary(self, vocabulary: str):
        """
        Refresh a vocabulary from Drupal.

        Args:
            vocabulary: Vocabulary machine name
        """
        logger.info(f"Refreshing taxonomy vocabulary: {vocabulary}")

        try:
            # Fetch all terms for this vocabulary
            # Use pagination to get all terms (some vocabularies have 75+ terms)
            all_terms = []
            page_limit = 50
            offset = 0

            while True:
                response = self.client.get(
                    f'taxonomy_term/{vocabulary}',
                    params={
                        'page[limit]': page_limit,
                        'page[offset]': offset,
                        'sort': 'weight,name'  # Sort by weight first, then name
                    }
                )

                terms = response.get('data', [])
                if not terms:
                    break

                all_terms.extend(terms)
                offset += page_limit

                # If we got fewer than page_limit, we're done
                if len(terms) < page_limit:
                    break

            # Process terms into cache structure
            by_name = {}
            by_uuid = {}
            processed_terms = []

            for term in all_terms:
                uuid = term.get('id')
                attributes = term.get('attributes', {})
                name = attributes.get('name')
                tid = attributes.get('drupal_internal__tid')
                weight = attributes.get('weight', 0)
                desc_field = attributes.get('description')
                description = desc_field.get('value', '') if desc_field and isinstance(desc_field, dict) else ''

                if not uuid or not name:
                    logger.warning(f"Skipping invalid term in {vocabulary}: {term}")
                    continue

                # Store in lookup maps (case-insensitive for names)
                by_name[name.lower()] = uuid
                by_uuid[uuid] = name

                # Store full term details
                processed_terms.append({
                    'uuid': uuid,
                    'name': name,
                    'tid': tid,
                    'weight': weight,
                    'description': description
                })

            # Update cache
            self._cache[vocabulary] = {
                'terms': processed_terms,
                'by_name': by_name,
                'by_uuid': by_uuid,
                'last_updated': datetime.now()
            }

            logger.info(f"Cached {len(processed_terms)} terms for vocabulary '{vocabulary}'")

        except Exception as e:
            logger.error(f"Failed to refresh vocabulary '{vocabulary}': {e}")
            raise


class DiscoveredPageTaxonomies:
    """
    High-level interface for discovered page taxonomies.

    Provides convenient access to the two main taxonomies used for discovered pages:
    - interested_in_because (75 terms)
    - page_elements (16 terms)
    """

    # Vocabulary machine names
    INTERESTED_BECAUSE = "interested_in_because"
    PAGE_ELEMENTS = "page_elements"

    def __init__(self, client):
        """
        Initialize taxonomy manager.

        Args:
            client: DrupalJSONAPIClient instance
        """
        self.cache = TaxonomyCache(client)

    def get_interested_because_terms(self, force_refresh: bool = False) -> List[Dict]:
        """
        Get all "interested because" terms.

        Returns:
            List of term dicts with 'uuid', 'name', 'tid', 'weight', 'description'
        """
        return self.cache.get_terms(self.INTERESTED_BECAUSE, force_refresh)

    def get_page_elements_terms(self, force_refresh: bool = False) -> List[Dict]:
        """
        Get all "page elements" (area of display) terms.

        Returns:
            List of term dicts with 'uuid', 'name', 'tid', 'weight', 'description'
        """
        return self.cache.get_terms(self.PAGE_ELEMENTS, force_refresh)

    def lookup_interested_because_uuids(self, term_names: List[str]) -> List[str]:
        """
        Convert "interested because" term names to UUIDs.

        Args:
            term_names: List of term names (e.g., ["Form", "Date Picker or Calendar"])

        Returns:
            List of UUIDs
        """
        return self.cache.lookup_uuids(self.INTERESTED_BECAUSE, term_names)

    def lookup_page_elements_uuids(self, term_names: List[str]) -> List[str]:
        """
        Convert "page elements" term names to UUIDs.

        Args:
            term_names: List of term names (e.g., ["Header", "Main body"])

        Returns:
            List of UUIDs
        """
        return self.cache.lookup_uuids(self.PAGE_ELEMENTS, term_names)

    def lookup_interested_because_names(self, term_uuids: List[str]) -> List[str]:
        """
        Convert "interested because" UUIDs to term names.

        Args:
            term_uuids: List of term UUIDs

        Returns:
            List of term names
        """
        return self.cache.lookup_names(self.INTERESTED_BECAUSE, term_uuids)

    def lookup_page_elements_names(self, term_uuids: List[str]) -> List[str]:
        """
        Convert "page elements" UUIDs to term names.

        Args:
            term_uuids: List of term UUIDs

        Returns:
            List of term names
        """
        return self.cache.lookup_names(self.PAGE_ELEMENTS, term_uuids)

    def validate_term_names(self, vocabulary: str, term_names: List[str]) -> Tuple[List[str], List[str]]:
        """
        Validate term names against a vocabulary.

        Args:
            vocabulary: Vocabulary machine name
            term_names: List of term names to validate

        Returns:
            Tuple of (valid_names, invalid_names)
        """
        valid = []
        invalid = []

        for name in term_names:
            if self.cache.get_uuid_by_name(vocabulary, name):
                valid.append(name)
            else:
                invalid.append(name)

        return valid, invalid

    def get_term_suggestions(self, vocabulary: str, partial_name: str, limit: int = 10) -> List[Dict]:
        """
        Get term suggestions based on partial name match.

        Args:
            vocabulary: Vocabulary machine name
            partial_name: Partial term name to search for
            limit: Maximum number of suggestions to return

        Returns:
            List of matching term dicts
        """
        terms = self.cache.get_terms(vocabulary)
        partial_lower = partial_name.lower()

        # Find terms that contain the partial name
        matches = [
            term for term in terms
            if partial_lower in term.get('name', '').lower()
        ]

        # Sort by how early the match appears in the term name
        matches.sort(key=lambda t: t.get('name', '').lower().index(partial_lower))

        return matches[:limit]

    def refresh_all(self):
        """Refresh all taxonomy caches."""
        self.cache.refresh_all()

    def clear_cache(self):
        """Clear all taxonomy caches."""
        self.cache.clear_cache()
