def json(data, dataList):
	for i in dataList:
		if i not in data:
			return False
	return True

def isPresent(db, table, attribute, value):
	return bool(db.session.query(table).filter(getattr(table, attribute) == value).first())