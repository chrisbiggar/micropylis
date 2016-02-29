'''
Created on Oct 18, 2015

@author: chris
'''
import argparse
from build import makeTiles
from build import makeToolIcons


def main():
    # process cmd-line for what type of gen
    parser = argparse.ArgumentParser(description='Generate Micropylis Graphics.')
    parser.add_argument('--tiles', action="store_true", help='generate tilesheets')
    parser.add_argument('--toolicons', action="store_true", help='generate toolicon sheet')
    args = parser.parse_args()
    
    if args.tiles:
        makeTiles.make(16, 'res/tiles.rc', 'res/tiles')
        print("Gen Tilesheets Done.")
    if args.toolicons:
        makeToolIcons.make("res/toolicons", 38, 38, 2)
        print("Gen ToolIcons Done.")
    


if __name__ == '__main__':
    main()