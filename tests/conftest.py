import re

def escape_ansi(string):
    return re.sub(r'\x1b[^m]*m', '', str(string))
