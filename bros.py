from main import *
import sys

if __name__== '__main__':
    times = 1
    if (len(sys.argv) > 1):
        times = int(str(sys.argv[1]))

    service = login()
    for i in range(times):
        main()