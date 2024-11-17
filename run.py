#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import parser
from os.path import join, dirname
from dotenv import load_dotenv


def main():
    args = arg_parser()

    if args.env is not None:
        dotenv_path = join(dirname(__file__), args.env)
        load_dotenv(dotenv_path)

    answer = parser.summary(args)
    print(answer)

def arg_parser():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--env', type=str, help='Path to the .env file')
    parser.add_argument('--pdf', type=str, help='Path to the PDF file')
    parser.add_argument('--pdf-url', type=str, help='URL to the PDF file')
    parser.add_argument('--url', type=str, help='URL to the HTML file')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main()