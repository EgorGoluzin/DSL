from argparse import ArgumentParser


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-j", "--json", dest="jsonFile", required=True)
    parser.add_argument("-d", "--dir", dest="directory", required=True)
    return parser.parse_args()