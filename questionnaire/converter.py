
def converter(cat, i):

    if cat == 'Normal':
        pass
    elif cat == 'Indoors':
        i += 12
    elif cat == 'Corridor':
        i += 32
    elif cat == 'Outdoors':
        i += 45
    elif cat == 'Quick':
        i += 64

    return i

    # 功能： 把相對題號變成絕對題號
    # 輸入： 1. cat ：類別
    #       2.   i ：相對題號
    # 輸出：絕對題號
