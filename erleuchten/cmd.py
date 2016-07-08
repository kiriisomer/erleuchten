# coding:utf-8

# entry of start an test

import argparse


def main():
    """"""


def create_environment():
    """"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--name')

    parser.add_argument('--one-or-more', nargs='+')l
    param = parser.parse_args()
    print param


def remove_environment():
    """"""


def create_test():
    """"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--name')
    parser.add_argument('--environment_name', nargs='?')
    parser.add_argument('--one-or-more', nargs='+')
    param = parser.parse_args()
    print param


def run_test():
    """"""


def remove_test():
    """"""
