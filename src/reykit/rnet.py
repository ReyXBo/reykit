# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-08 11:07:25
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Network methods.
"""


from typing import Any, Literal, TypedDict, NotRequired
from collections.abc import Callable, Iterable
from warnings import filterwarnings
from os.path import abspath as os_abspath, isfile as os_isfile
from socket import socket as  Socket
from urllib.parse import urlsplit as urllib_urlsplit, quote as urllib_quote, unquote as urllib_unquote
from requests.api import request as requests_request
from requests.models import Response
from requests_cache import (
    ALL_METHODS,
    OriginalResponse,
    CachedResponse,
    install_cache as requests_cache_install_cache,
    uninstall_cache as requests_cache_uninstall_cache,
    is_installed as requests_cache_is_installed,
    clear as requests_cache_clear
)
from mimetypes import guess_type
from filetype import guess as filetype_guess
from datetime import datetime

from .rbase import Base, throw, check_response_code
from .ros import File
from .rre import search


__all__ = (
    'join_url',
    'split_url',
    'join_cookie',
    'split_cookie',
    'get_content_type',
    'request',
    'download',
    'compute_stream_time',
    'listen_socket',
    'RequestCache'
)


RequestCacheParameters = TypedDict(
    'RequestCacheParameters',
    {
        'cache_name': str,
        'backend': Literal['sqllite', 'memory'],
        'expire_after': NotRequired[float | datetime],
        'code': Iterable[int],
        'method': Iterable[str],
        'judge': NotRequired[Callable[[Response], bool]]
    }
)


def join_url(url: str, params: dict) -> str:
    """
    Join URL and parameters.

    Parameters
    ----------
    url : URL.
    params : Parameters of URL.

    Returns
    -------
    Joined URL.
    """

    # Join parameter.
    params_str = '&'.join(
        [
            f'{key}={urllib_quote(value)}'
            for key, value in params.items()
        ]
    )

    # Join URL.
    if '?' not in url:
        url += '?'
    elif url[-1] != '?':
        url += '&'
    url += params_str

    return url


def split_url(url: str) -> tuple[str, dict[str, str]]:
    """
    Split URL and parameters.

    Parameters
    ----------
    url : URL.

    Returns
    -------
    Split URL and parameters.
    """

    # Split URL.
    split_result = urllib_urlsplit(url)
    params_str = split_result.query
    url = split_result.scheme + '://' + split_result.netloc + split_result.path

    # Split parameter.
    params = {
        key: urllib_unquote(value)
        for key, value in map(
            lambda item: item.split('=', 1),
            params_str.split('&')
        )
    }

    return url, params


def join_cookie(params: dict[str, str]) -> str:
    """
    Join parameters of Cookie.

    Parameters
    ----------
    params : Parameters.

    Returns
    -------
    Joined cookie.
    """

    # Join.
    cookie = '; '.join(
        [
            f'{key}={value}'
            for key, value in params.items()
        ]
    )

    return cookie


def split_cookie(cookie: str) -> dict[str, str]:
    """
    Split parameters of Cookie.

    Parameters
    ----------
    cookie : Cookie.

    Returns
    -------
    Split parameters
    """

    # Split parameter.
    params = {
        key: value
        for key, value in map(
            lambda item: item.split('=', 1),
            cookie.split('; ')
        )
    }

    return params


def get_content_type(file: str | bytes) -> str | None:
    """
    Get HTTP content type of file.

    Parameters
    ----------
    file : File path or bytes data.

    Returns
    -------
    HTTP content type.
    """

    # Guess.
    if (
        (
            type(file) == str
            and os_isfile(file)
        ) or type(file) == bytes
    ):
        file_type_obj = filetype_guess(file)
    else:
        file_type_obj = None
    if file_type_obj is not None:
        file_type = file_type_obj.MIME
    elif type(file) == str:
        file_type, _ = guess_type(file)
    else:
        file_type = None

    return file_type


def request(
    url: str,
    params: dict | None = None,
    data: dict | str | bytes | None = None,
    json: dict | None = None,
    files: dict[str, str | bytes | tuple[str | bytes, dict]] | None = None,
    headers: dict[str, str] = {},
    timeout: float | None = None,
    proxies: dict[str, str] = {},
    stream: bool = False,
    verify: bool = False,
    method: Literal['get', 'post', 'put', 'patch', 'delete', 'options', 'head'] | None = None,
    check: bool | int | Iterable[int] = False
) -> Response:
    """
    Send request.

    Parameters
    ----------
    url : Request URL.
    params : Request URL add parameters.
    data : Request body data.
        - `dict`, Convert to `key=value&...`: format bytes.
            Automatic set `Content-Type` to `application/x-www-form-urlencoded`.
        - `str`: File path to read file bytes data.
            Automatic set `Content-Type` to file media type, and `filename` to file name.
        - `bytes`: File bytes data.
            Automatic set `Content-Type` to file media type.
    json : Request body data, convert to `JSON` format.
        Automatic set `Content-Type` to `application/json`.
    files : Request body data, convert to `multi form` format.
        Automatic set `Content-Type` to `multipart/form-data`.
        - `dict[str, str]`: Parameter name and File path to read file bytes data.
            Automatic set `Content-Type` to file media type, and `filename` to file name.
        - `dict[str, bytes]`: Parameter name and file bytes data.
        - `dict[str, tuple[str, dict]`: Parameter name and File path to read file bytes data and other parameters.
            Automatic set `Content-Type` to file media type, and `filename` to file name.
        - `dict[str, tuple[bytes, dict]`: Parameter name and file bytes data and other parameters.
    headers : Request header data.
    timeout : Request maximun waiting time.
    proxies : Proxy IP setup.
        - `None`: No setup.
        - `dict[str, str]`: Name and use IP of each protocol.
    stream : Whether use stream request.
    verify : Whether verify certificate.
    method : Request method.
        - `None`: Automatic judge.
            When parameter `data` or `json` or `files` not has value, then request method is `get`.
            When parameter `data` or `json` or `files` has value, then request method is `post`.
        - `Literal['get', 'post', 'put', 'patch', 'delete', 'options', 'head']`: Use this request method.
    check : Check response code, and throw exception.
        - `Literal[False]`: Not check.
        - `Literal[True]`: Check if is between 200 and 299.
        - `int`: Check if is this value.
        - `Iterable`: Check if is in sequence.

    Returns
    -------
    Response object of requests package.
    """

    # Handle parameter.
    if method is None:
        if data is None and json is None and files is None:
            method = 'get'
        else:
            method = 'post'
    if files is None:
        if type(data) == str:
            rfile = File(data)
            data = rfile.bytes
            if 'Content-Disposition' not in headers:
                file_name = rfile.name_suffix
                headers['Content-Disposition'] = f'attachment; filename={file_name}'
        if type(data) == bytes:
            if 'Content-Type' not in headers:
                headers['Content-Type'] = get_content_type(data)
    else:
        for key, value in files.items():
            if type(value) == tuple:
                item_data, item_headers = value
            else:
                item_data, item_headers = value, {}
            if type(item_data) == str:
                rfile = File(item_data)
                data = rfile.bytes
                item_headers.setdefault('filename', rfile.name_suffix)
            if type(item_data) == bytes:
                if 'Content-Type' not in item_headers:
                    item_headers['Content-Type'] = get_content_type(item_data)
            files[key] = (
                item_headers.get('filename', key),
                item_data,
                item_headers.get('Content-Type'),
                item_headers
            )
    if not verify:
        filterwarnings(
            'ignore',
            'Unverified HTTPS request is being made to host'
        )

    # Request.
    response = requests_request(
        method,
        url,
        params=params,
        data=data,
        json=json,
        files=files,
        headers=headers,
        timeout=timeout,
        proxies=proxies,
        verify=verify,
        stream=stream
    )

    # Set encod type.
    if response.encoding == 'ISO-8859-1':
        pattern = r'<meta [^>]*charset=([\w-]+)[^>]*>'
        charset = search(pattern, response.text)
        if charset is None:
            charset = 'utf-8'
        response.encoding = charset

    # Check code.
    if check is not False:
        if check is True:
            range_ = None
        else:
            range_ = check
        check_response_code(response.status_code, range_)

    return response


def download(url: str, path: str | None = None) -> str:
    """
    Download file from URL.

    Parameters
    ----------
    url : Download URL.
    path : Save path.
        - `None`, File name is `download`: and automatic judge file type.

    Returns
    -------
    File absolute path.
    """

    # Download.
    response = request(url)
    content = response.content

    # Judge file type and path.
    if path is None:
        Content_disposition = response.headers.get('Content-Disposition', '')
        if 'filename' in Content_disposition:
            file_name = search(
                'filename=[\'"]?([^\\s\'"]+)',
                Content_disposition
            )
        else:
            file_name = None
        if file_name is None:
            file_type_obj = get_content_type(content)
            if file_type_obj is not None:
                file_name = 'download.' + file_type_obj.EXTENSION
        if file_name is None:
            file_name = 'download'
        path = os_abspath(file_name)

    # Save.
    rfile = File(path)
    rfile(content)

    return path


def compute_stream_time(
    file: str | bytes | int,
    bandwidth: float
) -> float:
    """
    Compute file stream transfer time, unit second.

    Parameters
    ----------
    file : File data.
        - `str`: File path.
        - `bytes`: File bytes data.
        - `int`: File bytes size.
    bandwidth : Bandwidth, unit Mpbs.

    Returns
    -------
    File send seconds.
    """

    # Get parameter.
    match file:
        case str():
            rfile = File(file)
            file_size = rfile.size
        case bytes() | bytearray():
            file_size = len(file)
        case int():
            file_size = file
        case _:
            throw(TypeError, file)

    # Calculate.
    seconds = file_size / 125_000 / bandwidth

    return seconds


def listen_socket(
    host: str,
    port: str | int,
    handler: Callable[[bytes], Any]
) -> None:
    """
    Listen socket and handle data.

    Parameters
    ----------
    host : Socket host.
    port : Socket port.
    handler : Handler function.
    """

    # Handle parameter.
    port = int(port)
    rece_size = 1024 * 1024 * 1024

    # Instance.
    socket = Socket()
    socket.bind((host, port))
    socket.listen()

    # Loop.
    while True:
        socket_conn, _ = socket.accept()
        data = socket_conn.recv(rece_size)
        handler(data)


class RequestCache(Base):
    """
    Requests cache type.
    """


    def __init__(
        self,
        path: str | None = 'cache.sqlite',
        timeout: float | datetime | None = None,
        codes: Iterable[int] | None = (200,),
        methods: Iterable[str] | None = ('get', 'head'),
        judge: Callable[[Response | OriginalResponse | CachedResponse], bool] | None = None
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        path : Cache file path.
            - `None`: Use memory cache.
            - `str`: Use SQLite cache.
        timeout : Cache timeout.
            - `None`: Not timeout.
            - `float`: Timeout seconds.
            - `datetime`: Timeout threshold time.
        codes : Cache response code range.
            - `None`: All.
        methods : Cache request method range.
            - `None`: All.
        judge : Judge function, `True` cache, `False` not cache.
            - `None`: Not judgment.
        """

        # Build.
        self.path = path
        self.timeout = timeout
        self.codes = codes
        self.methods = methods
        self.judge = judge


    @property
    def _start_params(self) -> RequestCacheParameters:
        """
        Get cache start parameters.

        Returns
        -------
        Cache start parameters.
        """

        # Generate.
        params = {}
        if self.path is None:
            params['cache_name'] = 'cache'
            params['backend'] = 'memory'
        else:
            params['cache_name'] = self.path
            params['backend'] = 'sqlite'
        if self.timeout is not None:
            params['expire_after'] = self.timeout
        if self.codes is None:
            params['allowable_codes'] = tuple(range(100, 600))
        else:
            params['allowable_codes'] = self.codes
        if self.methods is None:
            params['allowable_methods'] = ALL_METHODS
        else:
            params['allowable_methods'] = tuple([method.upper() for method in self.methods])
        if self.judge is not None:
            params['filter_fn'] = self.judge

        return params


    def start(self) -> None:
        """
        Start cache.
        """

        # Start.
        requests_cache_install_cache(**self._start_params)


    def stop(self) -> None:
        """
        Stop cache.
        """

        # Stop.
        requests_cache_uninstall_cache()


    @property
    def started(self) -> bool:
        """
        Whether started.

        Returns
        -------
        Result.
        """

        # Get.
        result = requests_cache_is_installed()

        return result


    def clear(self) -> None:
        """
        Clear cache.
        """

        # Clear.
        requests_cache_clear()
