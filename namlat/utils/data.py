

def deep_copy(obj):
    if isinstance(obj, dict):
        return deep_copy_dict(obj)
    elif isinstance(obj, list):
        return deep_copy_list(obj)
    raise ValueError("Unsupported object type: "+ str(obj))


def deep_copy_dict(obj):
    copy = dict()
    for k, v in obj.items():
        if isinstance(v, dict):
            copy[k] = deep_copy_dict(v)
        elif isinstance(v, list):
            copy[k] = deep_copy_list(v)
        else:
            copy[k] = v
    return copy


def deep_copy_list(obj):
    copy = list()
    for v in obj:
        if isinstance(v, dict):
            copy.append(deep_copy_dict(v))
        elif isinstance(v, list):
            copy.append(deep_copy_list(v))
        else:
            copy.append(v)
    return copy