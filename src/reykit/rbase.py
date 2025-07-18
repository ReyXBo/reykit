# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-07-17 09:46:40
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Base methods.
"""


from typing import Any, Literal, Self, TypeVar, NoReturn, overload
from types import TracebackType
from collections.abc import Callable, Iterable, Mapping
from sys import exc_info as sys_exc_info
from os.path import exists as os_exists
from traceback import format_exc
from warnings import warn as warnings_warn
from traceback import format_stack, extract_stack
from atexit import register as atexit_register
from time import sleep as time_sleep
from inspect import signature as inspect_signature, _ParameterKind, _empty
from varname import VarnameRetrievingError, argname


__all__ = (
    'T',
    'U',
    'V',
    'KT',
    'VT',
    'Base',
    'StaticMeta',
    'ConfigMeta',
    'Singleton',
    'Null',
    'null',
    'BaseError',
    'Exit',
    'Error',
    'throw',
    'warn',
    'catch_exc',
    'check_least_one',
    'check_most_one',
    'check_file_found',
    'check_file_exist',
    'check_response_code',
    'is_class',
    'is_instance',
    'is_iterable',
    'is_table',
    'is_num_str',
    'get_first_notnone',
    'get_stack_text',
    'get_stack_param',
    'get_arg_info',
    'get_name',
    'block',
    'at_exit'
)


# Generic.
T = TypeVar('T') # Any.
U = TypeVar('U') # Any.
V = TypeVar('V') # Any.
KT = TypeVar('KT') # Any dictionary key.
VT = TypeVar('VT') # Any dictionary value.


class Base(object):
    """
    Base type.
    """

    def __getitem__(self, name: str) -> Any:
        """
        Get Attribute.

        Parameters
        ----------
        name : Attribute name.

        Returns
        -------
        Attribute value.
        """

        # Get.
        value = getattr(self, name)

        return value


    def __setitem__(self, name: str, value: Any) -> None:
        """
        Set Attribute.

        Parameters
        ----------
        name : Attribute name.
        value : Attribute value.
        """

        # Set.
        setattr(self, name, value)


    def __delitem__(self, name: str) -> None:
        """
        Delete Attribute.

        Parameters
        ----------
        name : Attribute name.
        """

        # Delete.
        delattr(self, name)


class StaticMeta(Base, type):
    """
    Static meta type.
    """


    def __call__(cls):
        """
        Call method.
        """

        # Throw exception.
        raise TypeError('static class, no instances allowed.')


class ConfigMeta(StaticMeta):
    """
    Config meta type.
    """


    def __getitem__(cls, name: str) -> Any:
        """
        Get item.

        Parameters
        ----------
        name : Item name.

        Returns
        -------
        Item value.
        """

        # Get.
        item = getattr(cls, name)

        return item


    def __setitem__(cls, name: str, value: Any) -> None:
        """
        Set item.

        Parameters
        ----------
        name : Item name.
        """

        # Set.
        setattr(cls, name, value)


class Singleton(Base):
    """
    Singleton type.
    When instantiated, method `__singleton__` will be called only once, and will accept arguments.

    Attributes
    ----------
    _instance : Global singleton instance.
    """

    _instance: Self | None = None


    def __new__(self, *arg: Any, **kwargs: Any) -> Self:
        """
        Build `singleton` instance.
        """

        # Build.
        if self._instance is None:
            self._instance = super().__new__(self)

            ## Singleton method.
            if hasattr(self, "__singleton__"):
                __singleton__: Callable = getattr(self, "__singleton__")
                __singleton__(self, *arg, **kwargs)

        return self._instance


class Null(Singleton):
    """
    Null type.
    """


null = Null()


class BaseError(Base, BaseException):
    """
    Base error type.
    """


class Exit(BaseError):
    """
    Exit type.
    """


class Error(BaseError):
    """
    Error type.
    """


def throw(
    exception: type[BaseException] = AssertionError,
    value: Any = null,
    *values: Any,
    text: str | None = None,
    frame: int = 2
) -> NoReturn:
    """
    Throw exception.

    Parameters
    ----------
    exception : Exception Type.
    value : Exception value.
    values : Exception values.
    text : Exception text.
    frame : Number of code to upper level.
    """

    # Text.
    if text is None:
        if exception.__doc__ is not None:
            text = exception.__doc__.strip()
        if (
            text is None
            or text == ''
        ):
            text = 'use error'
        else:
            text = text[0].lower() + text[1:]

    ## Value.
    if value != null:
        values = (value,) + values

        ### Name.
        name = get_name(value, frame)
        names = (name,)
        if values != ():
            names_values = get_name(values)
            if names_values is not None:
                names += names_values

        ### Convert.
        match exception:
            case TypeError():
                values = [
                    type(value)
                    for value in values
                    if value is not None
                ]
            case TimeoutError():
                values = [
                    int(value)
                    if value % 1 == 0
                    else round(value, 3)
                    for value in values
                    if type(value) == float
                ]
        values = [
            repr(value)
            for value in values
        ]

        ### Join.
        if names == ():
            values_len = len(values)
            text_value = ', '.join(values)
            if values_len == 1:
                text_value = 'value is ' + text_value
            else:
                text_value = 'values is (%s)' % text_value
        else:
            names_values = zip(names, values)
            text_value = ', '.join(
                [
                    'parameter "%s" is %s' % (name, value)
                    for name, value in names_values
                ]
            )
        text += ' %s.' % text_value

    # Throw exception.
    exception = exception(text)
    raise exception


def warn(
    *infos: Any,
    exception: type[BaseException] = UserWarning,
    stacklevel: int = 3
) -> None:
    """
    Throw warning.

    Parameters
    ----------
    infos : Warn informations.
    exception : Exception type.
    stacklevel : Warning code location, number of recursions up the code level.
    """

    # Handle parameter.
    if infos == ():
        infos = 'Warning!'
    elif len(infos) == 1:
        if type(infos[0]) == str:
            infos = infos[0]
        else:
            infos = str(infos[0])
    else:
        infos = str(infos)

    # Throw warning.
    warnings_warn(infos, exception, stacklevel)


def catch_exc(
    title: str | None = None
) -> tuple[str, type[BaseException], BaseException, TracebackType]:
    """
    Catch exception information and print, must used in `except` syntax.

    Parameters
    ----------
    title : Print title.
        - `None`: Not print.
        - `str`: Print and use this title.

    Returns
    -------
    Exception data.
        - `str`: Exception report text.
        - `type[BaseException]`: Exception type.
        - `BaseException`: Exception instance.
        - `TracebackType`: Exception traceback instance.
    """

    # Get parameter.
    exc_report = format_exc()
    exc_report = exc_report.strip()
    exc_type, exc_instance, exc_traceback = sys_exc_info()

    # Print.
    if title is not None:

        ## Import.
        from .rstdout import echo

        ## Execute.
        echo(exc_report, title=title, frame='half')

    return exc_report, exc_type, exc_instance, exc_traceback


@overload
def check_least_one(*values: None) -> NoReturn: ...

@overload
def check_least_one(*values: Any) -> None: ...

def check_least_one(*values: Any) -> None:
    """
    Check that at least one of multiple values is not null, when check fail, then throw exception.

    Parameters
    ----------
    values : Check values.
    """

    # Check.
    for value in values:
        if value is not None:
            return

    # Throw exception.
    vars_name = get_name(values)
    if vars_name is not None:
        vars_name_de_dup = list(set(vars_name))
        vars_name_de_dup.sort(key=vars_name.index)
        vars_name_str = ' ' + ' and '.join([f'"{var_name}"' for var_name in vars_name_de_dup])
    else:
        vars_name_str = ''
    raise TypeError(f'at least one of parameters{vars_name_str} is not None')


def check_most_one(*values: Any) -> None:
    """
    Check that at most one of multiple values is not null, when check fail, then throw exception.

    Parameters
    ----------
    values : Check values.
    """

    # Check.
    exist = False
    for value in values:
        if value is not None:
            if exist is True:

                # Throw exception.
                vars_name = get_name(values)
                if vars_name is not None:
                    vars_name_de_dup = list(set(vars_name))
                    vars_name_de_dup.sort(key=vars_name.index)
                    vars_name_str = ' ' + ' and '.join([f'"{var_name}"' for var_name in vars_name_de_dup])
                else:
                    vars_name_str = ''
                raise TypeError(f'at most one of parameters{vars_name_str} is not None')

            exist = True


def check_file_found(path: str) -> None:
    """
    Check if file path found, if not, throw exception.

    Parameters
    ----------
    path : File path.
    """

    # Check.
    exist = os_exists(path)

    # Throw exception.
    if not exist:
        throw(FileNotFoundError, path)


def check_file_exist(path: str) -> None:
    """
    Check if file path exist, if exist, throw exception.

    Parameters
    ----------
    path : File path.
    """

    # Check.
    exist = os_exists(path)

    # Throw exception.
    if exist:
        throw(FileExistsError, path)


def check_response_code(
    code: int,
    range_: int | Iterable[int] | None = None
) -> bool:
    """
    Check if the response code is in range.

    Parameters
    ----------
    code : Response code.
    range_ : Pass the code range.
        - `None`: Check if is between 200 and 299.
        - `int`: Check if is this value.
        - `Iterable`: Check if is in sequence.

    Returns
    -------
    Check result.
    """

    # Check.
    match range_:
        case None:
            result = code // 100 == 2
        case int():
            result = code == range_
        case _ if hasattr(range_, '__contains__'):
            result = code in range_
        case _:
            throw(TypeError, range_)

    # Throw exception.
    if not result:
        throw(value=code)

    return result


def is_class(obj: Any) -> bool:
    """
    Judge whether it is class.

    Parameters
    ----------
    obj : Judge object.

    Returns
    -------
    Judgment result.
    """

    # Judge.
    judge = isinstance(obj, type)

    return judge


def is_instance(obj: Any) -> bool:
    """
    Judge whether it is instance.

    Parameters
    ----------
    obj : Judge object.

    Returns
    -------
    Judgment result.
    """

    # judge.
    judge = not is_class(obj)

    return judge


def is_iterable(
    obj: Any,
    exclude_types: Iterable[type] | None = None
) -> bool:
    """
    Judge whether it is iterable.

    Parameters
    ----------
    obj : Judge object.
    exclude_types : Non iterative types.

    Returns
    -------
    Judgment result.
    """

    # Judge.
    if (
        hasattr(obj, '__iter__')
        and not (
            exclude_types is not None
            and type(obj) in exclude_types
        )
    ):
        return True

    return False


def is_table(
    obj: Any,
    check_fields: bool = True
) -> bool:
    """
    Judge whether it is `list[dict]` table format and keys and keys sort of the dict are the same.

    Parameters
    ----------
    obj : Judge object.
    check_fields : Do you want to check the keys and keys sort of the dict are the same.

    Returns
    -------
    Judgment result.
    """

    # Judge.
    if type(obj) != list:
        return False
    for element in obj:
        if type(element) != dict:
            return False

    ## Check fields of table.
    if check_fields:
        keys_strs = [
            ':'.join([str(key) for key in element.keys()])
            for element in obj
        ]
        keys_strs_only = set(keys_strs)
        if len(keys_strs_only) != 1:
            return False

    return True


def is_num_str(
    string: str
) -> bool:
    """
    Judge whether it is number string.

    Parameters
    ----------
    string : String.

    Returns
    -------
    Judgment result.
    """

    # Judge.
    try:
        float(string)
    except (ValueError, TypeError):
        return False

    return True


@overload
def get_first_notnone(*values: None, default: T) -> T: ...

@overload
def get_first_notnone(*values: None) -> NoReturn: ...

@overload
def get_first_notnone(*values: T) -> T: ...

def get_first_notnone(*values: T, default: U = null) -> T | U:
    """
    Get the first value that is not `None`.

    Parameters
    ----------
    values : Check values.
    default : When all are `None`, then return this is value, or throw exception.
        - `Any`: Return this is value.
        - `Literal['exception']`: Throw exception.

    Returns
    -------
    Return first not `None` value, when all are `None`, then return default value.
    """

    # Get value.
    for value in values:
        if value is not None:
            return value

    # Throw exception.
    if default == null:
        vars_name = get_name(values)
        if vars_name is not None:
            vars_name_de_dup = list(set(vars_name))
            vars_name_de_dup.sort(key=vars_name.index)
            vars_name_str = ' ' + ' and '.join([f'"{var_name}"' for var_name in vars_name_de_dup])
        else:
            vars_name_str = ''
        text = f'at least one of parameters{vars_name_str} is not None'
        throw(ValueError, text=text)

    return default


def get_stack_text(format_: Literal['plain', 'full'] = 'plain', limit: int = 2) -> str:
    """
    Get code stack text.

    Parameters
    ----------
    format_ : Stack text format.
        - `Literal['plain']`: Floor stack position.
        - `Literal['full']`: Full stack information.
    limit : Stack limit level.

    Returns
    -------
    Code stack text.
    """

    # Get.
    match format_:

        ## Plain.
        case 'plain':
            limit += 1
            stacks = format_stack(limit=limit)

            ### Check.
            if len(stacks) != limit:
                throw(value=limit)

            ### Convert.
            text = stacks[0]
            index_end = text.find(', in ')
            text = text[2:index_end]

        ## Full.
        case 'full':
            stacks = format_stack()
            index_limit = len(stacks) - limit
            stacks = stacks[:index_limit]

            ### Check.
            if len(stacks) == 0:
                throw(value=limit)

            ### Convert.
            stacks = [
                stack[2:].replace('\n  ', '\n', 1)
                for stack in stacks
            ]
            text = ''.join(stacks)
            text = text[:-1]

        ## Throw exception.
        case _:
            throw(ValueError, format_)

    return text


@overload
def get_stack_param(format_: Literal['floor'] = 'floor', limit: int = 2) -> dict: ...

@overload
def get_stack_param(format_: Literal['full'], limit: int = 2) -> list[dict]: ...

def get_stack_param(format_: Literal['floor', 'full'] = 'floor', limit: int = 2) -> dict | list[dict]:
    """
    Get code stack parameters.

    Parameters
    ----------
    format_ : Stack parameters format.
        - `Literal['floor']`: Floor stack parameters.
        - `Literal['full']`: Full stack parameters.
    limit : Stack limit level.

    Returns
    -------
    Code stack parameters.
    """

    # Get.
    stacks = extract_stack()
    index_limit = len(stacks) - limit
    stacks = stacks[:index_limit]

    # Check.
    if len(stacks) == 0:
        throw(value=limit)

    # Convert.
    match format_:

        ## Floor.
        case 'floor':
            stack = stacks[-1]
            params = {
                'filename': stack.filename,
                'lineno': stack.lineno,
                'name': stack.name,
                'line': stack.line
            }

        ## Full.
        case 'full':
            params = [
                {
                    'filename': stack.filename,
                    'lineno': stack.lineno,
                    'name': stack.name,
                    'line': stack.line
                }
                for stack in stacks
            ]

    return params


def get_arg_info(func: Callable) -> list[
    dict[
        Literal['name', 'type', 'annotation', 'default'],
        str | None
    ]
]:
    """
    Get function arguments information.

    Parameters
    ----------
    func : Function.

    Returns
    -------
    Arguments information.
        - `Value of key 'name'`: Argument name.
        - `Value of key 'type'`: Argument bind type.
            `Literal['position_or_keyword']`: Is positional argument or keyword argument.
            `Literal['var_position']`: Is variable length positional argument.
            `Literal['var_keyword']`: Is variable length keyword argument.
            `Literal['only_position']`: Is positional only argument.
            `Literal['only_keyword']`: Is keyword only argument.
        - `Value of key 'annotation'`: Argument annotation.
        - `Value of key 'default'`: Argument default value.
    """

    # Get signature.
    signature = inspect_signature(func)

    # Get information.
    info = [
        {
            'name': name,
            'type': (
                'position_or_keyword'
                if parameter.kind == _ParameterKind.POSITIONAL_OR_KEYWORD
                else 'var_position'
                if parameter.kind == _ParameterKind.VAR_POSITIONAL
                else 'var_keyword'
                if parameter.kind == _ParameterKind.VAR_KEYWORD
                else 'only_position'
                if parameter.kind == _ParameterKind.POSITIONAL_ONLY
                else 'only_keyword'
                if parameter.kind == _ParameterKind.KEYWORD_ONLY
                else None
            ),
            'annotation': parameter.annotation,
            'default': parameter.default
        }
        for name, parameter in signature.parameters.items()
    ]

    # Replace empty.
    for row in info:
        for key, value in row.items():
            if value == _empty:
                row[key] = None

    return info


@overload
def get_name(obj: tuple, frame: int = 2) -> tuple[str, ...] | None: ...

@overload
def get_name(obj: Any, frame: int = 2) -> str | None: ...

def get_name(obj: Any, frame: int = 2) -> str | tuple[str, ...] | None:
    """
    Get name of object or variable.

    Parameters
    ----------
    obj : Object.
        - `tuple`: Variable length position parameter of previous layer.
        - `Any`: Parameter of any layer.
    frame : Number of code to upper level.

    Returns
    -------
    Name or None.
    """

    # Get name using built in method.
    if hasattr(obj, '__name__'):
        name = obj.__name__
        return name

    # Get name using module method.
    name = 'obj'
    for frame_ in range(1, frame + 1):
        if type(name) != str:
            return
        try:
            name = argname(name, frame=frame_)
        except VarnameRetrievingError:
            return
    if type(name) == tuple:
        for element in name:
            if type(element) != str:
                return

    return name


def block() -> None:
    """
    Blocking program, can be double press interrupt to end blocking.
    """

    # Start.
    print('Start blocking.')
    while True:
        try:
            time_sleep(1)
        except KeyboardInterrupt:

            # Confirm.
            try:
                print('Double press interrupt to end blocking.')
                time_sleep(1)

            # End.
            except KeyboardInterrupt:
                print('End blocking.')
                break

            except:
                continue


def at_exit(*contents: str | Callable | tuple[Callable, Iterable, Mapping]) -> list[Callable]:
    """
    At exiting print text or execute function.

    Parameters
    ----------
    contents : execute contents.
        - `str`: Define the print text function and execute it.
        - `Callable`: Execute function.
        - `tuple[Callable, Iterable, Mapping]`: Execute function and position arguments and keyword arguments.

    Returns
    -------
    Execute functions.
    """

    # Register.
    funcs = []
    for content in reversed(contents):
        args = ()
        kwargs = {}
        if type(content) == str:
            func = lambda : print(content)
        elif callable(content):
            func = content
        elif type(content) == tuple:
            func, args, kwargs = content
        funcs.append(func)
        atexit_register(func, *args, **kwargs)
    funcs = list(reversed(funcs))

    return funcs
