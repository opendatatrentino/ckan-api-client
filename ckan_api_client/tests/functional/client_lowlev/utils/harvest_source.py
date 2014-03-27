"""
Utilities for real-case harvesting scenario
"""

from collections import Mapping
import os
import json


HARVEST_SOURCE_NAME = 'dummy-harvest-source'


class HarvestSource(Mapping):
    """
    Provides dict-like access to harvest sources
    """

    # Default harvest source..
    source_name = HARVEST_SOURCE_NAME

    def __init__(self, base_dir, day):
        """
        :param day:
            The day from which to get data.
            Full name, like 'day-00', 'day-01', ..
        """
        self.base_dir = base_dir
        self.day = day

    def __getitem__(self, name):
        if name not in self.__iter__():
            raise KeyError("No such object type: {0!r}".format(name))
        return HarvestSourceCollection(self, name)

    def __iter__(self):
        """List object types"""

        folder = os.path.join(self.base_dir, self.day)
        for name in os.listdir(folder):
            # Skip hidden files
            if name.startswith('.'):
                continue

            # Skip non-directories
            path = os.path.join(folder, name)
            if not os.path.isdir(path):
                continue

            yield name

    def __len__(self):
        return len(list(self.__iter__()))


class HarvestSourceCollection(Mapping):
    """
    Wrapper around a "collection" of items in the "harvest source".
    """

    def __init__(self, source, name):
        self.source = source
        self.name = name

    def __getitem__(self, name):
        if name not in self.__iter__():
            raise KeyError("There is no object of type={0!r} id={1!r}"
                           .format(self.name, name))
        folder = os.path.join(self.source.base_dir, self.source.day, self.name)
        path = os.path.join(folder, name)

        with open(path, 'r') as f:
            data = json.load(f)
            if 'id' in data:
                if data['id'] != name:
                    raise ValueError("Mismatching dataset id -- bad data?")
            data['id'] = name  # make sure we pass it back

        return data

    def __iter__(self):
        """List object ids"""

        folder = os.path.join(self.source.base_dir, self.source.day, self.name)
        for name in os.listdir(folder):
            # Skip hidden files
            if name.startswith('.'):
                continue

            # Skip non-files
            path = os.path.join(folder, name)
            if not os.path.isfile(path):
                continue

            yield name

    def __len__(self):
        return len(list(self.__iter__()))
