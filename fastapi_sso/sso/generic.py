"""A generic OAuth client that can be used to quickly create support for any OAuth provider
with close to no code
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Type, Union

from fastapi_sso.sso.base import DiscoveryDocument, OpenID, SSOBase

logger = logging.getLogger(__name__)


def create_provider(
    *,
    name: str = "generic",
    default_scope: Optional[List[str]] = None,
    discovery_document: Union[DiscoveryDocument, Callable[[SSOBase], DiscoveryDocument]],
    response_convertor: Optional[Callable[[Dict[str, Any]], OpenID]] = None
) -> Type[SSOBase]:
    """A factory to create a generic OAuth client usable with almost any OAuth provider.
    Returns a class.

    Args:

        name: Name of the provider
        default_scope: default list of scopes (can be overriden in constructor)
        discovery_document: a dictionary containing discovery document or a callable returning it
        response_convertor: a callable that will receive JSON response from the userinfo endpoint
            and should return OpenID object

    Example:
        ```python
        from fastapi_sso.sso.generic import create_provider

        discovery = {
            "authorization_endpoint": "http://localhost:9090/auth",
            "token_endpoint": "http://localhost:9090/token",
            "userinfo_endpoint": "http://localhost:9090/me",
        }

        SSOProvider = create_provider(name="oidc", discovery_document=discovery)
        sso = SSOProvider(
            client_id="test",
            client_secret="secret",
            redirect_uri="http://localhost:8080/callback",
            allow_insecure_http=True
            )
        ```

    """

    class GenericSSOProvider(SSOBase):
        """SSO Provider Template"""

        provider = name
        scope = default_scope or ["openid"]

        async def get_discovery_document(self) -> DiscoveryDocument:
            """Get document containing handy urls"""
            if callable(discovery_document):
                return discovery_document(self)
            return discovery_document

        @classmethod
        async def openid_from_response(cls, response: dict) -> OpenID:
            if not response_convertor:
                logger.warning("No response convertor was provided, returned OpenID will always be empty")
                return OpenID(
                    provider=cls.provider,
                    data=response,
                )
            return response_convertor(response)

    return GenericSSOProvider
