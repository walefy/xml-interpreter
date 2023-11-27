def get_nested_value(list_key: tuple[str, ...], entry_dict: dict):
    response = entry_dict.copy()

    for key in list_key:
        if isinstance(response, dict):
            response = response.get(key)

            if response is None:
                raise ValueError(f'Key {key} not found')
        else:
            raise ValueError(f'Key {key} not found')

    return response
