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

def check_str_isInt(input_num):
    try:
        float(input_num)
    except ValueError:
        return False
    else:
        return float(input_num).is_integer()