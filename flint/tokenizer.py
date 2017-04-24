class Tokenizer(object):

    # I don't use these two
    special_chars = ' =+-*/\\()[]{},.:;!"%&~<>?\'`|$#@'     # Table 3.1
    lexical_tokens = '=+-*/()[],.:;%&<>'                    # Meaningful?

    # I only use this one
    punctuation = '=+-*/\\()[]{},:;%&~<>?`|$#@'    # Unhandled Table 3.1 tokens

    def __init__(self):
        self.characters = None
        self.prior_char = None
        self.char = None

        self.prior_delim = None

    def parse(self, line):
        """Tokenize a line of Fortran source."""

        tokens = []

        word = ''
        self.characters = iter(line)
        self.char = next(self.characters)

        while self.char != '\n':
            if self.char in ' \t':
                while self.char in ' \t':
                    word += self.char
                    self.char = next(self.characters)

            elif self.char in '"\'' or self.prior_delim:
                word = self.parse_string()
                if (self.prior_char, self.char) == ('&', '\n'):
                    tokens.append(word)
                    word = self.prior_char

            elif self.char.isalpha() or self.char == '_':
                # NOTE: Variables cannot start with underscore
                #       But keep for now to accommodate preprocessed tags
                while self.char.isalnum() or self.char == '_':
                    word += self.char
                    self.char = next(self.characters)

            elif self.char.isdigit():
                word = self.parse_numeric()

            elif self.char in ('!', '#'):
                while self.char != '\n':
                    word += self.char
                    self.char = next(self.characters)

            elif self.char == '.':
                self.char = next(self.characters)
                if self.char.isdigit():
                    frac = self.parse_numeric()
                    word = '.' + frac
                else:
                    word = '.'
                    while self.char.isalpha():
                        word += self.char
                        self.char = next(self.characters)
                    if self.char == '.':
                        word += self.char
                        self.char = next(self.characters)

            elif self.char in Tokenizer.punctuation:
                # TODO: Check for valid two-character tokens
                word += self.char
                self.char = next(self.characters)

            else:
                # This should never happen
                raise ValueError

            tokens.append(word)
            word = ''

        return tokens

    def parse_string(self):
        word = ''

        if self.prior_delim:
            delim = self.prior_delim
            self.prior_delim = None
        else:
            delim = self.char
            word += self.char
            self.prior_char, self.char = self.char, next(self.characters)

        next_delim = None
        while True:
            if self.char == '&':
                self.prior_char, self.char = self.char, next(self.characters)
                if self.char == '\n':
                    next_delim = delim
                    break
                else:
                    word += '&'
            elif self.char == delim:
                # Check for escaped delimiters
                self.prior_char, self.char = self.char, next(self.characters)
                if self.char == delim:
                    word += 2 * delim
                    self.prior_char, self.char = (self.char,
                                                  next(self.characters))
                else:
                    word += delim
                    break
            else:
                word += self.char
                self.prior_char, self.char = self.char, next(self.characters)

        self.prior_delim = next_delim

        return word

    def parse_numeric(self):
        word = ''
        frac = False

        while self.char.isdigit() or (self.char == '.' and not frac):
            # Only allow one decimal point
            if self.char == '.':
                frac = True
            word += self.char
            self.char = next(self.characters)

        # Check for float exponent
        if self.char in 'eEdD':
            word += self.char
            self.char = next(self.characters)
            if self.char in '+-':
                word += self.char
                self.char = next(self.characters)
            while self.char.isdigit():
                word += self.char
                self.char = next(self.characters)

        if self.char == '_':
            word += self.char
            self.char = next(self.characters)
            named = self.char.isalpha()

            while (self.char.isdigit() or
                   (self.char.isalpha() or self.char == '_' and named)):
                word += self.char
                self.char = next(self.characters)

        return word
