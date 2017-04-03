from itertools import groupby
import os
import shlex
import sys

from flint.fortlines import FortLines
from flint.program import Program


class Source(object):
    def __init__(self):
        self.project = None     # Link to parent
        self.path = None
        self.abspath = None     # Use property to get root from project

        # Source attributes
        self.programs = []
        self.modules = []
        self.subroutines = []
        self.functions = []

        # Diagnostics
        self.linewidths = []
        self.whitespace = []

    def parse(self, path):
        # Resolve filepaths
        if os.path.isabs(path):
            self.abspath = path

            if self.project:
                root_path = self.project.path
                plen = len(root_path)
                assert path[:plen] == self.project.path
                self.abspath = path[plen:]
            else:
                self.path = self.abspath

        else:
            self.path = path
            if self.project:
                # TODO: Probably need a root path consistency check here...
                self.abspath = os.path.join(self.project.path, path)
            else:
                self.abspath = os.path.abspath(path)

        # Create tokenizer
        with open(self.path) as srcfile:
            f90lex = shlex.shlex(srcfile, punctuation_chars='*/=<>:')
            f90lex.commenters = ''
            f90lex.whitespace = ''

            # shlex mangles wordchars when punctuation_chars is used...
            t = f90lex.wordchars.maketrans(dict.fromkeys('~-.?'))
            f90lex.wordchars = f90lex.wordchars.translate(t)

            tokens = list(f90lex)

        # Tokenized lines
        # NOTE: Try to do this with list comprehensions
        raw_lines = []
        start = end = 0
        while True:
            try:
                end = start + tokens[start:].index('\n')
                raw_lines.append(tokens[start:end])
                start = end + 1
            except ValueError:
                break

        # Line cleanup

        src_lines = []
        for line in raw_lines:
            # Record line widths
            width = len(''.join(line))
            self.linewidths.append(width)

            # Strip comments
            if '!' in line:
                line = line[:line.index('!')]
                commented = True
            else:
                commented = False

            # Merge unhandled tokens
            # TODO  m(-_-)m
            #   1. Operators
            #   2. Boolean values
            #   3. Floating point values

            # Track whitespace between tokens
            # TODO
            #if line == [] or line[0] != ' ':
            #    ws_count = [0]
            #else:
            #    ws_count = []

            #ws_count.extend([len(list(g))
            #                 for k, g in groupby(line, lambda x: x == ' ')
            #                 if k])

            #self.whitespace.append(ws_count)

            # Remove whitespace
            tokenized_line = [tok for tok in line if not tok == ' ']
            if tokenized_line:
                src_lines.append(tokenized_line)

        for line in src_lines:
            print(line)

        ilines = FortLines(src_lines)
        for line in ilines:
            if line[0].lower() == 'program':
                # Testing
                print(' '.join(line))

                # TODO: Validate prog_name (need to deal with whitespace)
                prog_name = None

                prog = Program(prog_name)
                prog.parse(ilines)

                self.programs.append(prog)
            else:
                # Unresolved line
                print('XXX: {}'.format(' '.join(line)))