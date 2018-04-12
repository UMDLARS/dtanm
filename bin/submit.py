#!/usr/bin/python

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
# two arguments: attack, update
    parser.add_argument("op", type=int, help="submit attacks [1] or submit code [2]", choices=[1,2])
    parser.add_argument("--file", "-f", type=str, help="file with ")
