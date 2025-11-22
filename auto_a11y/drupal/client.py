"""
Drupal JSON:API Client

Handles low-level communication with Drupal's JSON:API endpoints using
HTTP Basic Authentication.
"""

import logging
import base64
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlencode

logger = logging.getLogger(__name__)


class DrupalJSONAPIError(Exception):
    """Base exception for Drupal JSON:API errors"""
    pass


class DrupalConnectionError(DrupalJSONAPIError):
    """Raised when connection to Drupal fails"""
    pass


class DrupalAuthenticationError(DrupalJSONAPIError):
    """Raised when authentication fails"""
    pass


class DrupalValidationError(DrupalJSONAPIError):
    """Raised when Drupal rejects data due to validation"""
    pass


class DrupalJSONAPIClient:
    """
    Client for interacting with Drupal's JSON:API.

    Provides GET and POST methods with proper authentication headers
    and error handling.
    """

    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize the Drupal JSON:API client.

        Args:
            base_url: Base URL of the Drupal site (e.g., 'https://example.com')
            username: Drupal username for Basic Auth
            password: Drupal password for Basic Auth
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password

        # Create auth header
        credentials = f"{username}:{password}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()

        # Standard JSON:API headers
        self.headers = {
            'Accept': 'application/vnd.api+json',
            'Content-Type': 'application/vnd.api+json',
            'Authorization': f'Basic {b64_credentials}'
        }

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        logger.info(f"Initialized Drupal JSON:API client for {self.base_url}")

    def _build_url(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Build a complete URL for a JSON:API endpoint.

        Args:
            endpoint: The JSON:API endpoint (e.g., 'node/discovered_page')
            params: Optional query parameters

        Returns:
            Complete URL with optional query string
        """
        # Ensure endpoint starts with /jsonapi/
        if not endpoint.startswith('/jsonapi/'):
            endpoint = f'/jsonapi/{endpoint}'

        url = urljoin(self.base_url, endpoint)

        if params:
            # Use safe parameter to prevent encoding of brackets for Drupal JSON:API
            query_string = urlencode(params, safe='[]')
            url = f"{url}?{query_string}"

        return url

    def test_connection(self) -> bool:
        """
        Test the connection to Drupal by fetching the JSON:API index.

        Returns:
            True if connection successful, False otherwise

        Raises:
            DrupalConnectionError: If connection fails
            DrupalAuthenticationError: If authentication fails
        """
        try:
            url = self._build_url('')
            response = self.session.get(url, timeout=10)

            if response.status_code == 401:
                raise DrupalAuthenticationError(
                    "Authentication failed. Check username and password."
                )

            if response.status_code == 403:
                raise DrupalAuthenticationError(
                    "Access forbidden. User may lack permissions for JSON:API."
                )

            response.raise_for_status()

            logger.info("Successfully connected to Drupal JSON:API")
            return True

        except requests.exceptions.Timeout:
            raise DrupalConnectionError(f"Connection to {self.base_url} timed out")

        except requests.exceptions.ConnectionError as e:
            raise DrupalConnectionError(f"Could not connect to {self.base_url}: {e}")

        except requests.exceptions.RequestException as e:
            raise DrupalConnectionError(f"Connection error: {e}")

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform a GET request to a JSON:API endpoint.

        Args:
            endpoint: The JSON:API endpoint (e.g., 'node/discovered_page')
            params: Optional query parameters (filters, includes, etc.)

        Returns:
            Parsed JSON response

        Raises:
            DrupalJSONAPIError: If request fails
        """
        url = self._build_url(endpoint, params)

        try:
            logger.debug(f"GET {url}")
            response = self.session.get(url, timeout=30)

            # Handle authentication errors
            if response.status_code == 401:
                raise DrupalAuthenticationError("Authentication failed")

            if response.status_code == 403:
                raise DrupalAuthenticationError("Access forbidden")

            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:
            raise DrupalConnectionError(f"Request to {url} timed out")

        except requests.exceptions.RequestException as e:
            logger.error(f"GET request failed: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise DrupalJSONAPIError(f"GET request failed: {e}")

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a POST request to a JSON:API endpoint.

        Args:
            endpoint: The JSON:API endpoint (e.g., 'node/issue')
            data: JSON:API formatted data to send

        Returns:
            Parsed JSON response containing created entity

        Raises:
            DrupalJSONAPIError: If request fails
            DrupalValidationError: If Drupal rejects the data
        """
        url = self._build_url(endpoint)

        try:
            logger.debug(f"POST {url}")
            logger.debug(f"Data: {data}")

            response = self.session.post(url, json=data, timeout=30)

            # Handle authentication errors
            if response.status_code == 401:
                raise DrupalAuthenticationError("Authentication failed")

            if response.status_code == 403:
                raise DrupalAuthenticationError("Access forbidden")

            # Handle validation errors
            if response.status_code == 422:
                error_data = response.json()
                error_msg = self._parse_validation_errors(error_data)
                raise DrupalValidationError(f"Validation failed: {error_msg}")

            response.raise_for_status()

            result = response.json()
            logger.info(f"Successfully created entity: {result.get('data', {}).get('id')}")

            return result

        except requests.exceptions.Timeout:
            raise DrupalConnectionError(f"Request to {url} timed out")

        except requests.exceptions.RequestException as e:
            logger.error(f"POST request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response: {e.response.text}")
            raise DrupalJSONAPIError(f"POST request failed: {e}")

    def patch(self, endpoint: str, uuid: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a PATCH request to update an entity.

        Args:
            endpoint: The JSON:API endpoint (e.g., 'node/issue')
            uuid: UUID of the entity to update
            data: JSON:API formatted data to send

        Returns:
            Parsed JSON response containing updated entity

        Raises:
            DrupalJSONAPIError: If request fails
        """
        url = self._build_url(f"{endpoint}/{uuid}")

        try:
            logger.debug(f"PATCH {url}")
            response = self.session.patch(url, json=data, timeout=30)

            if response.status_code == 401:
                raise DrupalAuthenticationError("Authentication failed")

            if response.status_code == 403:
                raise DrupalAuthenticationError("Access forbidden")

            if response.status_code == 422:
                error_data = response.json()
                error_msg = self._parse_validation_errors(error_data)
                raise DrupalValidationError(f"Validation failed: {error_msg}")

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"PATCH request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise DrupalJSONAPIError(f"PATCH request failed: {e}")

    def _parse_validation_errors(self, error_data: Dict[str, Any]) -> str:
        """
        Parse JSON:API validation errors into a readable message.

        Args:
            error_data: The error response from Drupal

        Returns:
            Human-readable error message
        """
        errors = error_data.get('errors', [])
        if not errors:
            return "Unknown validation error"

        messages = []
        for error in errors:
            title = error.get('title', 'Validation error')
            detail = error.get('detail', '')
            source = error.get('source', {})
            pointer = source.get('pointer', '')

            if pointer:
                messages.append(f"{pointer}: {title} - {detail}")
            else:
                messages.append(f"{title}: {detail}")

        return "; ".join(messages)

    def close(self):
        """Close the session and clean up resources."""
        self.session.close()
        logger.debug("Closed Drupal JSON:API client session")
