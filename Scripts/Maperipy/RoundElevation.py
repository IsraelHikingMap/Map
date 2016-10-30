def roundEle(e):
    for set in e.tagSets:
        if set.hasTag('ele'):
	    return('('+str(int(round(float(set['ele']),0)))+')')
    return('')
