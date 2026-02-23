from SETTINGS import *
from jPOD import *


def main():
    offs = processPOD(podfile)
    outputFile = open("output.txt", 'w')
    outputFile.write(str(offs))
    outputFile.close()
    offs2 = processPOD(animpodfile)
    outputFile2 = open("outputanim.txt", 'w')
    outputFile2.write(str(offs2))
    outputFile2.close()

if __name__ == "__main__":
    main()
