

import User
import pprint

pp = pprint.PrettyPrinter(indent=4)
DEBUG = False



def Debug(s):
    # pp.pprint(s)
    pass

def Error(s):
    pp.pprint(s)
    pass

def Info(s):
    pp.pprint(s)
    pass

User.grabUserPages('kakabomba')