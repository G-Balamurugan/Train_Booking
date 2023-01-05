def json(data, datalist):
    # print (data, datalist)
    for i in datalist:
        print(i)
        if i not in data:
            print("hello")
            return False
    return True

def isPresent(db, table, attribute, value):
	return bool(db.session.query(table).filter(getattr(table, attribute) == value).first())