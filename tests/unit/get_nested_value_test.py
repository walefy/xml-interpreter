import pytest

from utils import get_nested_value


@pytest.mark.asyncio
async def test_get_nested_value():
    list_key = ('a', 'b', 'c')
    entry_dict = {'a': {'b': {'c': 'test'}}}

    assert get_nested_value(list_key, entry_dict) == 'test'


@pytest.mark.asyncio
async def test_get_nested_value_with_nonexistent_key():
    list_key = ('a', 'b', 'd')
    dict_test = {'a': {'b': {'c': 'cheguei'}}}

    with pytest.raises(ValueError):
        get_nested_value(list_key, dict_test)

    with pytest.raises(ValueError):
        get_nested_value(list_key, {'a': {'b': 'c'}})
