import logging
from abc import ABC, abstractmethod
from pprint import pformat
from typing import Sequence, Generator, Callable, Optional

import requests
from requests import HTTPError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .typing import RemoteResult, RemoteResponse

logger = logging.getLogger()


class BaseRemoteClient(ABC):
    """"""


class ListRemoteClientMixin(ABC):
    @abstractmethod
    def list_all(self, *args, **kwargs) -> Generator[RemoteResult, None, None]:
        _, results, next_pages_call = self.get_list_page(*args, **kwargs)
        yield from results
        if next_pages_call:
            yield from next_pages_call()

    @abstractmethod
    def get_list_page(self, *args, **kwargs) -> tuple[
        RemoteResponse,
        Sequence[RemoteResult],
        Optional[Callable[[], Generator[RemoteResult, None, None]]]
    ]:
        raise NotImplementedError


class CreateRemoteClientMixin(ABC):
    @abstractmethod
    def create(self, *args, **kwargs) -> RemoteResult:
        raise NotImplementedError


class RetrieveRemoteClientMixin(ABC):
    @abstractmethod
    def retrieve(self, remote_id) -> RemoteResult:
        raise NotImplementedError


class UpdateRemoteClientMixin(ABC):
    @abstractmethod
    def update(self, remote_id, *args, **kwargs) -> RemoteResult:
        raise NotImplementedError


class DeleteRemoteClientMixin(ABC):
    @abstractmethod
    def delete(self, remote_id) -> RemoteResult:
        raise NotImplementedError


class RemoteClient(
    ListRemoteClientMixin,
    CreateRemoteClientMixin,
    RetrieveRemoteClientMixin,
    UpdateRemoteClientMixin,
    DeleteRemoteClientMixin,
    BaseRemoteClient, ABC
):
    """"""


class RestAPIRemoteClientMixin(ABC):
    def __init__(self):
        self._session = self._setup_session()

    @staticmethod
    def _setup_session():
        session = requests.Session()

        def assert_status_hook(response, *args, **kwargs):
            try:
                response.raise_for_status()
            except HTTPError:
                logger.error(pformat(response.json()))
                raise

        session.hooks['response'] = [assert_status_hook]

        retry_strategy = Retry(
            total=3,
            status_forcelist=[403, 429, 500, 502, 503, 504],
            method_whitelist=['GET'],
            backoff_factor=0.5,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('https://', adapter)
        session.mount('http://', adapter)

        return session


__all__ = (
    'BaseRemoteClient',
    'ListRemoteClientMixin',
    'CreateRemoteClientMixin',
    'RetrieveRemoteClientMixin',
    'UpdateRemoteClientMixin',
    'DeleteRemoteClientMixin',
    'RestAPIRemoteClientMixin',
)
