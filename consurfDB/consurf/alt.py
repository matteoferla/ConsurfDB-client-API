from __future__ import annotations
from typing import *
from ..residue_type import ResidueDataType
from .base import ConBase


class ConAlt(ConBase):

    @classmethod
    def from_web(cls, code: str, chain: str) -> ConAlt:
        """
        Consurf DB. Two requests.
        """
        self = cls()
        self.fetch(code, chain)
        return self

    @classmethod
    def from_filename(cls, grades_filename: str) -> ConAlt:
        """
        dot grades file.
        """
        self = cls()
        self.read(grades_filename)
        return self

    @classmethod
    def merge(cls, consufers: List[ConAlt]) -> ConAlt:
        """
        Merging into one.
        """
        self = cls()
        # shoddy chaining.
        self.data: Dict[str, ResidueDataType] = {key: values for cs in consufers  # noqa
                                                 for key, values in cs.data.items()}
        return self
