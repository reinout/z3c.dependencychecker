import hashlib
from functools import total_ordering

from cached_property import cached_property


@total_ordering
class DottedName:
    def __init__(
        self,
        name,
        file_path=None,
        is_test=False,
    ):
        self.name = name
        self.safe_name = name.lower().replace('-', '_')

        self.file_path = file_path
        self.is_test = is_test

    @classmethod
    def from_requirement(cls, requirement, file_path=None):
        """A requirement in this method's context is a
        pkg_resources.Requirement
        """
        return cls(
            requirement.project_name,
            file_path=file_path,
        )

    @cached_property
    def namespaces(self):
        return self.safe_name.split('.')

    @cached_property
    def is_namespaced(self):
        return bool(len(self.namespaces) - 1)

    def __lt__(self, other):
        if not isinstance(other, DottedName):
            return NotImplemented
        return self.name < other.name

    def __eq__(self, other):
        if not isinstance(other, DottedName):
            return NotImplemented

        return self.safe_name == other.safe_name

    def __repr__(self):
        return f'<DottedName {self.name}>'

    def __hash__(self):
        digest = hashlib.sha256(self.safe_name.encode()).hexdigest()
        return int(digest, 16) % 10**8

    def __contains__(self, item):
        """Check if self is in item or the other way around

        As we can never know which one is actually the requirement/pypi name
        and which one the import, check if one fits inside the other.

        So ``x in s`` and ``s in x`` should return the same in this
        implementation.
        """
        if not isinstance(item, DottedName):
            return False

        if self.safe_name == item.safe_name:
            return True

        # note that zip makes two different sized iterables have the same size
        # i.e. [1,2,3] and [4,5,6,7,8] will only loop through [1,4] [2,5]
        # and [3,6]. The other elements (7 and 8) will be totally ignored.
        # That's a nice trick to ensure that all the namespace is shared.
        for part1, part2 in zip(self.namespaces, item.namespaces):
            if part1 != part2:
                return False

        return True
