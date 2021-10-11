from main import *
import sys

if __name__ == '__main__':
    offset = 0  # rotation offsets
    iter = 15   # number of times to run main.py
    if (len(sys.argv) == 2):
        iter = sys.argv[1]
    for i in range(iter):
        main(offset)