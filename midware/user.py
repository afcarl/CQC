from midware.parameter import RecordBase


class User(RecordBase):
    table = "Staff"
    fields = ("id", "name", "level", "division", "alias1", "alias2")
    upstream_key = None

    @classmethod
    def current(cls, dbifc):
        from getpass import getuser
        ID = getuser()
        if not ID.isdigit():
            ID = "315855"
        try:
            return cls.from_database(ID, dbifc)
        except Exception as E:
            print("E @ User.current:", str(E))
            return None
