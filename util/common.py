from dbconnection import DBConnection

_ifc = DBConnection()
_ifc.x("SELECT tasz, name FROM Staff;")

staff = dict(_ifc.c.fetchall())
staff.update({v: k for k, v in staff.items()})
