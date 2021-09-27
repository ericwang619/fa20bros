from main import *

# check for duplicate pairings
def test():
    global values
    service = login()
    sheet_range = cell_range('All_Pairs', 'A2', 'AZ')
    values = read_spreadsheet(service, sheet_range)
    bros = {}
    duplicates = []
    for v in values:
        pairs = v[2:]
        bros[v[0]] = []
        for pair in pairs:
            adjusted_pair = pair.split(',')
            for a in adjusted_pair:
                a = a.strip()
                if (a in bros[v[0]] and a != 'n/a'):
                    duplicates.append((v[0], a))
                else:
                    bros[v[0]].append(a)
    print(duplicates)


if __name__=='__main__':
    test()
