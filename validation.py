def validate_date(date):
    try:
        day = int(date.split(".")[0])
        month = int(date.split(".")[1])
        year = int(date.split(".")[2])
    except:
        return False

    if day>31:
        return False
    if month>12:
        return False
    if month == 2 and year % 4 !=0 and day>28:
        return False
    if month == 2 and day>29:
        return False
    if month in [4,6,9,11] and day>30:
        return False 
    return True