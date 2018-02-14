import namlat.updates as nup
#import copy
import logging

logger = logging.getLogger(__name__)


def _convert_to_edit_object(v, parent=None, key=None):
    if not (key is None or isinstance(key, str) or isinstance(key, int)
            or isinstance(key, float) or isinstance(key, bool)):
        raise ValueError("Unsupported key type")
    if isinstance(v, dict):
        return EditDict(v, parent, key)
    elif isinstance(v, list):
        return EditList(v, parent, key)
    elif v is None or isinstance(v, int) or isinstance(v, float) or isinstance(v, bool) or isinstance(v, str) \
            or isinstance(v, bytes):
        return v
    else:
        raise ValueError("Unsupported value type")

class EditObject(object):
    pass


class EditDict(EditObject):
    def __init__(self, original_dict, parent=None, key=None):
        self.original_dict = original_dict
        self.current_dict = self._fill_edit_dict(original_dict)
        self.parent = parent
        self.key = key
        self.edits = []

    def _fill_edit_dict(self, original_dict):
        current_dict = dict()
        for k,v in original_dict.items():
            current_dict[k] = _convert_to_edit_object(v, self, k)
        return current_dict

    def append_edits(self, edit):
        if self.parent is None:
            self.edits.append(edit)
        else:
            edit.path.insert(0, self.key)
            self.parent.append_edits(edit)

    def __contains__(self, key):
        return self.current_dict.__contains__(key)

    def __delitem__(self, key):
        self.current_dict.__delitem__(key)
        self.append_edits(nup.Edit('del',[], key))

    def __getitem__(self, key):
        return self.current_dict[key]

    def __iter__(self):
        return self.current_dict.__iter__()

    def __len__(self):
        return self.current_dict.__len__()

    def __repr__(self):
        return self.current_dict.__repr__()

    def __setitem__(self, key, value):
        self.current_dict.__setitem__(key, _convert_to_edit_object(value, self, key))
        self.append_edits(nup.Edit('set', [key], value))

    def __str__(self):
        return self.current_dict.__str__()

    def clear(self):
        # self.current_dict.clear()
        # self.append_edits(nup.Edit('clear', []))
        keys = list(self.current_dict.keys())
        for  k in keys:
            self.__delitem__(k)

    def get(self, key):
        return self.current_dict.get(key)

    def items(self):
        return self.current_dict.items()

    def keys(self):
        return self.current_dict.keys()

    def update(self, update_dict):
        for k,v in update_dict.items():
            self.current_dict.__setitem__(k, _convert_to_edit_object(v, self, k))
        self.append_edits(nup.Edit('update', [], update_dict))

    def values(self):
        return self.current_dict.values()

    def deep_copy(self):
        copy = dict()
        for k,v in self.current_dict.items():
            if isinstance(v, EditObject):
                copy[k] = v.deep_copy()
            else:
                copy[k] = v
        return copy


class EditList(EditObject):
    def __init__(self, original_list, parent=None, key=None):
        self.original_list = original_list
        self.current_list = self._fill_edit_list(original_list)
        self.parent = parent
        self.key = key
        self.edits = []

    def _fill_edit_list(self, original_list):
        current_list = list()
        for k in range(len(original_list)):
            v = original_list[k]
            current_list.append(_convert_to_edit_object(v, self, k))
        return current_list

    def append_edits(self, edit):
        if self.parent is None:
            self.edits.append(edit)
        else:
            edit.path.insert(0, self.key)
            self.parent.append_edits(edit)

    def __contains__(self, o):
        return self.current_list.__contains__(o)

    def __delitem__(self, o):
        self.current_list.__delitem__(o)
        self.append_edits(nup.Edit('del', [], o))

    def __getitem__(self, o):
        return self.current_list.__getitem__(o)

    def __iter__(self):
        return self.current_list.__iter__()

    def __len__(self):
        return self.current_list.__len__()

    def __repr__(self):
        return self.current_list.__repr__()

    def __setitem__(self, key, value):
        self.current_list.__setitem__(key, _convert_to_edit_object(value, self, key))
        self.append_edits(nup.Edit('set', [key], value))

    def __str__(self):
        return self.current_list.__str__()

    def append(self, value):
        self.current_list.append(_convert_to_edit_object(value, self, len(self.current_list)))
        self.append_edits(nup.Edit('append', [], value))

    def clear(self):
        # self.current_list.clear()
        # self.append_edits(nup.Edit('clear', []))
        l = len(self.current_list)
        for i in range(l):
            self.__delitem__(i)

    def extend(self, other_list):
        for v in other_list:
            self.current_list.append(_convert_to_edit_object(v, self, len(self.current_list)))
        self.append_edits(nup.Edit('extend', [], other_list))

    def index(self, o):
        return self.current_list.index(o)

    def insert(self, i, v):
        vc = _convert_to_edit_object(v, self, i)
        self.current_list.insert(i, vc)
        self.append_edits(nup.Edit('insert', [i], v))

    def remove(self, o):
        self.__delitem__(self.index(o))

    def deep_copy(self):
        copy = list()
        for v in self.current_list:
            if isinstance(v, EditObject):
                copy.append(v.deep_copy())
            else:
                copy.append(v)
        return copy
