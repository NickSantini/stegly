import os
import argparse
from pathlib import Path

# TODO
# only consider image files

ALGORITHM_CHOCIES = ['dct', 'cdct', 'edct', 'picky', 'mbdct']

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--directory", required=True, type=str.lower)
parser.add_argument("-t", "--type", required=True, choices=ALGORITHM_CHOCIES, type=str.lower)
parser.add_argument("-s", "--secret_message", required=True)
args = parser.parse_args()

folder = Path(args.directory)

for child in folder.iterdir(): os.system("python3 stegly.py -a embed -t " + args.type +  " -s " + args.secret_message +" -i " + str(child))