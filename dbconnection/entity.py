"""
Defines various abstract entities present in the database
"""
from types import SimpleNamespace
from dbconnection.interface import DBConnection


class Node(SimpleNamespace):

    def __init__(self, level, children=(), **attributes):
        self.level = level
        self.children = children
        self.__dict__.update(attributes)

    @classmethod
    def query(cls, dbifc: DBConnection, level, ID):
        print("Queried on level:", level)
        return cls(level, name="Buzowaga")
