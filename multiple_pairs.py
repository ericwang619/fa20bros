from main import *

if __name__ == '__main__':
    offset = 0  # rotation offsets
    iter = 5   # number of times to run main.py
    if (len(sys.argv) == 2):
        iter = sys.argv[1]
    for i in range(iter):
        main(offset)