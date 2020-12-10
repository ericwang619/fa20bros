from main import *

if __name__=='__main__':
    values, service = read_spreadsheet()
    bros = {}
    dups = []
    for v in values:
        pairs = v[2:]
        bros[v[0]] = []
        for p in pairs:
            if (p in bros[v[0]]):
                raise Exception("qq")
            else:
                bros[v[0]].append(p)
