#!/usr/bin/env python2
"""
Generates a FASTA file from a set of regions
"""

import os, argparse, sys, subprocess, pysam

__author__ = "Fong Chun Chan <f.chan@achillestx.com>"
__script_examples__="""
Examples:

    Run the template script with some parameters:
        {scriptname} \\
                --input-file input.txt \\
                --output-file output.txt \\
                --some-parameter asdf qwer

    Run the template script with some parameters in a pipe:
        grep 'query' input.txt \\
            | {scriptname} \\
                --some-parameter asdf qwer \\
            | awk '{{print $1}}' \\
            > output.txt

""".format(scriptname = sys.argv[0])

def main(args):
    """
    Main function

    Args:
        args: A list of arguments from the CLI

    Returns:
        None
    """

    # Parse the command line arguments:
    parameters = parse_args(args)

    print "Generating fasta file for given regions..."
    # Input files
    ref = pysam.Fastafile(parameters.fasta_file)
    f = open(parameters.target_bed_file)

    # Output files
    faoutfile = parameters.target_fasta_file
    abdoutfile = parameters.target_abd_file

    wfa = open(faoutfile, 'w')
    wabd = open(abdoutfile, 'w')
    i = f.readline()
    abd = 0
    while i:
        i = f.readline()
        values = i.split("\t")
        if i.startswith("#") or len(values)<3:
            continue
        chrom = values[0]
        start = max(int(values[1]) - parameters.slack, 1)
        end = int(values[2]) + parameters.slack
        header = ">" + chrom + "_" + str(start) + "_" + str(end)
        x = ref.fetch(chrom, start, end)
        length = len(x)
        abd += length
        wfa.write(header + "\n")
        wfa.write(x + "\n")
        wabd.write(str(abd) + "\n")
    f.close()
    wfa.close()
    wabd.close()

def parse_args(args):
    """
    Parse the command line arguments into a dict object.

    The command line parameters should be changed to suit your needs.

    Any parameter-checking should ideally be implemented as argparse 'type'
    parameters. For example:
      * To prevent overwriting of existing output files:
        https://stackoverflow.com/a/16365493
      * To impose valid range of values:
        https://stackoverflow.com/a/25295717

    Args:
        args: Arguments from the CLI

    Returns:
        A dict object with the argument -> value pairs taken from the CLI.
    """

    parser = argparse.ArgumentParser(
        description = __doc__,
        epilog = __script_examples__,
        formatter_class = argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '-v', '--version',
        action = 'version',
        version = '%(prog)s {version}'.format(version = get_version())
    )

    parser.add_argument(
        "--fasta-file",
        help = "The reference FASTA file",
        required = True
    )

    parser.add_argument(
        "--target-bed-file",
        help = "The target bed file",
        required = True
    )

    parser.add_argument(
        "--target-fasta-file",
        help = "The target FASTA file that will be generated",
        required = True
    )

    parser.add_argument(
        "--target-abd-file",
        help = "The target abd file that will be generated",
        required = True
    )

    parser.add_argument(
        "--slack",
        help = "Slack margin of the given boundaries [%(default)s]",
        required = False,
        default = 0
    )

    return parser.parse_args(args)


def get_version():
    """
    Get the version number of the script from its repo/directory

    This function assumes the script is part of a package that is either a git
    repository or has a VERSION file. It first attempts to use 'git describe'
    to identify the version information based on the scripts location on the
    filesystem. If that fails, it searches from the script's directory to the
    filesystem root until it finds a file called "VERSION" and reads its
    contents.

    If no version information is found, it returns "(Unknown version)"
    """
    start_wd = os.getcwd()
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    try:
        version = subprocess.check_output(
                ["git", "describe", "--always", "--tags", "--dirty"],
                stderr = subprocess.STDOUT
            ).strip().decode('utf8')
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        version = None

    while version == None:
        versionFilePath = os.path.join(os.getcwd(), "VERSION")
        if os.path.isfile(versionFilePath):
            with open(versionFilePath) as fh:
                version = fh.read()
        else:
            currentDir = os.getcwd()
            parentDir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

            if currentDir == parentDir:
                break

            os.chdir(parentDir)

    if version == None:
        version = "(Unknown Version)"

    os.chdir(start_wd)
    return version

# If this script has been called directly (and not imported by another), run the
# 'main' function with the command line arguments:
if __name__ == "__main__":
    main(sys.argv[1:])
