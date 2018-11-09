import re

def extract(x):
    y = re.findall("no=([^&]+)", x)
    a = re.findall("wer=([^&]+)", x)
    b = a[0]
    z = y[0]
    z = int(z)
    e = [z, b]

    return e
