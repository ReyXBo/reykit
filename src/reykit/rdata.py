# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-05 14:10:42
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Data methods.
"""


from typing import Any, TypedDict, Literal, overload
from collections import defaultdict as Defaultdict, ChainMap
from collections.abc import Callable, Iterable, Generator
from itertools import chain as IChain

from .rbase import T, KT, VT, Base, null, check_least_one, check_most_one, is_iterable


__all__ = (
    'count',
    'flatten',
    'split',
    'unique',
    'in_arrs',
    'objs_in',
    'chain',
    'default_dict',
    'FunctionGenerator'
)


CountResult = TypedDict('CountResult', {'value': Any, 'count': int})


def count(
    data: Iterable,
    ascend: bool = False
) -> list[CountResult]:
    """
    Group count data element value.

    Parameters
    ----------
    data : Data.
    ascend : Whether ascending by count, otherwise descending order.

    Returns
    -------
    Count result.

    Examples
    --------
    >>> count([1, True, 1, '1', (2, 3)])
    [{'value': 1, 'count': 2}, {'value': True, 'count': 1}, {'value': '1', 'count': 1}, {'value': (2, 3), 'count': 1}]
    """

    # Set parameter.
    value_list = []
    count_list = []

    # Count.
    for element in data:
        for index, value in enumerate(value_list):
            element_str = str(element)
            value_str = str(value)
            if element_str == value_str:
                count_list[index] += 1
                break
        else:
            value_list.append(element)
            count_list.append(1)

    # Convert.
    result = [
        {
            'value': value,
            'count': count
        }
        for value, count in zip(value_list, count_list)
    ]

    # Sort.
    result.sort(
        key=lambda info: info['count'],
        reverse=not ascend
    )

    return result


def flatten(data: Any, *, _flattern_data: list | None = None) -> list:
    """
    Flatten data.

    Parameters
    ----------
    data : Data.
    _flattern_data : Recursion cumulative data.

    Returns
    -------
    Data after flatten.
    """

    # Handle parameter.
    _flattern_data = _flattern_data or []

    # Flatten.

    ## Recursion dict object.
    if type(data) == dict:
        for element in data.values():
            _flattern_data = flatten(
                element,
                _flattern_data = _flattern_data
            )

    ## Recursion iterator.
    elif is_iterable(data, (str, bytes)):
        for element in data:
            _flattern_data = flatten(
                element,
                _flattern_data = _flattern_data
            )

    ## Other.
    else:
        _flattern_data.append(data)

    return _flattern_data


@overload
def split(data: Iterable[T], share: int) -> list[list[T]]: ...

@overload
def split(data: Iterable[T], *, bin_size: int) -> list[list[T]]: ...

def split(data: Iterable[T], share: int | None = None, bin_size: int | None = None) -> list[list[T]]:
    """
    Split data into multiple data.

    Parameters
    ----------
    data : Data.
    share : Number of split share.
    bin_size : Size of each bin.

    Returns
    -------
    Split data.
    """

    # Check parameter.
    check_least_one(share, bin_size)
    check_most_one(share, bin_size)

    # Handle parameter.
    data = list(data)

    # Split.
    data_len = len(data)
    _data = []
    _data_len = 0

    ## by number of share.
    if share is not None:
        average = data_len / share
        for n in range(share):
            bin_size = int(average * (n + 1)) - int(average * n)
            _data = data[_data_len:_data_len + bin_size]
            _data.append(_data)
            _data_len += bin_size

    ## By size of bin.
    elif bin_size is not None:
        while True:
            _data = data[_data_len:_data_len + bin_size]
            _data.append(_data)
            _data_len += bin_size
            if _data_len > data_len:
                break

    return _data


def unique(data: Iterable[T]) -> list[T]:
    """
    De duplication of data.

    Parameters
    ----------
    data : Data.

    Returns
    -------
    List after de duplication.
    """

    # Handle parameter.
    data = tuple(data)

    # Delete duplicate.
    data_unique = list(set(data))
    data_unique.sort(key=data.index)
    return data_unique


def in_arrs(ojb: Any, *arrs: Iterable, mode: Literal['or', 'and'] = 'or') -> bool:
    """
    Judge whether the one object is in multiple arrays.

    Parameters
    ----------
    obj : One object.
    arrs : Multiple arrays.
    mode : Judge mode.
        - `Literal['or']`: Judge whether the in a certain array.
        - `Literal['and']`: Judge whether the in all arrays.

    Returns
    -------
    Judge result.
    """

    # Judge.
    match mode:

        ## Or.
        case 'or':
            for arr in arrs:
                if ojb in arr:
                    return True

            return False

        ## And.
        case 'and':
            for arr in arrs:
                if ojb not in arr:
                    return False

            return True


def objs_in(arr: Iterable, *objs: Any, mode: Literal['or', 'and'] = 'or') -> bool:
    """
    Judge whether the multiple objects is in one array.

    Parameters
    ----------
    arr : One array.
    objs : Multiple objects.
    mode : Judge mode.
        - `Literal['or']`: Judge whether contain a certain object.
        - `Literal['and']`: Judge whether contain all objects.

    Returns
    -------
    Judge result.
    """

    # Judge.
    match mode:

        ## Or.
        case 'or':
            for obj in objs:
                if obj in arr:
                    return True

            return False

        ## And.
        case 'and':
            for obj in objs:
                if obj not in arr:
                    return False

            return True


@overload
def chain(*iterables: dict[KT, VT]) -> ChainMap[KT, VT]: ...

@overload
def chain(*iterables: Iterable[T]) -> IChain[T]: ...

def chain(*iterables: dict[KT, VT] | Iterable[T]) -> ChainMap[KT, VT] | IChain[T]:
    """
    Connect multiple iterables.

    Parameters
    ----------
    iterables : Multiple iterables.
        - `dict`: Connect to chain mapping.
        - `Iterable`: Connect to chain.

    Returns
    -------
    Chain instance.
    """

    # Dict.
    if all(
        [
            isinstance(iterable, dict)
            for iterable in iterables
        ]
    ):
        data = ChainMap(*iterables)

    # Other.
    else:
        data = IChain(*iterables)

    return data


def default_dict(default: T = null, data: dict[KT, VT] | None = None) -> Defaultdict[KT, VT | T]:
    """
    Set `dict` instance, default value when key does not exist.

    Parameters
    ----------
    default : Default value.
        - `Literal[null]`: Nest function self.
        - `Callable`: Use call return value.
    data : `dict` instance.
        - `None`: Empty `dict`.
    """

    # Handle parameter.

    ## Null.
    if default == null:
        default_factory = default_dict

    ## Callable.
    elif callable(default):
        default_factory = default

    ## Not callable.
    else:
        default_factory = lambda : default

    if data is None:
        data = {}

    # Instance.
    dict_set = Defaultdict(default_factory, data)

    return dict_set


class FunctionGenerator(Base):
    """
    Function generator type.

    Examples
    --------
    >>> func = lambda arg1, arg2: arg1 + arg2
    >>> fgenerator = FunctionGenerator(func, 10)
    >>> fgenerator.add(1)
    >>> fgenerator.add(2)
    >>> list(fgenerator)
    [11, 12]
    """


    def __init__(
        self,
        func: Callable,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        func : Generate function.
        args : Function default position arguments.
        kwargs : Function default keyword arguments.
        """

        # Set attribute.
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.params: list[tuple[tuple, dict]] = []
        self.generator = self._generator()


    def _generator(self) -> Generator[Any, Any, None]:
        """
        Create generator.

        Parameters
        ----------
        Generator.
        """

        # Loop.
        while True:

            # Break.
            if self.params == []:
                break

            # Generate.
            args, kwargs = self.params.pop(0)
            result = self.func(*args, **kwargs)

            # Return.
            yield result


    def add(
        self,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """
        Add once generate.

        Parameters
        ----------
        args : Function position arguments.
        kwargs : Function keyword arguments.
        """

        # Set parameter.
        func_args = (
            *self.args,
            *args
        )
        func_kwargs = {
            **self.kwargs,
            **kwargs
        }

        # Add.
        item = (
            func_args,
            func_kwargs
        )
        self.params.append(item)


    __call__ = add


    def __next__(self) -> Any:
        """
        Generate once from generator.

        Returns
        -------
        Generate value.
        """

        # Generate.
        result = next(self.generator)

        return result


    def __iter__(self) -> Generator[Any, Any, None]:
        """
        Iterating generator.
        """

        # Iterating.
        return self.generator
