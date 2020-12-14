from main import *

if __name__=='__main__':
    service = login()
    sheet_range = cell_range('All_Pairs', 'A3', 'AZ')
    values = read_spreadsheet(service, sheet_range)
    bros = {}
    dups = []
    for v in values:
        pairs = v[2:]
        bros[v[0]] = []
        for p in pairs:
            if (p in bros[v[0]] and p != 'n/a'):
                raise Exception("qq")
            else:
                bros[v[0]].append(p)
