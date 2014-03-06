from collections import namedtuple, Mapping, Sequence


IDPair = namedtuple('IDPair', ['source_id', 'ckan_id'])


class SuppressExceptionIf(object):
    def __init__(self, cond):
        self.cond = cond

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value is None:
            return
        if callable(self.cond):
            # If the callable returns True, exception
            # will be suppressed
            return self.cond(exc_value)
        return self.cond


class IDMap(object):
    """
    Two-way hashmap to map source ids to ckan ids
    and the other way back.
    """

    def __init__(self):
        self._source_to_ckan = {}
        self._ckan_to_source = {}

    def to_ckan(self, source_id):
        return self._source_to_ckan[source_id]

    def to_source(self, ckan_id):
        return self._ckan_to_source[ckan_id]

    def add(self, pair):
        ## Check both directions first..
        if pair.source_id in self._source_to_ckan:
            if self._source_to_ckan[pair.source_id] != pair.ckan_id:
                raise ValueError("Mismatching information")

        if pair.ckan_id in self._ckan_to_source:
            if self._ckan_to_source[pair.ckan_id] != pair.source_id:
                raise ValueError("Mismatching information")

        self._source_to_ckan[pair.source_id] = pair.ckan_id
        self._ckan_to_source[pair.ckan_id] = pair.source_id

    def remove(self, pair):
        ## Check both directions first..
        if pair.source_id in self._source_to_ckan:
            if self._source_to_ckan[pair.source_id] != pair.ckan_id:
                raise ValueError("Mismatching information")

        if pair.ckan_id in self._ckan_to_source:
            if self._ckan_to_source[pair.ckan_id] != pair.source_id:
                raise ValueError("Mismatching information")

        del self._source_to_ckan[pair.source_id]
        del self._ckan_to_source[pair.ckan_id]


##------------------------------------------------------------
## Frozen objects, mainly used while running tests,
## to make sure certain objects are left untouched.
##------------------------------------------------------------

class FrozenDict(Mapping):
    def __init__(self, data):
        self.__wrapped = data

    def __getitem__(self, name):
        return freeze(self.__wrapped[name])

    def __iter__(self):
        return iter(self.__wrapped)

    def __len__(self):
        return len(self.__wrapped)


class FrozenSequence(Sequence):
    def __init__(self, data):
        self.__wrapped = data

    def __getitem__(self, name):
        return freeze(self.__wrapped[name])

    def __len__(self):
        return len(self.__wrapped)


class FrozenList(FrozenSequence):
    pass


class FrozenTuple(FrozenSequence):
    pass


def freeze(obj):
    if obj is None:
        return None
    if isinstance(obj, (basestring, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return FrozenDict(obj)
    if isinstance(obj, list):
        return FrozenList(obj)
    if isinstance(obj, tuple):
        return FrozenTuple(obj)
    raise TypeError("I don't know how to freeze this!")
