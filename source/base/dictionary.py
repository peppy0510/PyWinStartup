# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import collections.abc
import copy
import json
import re
import ujson

from collections import namedtuple


def merge_dict(*args, add_keys=True, append_list=False):
    assert len(args) >= 2, 'merge_dict requires at least two dicts to merge'
    rtn_dct = args[0].copy()
    merge_dicts = args[1:]
    for merge_dct in merge_dicts:
        if add_keys is False:
            merge_dct = {key: merge_dct[key] for key in set(rtn_dct).intersection(set(merge_dct))}
        for k, v in merge_dct.items():
            if not rtn_dct.get(k):
                rtn_dct[k] = v
            elif k in rtn_dct and type(v) != type(rtn_dct[k]):  # noqa
                raise TypeError(('''Overlapping keys exist with different types: '''
                                 f'''original is {type(rtn_dct[k])}, new value is {type(v)}'''))
            elif isinstance(rtn_dct[k], dict) and isinstance(merge_dct[k], collections.abc.Mapping):
                rtn_dct[k] = merge_dict(rtn_dct[k], merge_dct[k], add_keys=add_keys)
            elif append_list and isinstance(v, list):
                for list_value in v:
                    if list_value not in rtn_dct[k]:
                        rtn_dct[k].append(list_value)
            else:
                rtn_dct[k] = v
    return rtn_dct


def load_commented_json(path_or_json):
    # import time
    # tic = time.time()

    path = str(path_or_json)

    if '{' not in path and '[' not in path:
        with open(path, 'rb') as file:
            path_or_json = file.read().decode('utf-8')

    lines = path_or_json.split('\n')

    for i in range(len(lines) - 1, -1, -1):
        lines[i] = re.sub(r'^([\s\t]{0,})//([\w\W]{0,})$', r'', lines[i])
        lines[i] = re.sub(r'([\s]{0,})$', r'', lines[i])
        if not lines[i].strip():
            lines.pop(i)

    has_bracket = False
    for i in range(len(lines) - 1):
        line = lines[i + 1].strip()
        if len(line):
            has_bracket = line[0] in ('}', ']')
        if lines[i].strip().endswith(',') and has_bracket:
            lines[i] = re.sub(r'(,)([\s\t]{0,}){0,}$', r'', lines[i])

    data = '\n'.join(lines)

    # with open(path, 'rb') as file:
    #     lines = file.read().decode('utf-8').split('\n')
    #     data = '\n'.join([v for v in lines if not v.strip().startswith('//')])

    try:
        data = ujson.loads(data)
    except ValueError:
        print(path_or_json)
        # print(traceback.format_exc())
        # print(error)
        raise
    # print(time.time() - tic)
    return data


class dictobject(object):

    def __init__(self, *args, **kwargs):
        for arg in args:
            self.set_dict(arg)
        self.set_dict(kwargs)

    def get(self, *args, **kwargs):
        return self.__dict__.get(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self.__dict__.set(*args, **kwargs)

    def items(self):
        return self.__dict__.items()

    def values(self):
        return self.__dict__.values()

    def keys(self):
        return self.__dict__.keys()

    def get_dict(self, sort_keys=True, recursive=True):
        '''
        dtruct to dict.
        ex) x.get_dict()
        '''
        def struct_to_dict(data, recursive=True):
            if not isinstance(data, dictobject):
                return data
            result = dict()
            for key in data.keys():
                result[key] = eval(f'data.{key}')
                if recursive and isinstance(result[key], dictobject):
                    result[key] = struct_to_dict(result[key], recursive=recursive)
                elif recursive and isinstance(result[key], list):
                    result[key] = [struct_to_dict(v, recursive=recursive)
                                   for v in result[key]]
                elif recursive and isinstance(result[key], tuple):
                    result[key] = tuple([struct_to_dict(v, recursive=recursive)
                                         for v in result[key]])
            return result

        return struct_to_dict(self, recursive)

    def set_dict(self, data, recursive=True, deepcopy=False):
        '''
        dict to dtruct.
        ex) x.set_dict({'a': 1, 'b': {'c': 2}})
        '''

        def dict_to_struct(data, recursive=True):

            if isinstance(data, int):
                return data

            if isinstance(data, float):
                return data

            if isinstance(data, str):
                return data

            if isinstance(data, list):
                return [dict_to_struct(v, recursive=recursive) for v in data]

            if isinstance(data, tuple):
                return tuple([dict_to_struct(v, recursive=recursive) for v in data])

            if isinstance(data, dictobject):
                return data

            # assume data is dict
            result = dictobject()
            for key in data.keys():
                if recursive and isinstance(data[key], dict):
                    data[key] = dict_to_struct(data[key],
                                               recursive=recursive)
                elif recursive and isinstance(data[key], list):
                    data[key] = [dict_to_struct(v, recursive=recursive)
                                 for v in data[key]]
                elif recursive and isinstance(data[key], tuple):
                    data[key] = tuple([dict_to_struct(v, recursive=recursive)
                                       for v in data[key]])
                setattr(result, key, data[key])
            return result

        if deepcopy:
            data = copy.deepcopy(data)

        for key in data.keys():
            if recursive and isinstance(data[key], dict):
                data[key] = dict_to_struct(data[key], recursive=recursive)
            setattr(self, key, data[key])


def json_to_object(data):

    def json_object_hook(_data):
        # for k in _data.keys():
        #     if k == 'path':
        #         _data[k] = str(Path(PROJECT_DIR).joinpath(_data[k]).resolve())
        return namedtuple('SETTINGS', _data.keys())(*_data.values())

    return json.loads(data, object_hook=json_object_hook)


def json_to_dictobject(data):

    def json_dictobject_hook(_data):
        return dictobject(_data)

    return json.loads(data, object_hook=json_dictobject_hook)
