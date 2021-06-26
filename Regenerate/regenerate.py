#!/usr/bin/python3

import re
import sys
import argparse
import pprint

ASCII_CHARS = list(map(chr, range(32, 127)))
INFINITY = float("inf")

def range_from_to(lower_bound, upper_bound):
    """Generates an inclusive range from lower to upper bound.

    An upper bound of infinity is also supported.
    """
    i = int(lower_bound)
    while i <= upper_bound:
        yield i
        i += 1

def isbackreference(string):
    return re.fullmatch(r".~?\d+", string) is not None


class Tokens:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.group_num = 0

    def __str__(self):
        return str(self.tokens)

    def peek(self):
        return self.tokens[0]

    def pop(self):
        return self.tokens.pop(0)

    def next_group_num(self):
        self.group_num += 1
        return self.group_num


def scan(expr):
    return Tokens(re.findall(r"[$#]~?\d+|\${|\\.|[^\\]", expr + ")"))

def parse(tokens):
    return parse_alternation(tokens)

def parse_alternation(tokens):
    branches = []
    subexpression = parse_concatenation(tokens)
    if tokens.peek() in "|!":
        branches = [tokens.pop()]
        branches.append(subexpression)
        subexpression = parse_alternation(tokens)
        branches.append(subexpression)
    return branches if branches else subexpression

def parse_concatenation(tokens):
    branches = [""]
    subexpression = parse_repetition(tokens)
    while subexpression is not None:
        branches.append(subexpression)
        subexpression = parse_repetition(tokens)
    if len(branches) == 1:
        return None
    elif len(branches) == 2:
        return branches[1]
    else:
        return branches

def parse_repetition(tokens):
    expression = parse_atom(tokens)
    while tokens.peek() in ["*", "+", "?", "{"]:
        repetition_operator = tokens.pop()
        if repetition_operator == "*":
            bounds = ["0", ""]
        elif repetition_operator == "+":
            bounds = ["1", ""]
        elif repetition_operator == "?":
            bounds = ["0", "1"]
        elif repetition_operator == "{":
            lower_bound = parse_numeric_expr(tokens)
            if tokens.peek() == ",":
                tokens.pop()
                upper_bound = parse_numeric_expr(tokens)
            else:
                upper_bound = lower_bound
            tokens.pop()
            bounds = [lower_bound, upper_bound]
        expression = [bounds, expression]
    return expression

def parse_atom(tokens):
    if tokens.peek() == "[":
        return parse_character_class(tokens)
    elif tokens.peek() == "(":
        tokens.pop()
        group_num = tokens.next_group_num()
        subexpression = parse(tokens)
        tokens.pop()
        return ["(", group_num, subexpression]
    elif tokens.peek() == "${":
        tokens.pop()
        numeric_expression = parse_numeric_expr(tokens)
        tokens.pop()
        return ["${", numeric_expression]
    elif tokens.peek() not in "(){}|!+*?":
        return tokens.pop()
    else:
        return None

def parse_character_class(tokens):
    characters = set()
    prev_character = None
    creating_range = False
    negated = False
    tokens.pop()
    if tokens.peek() == "^":
        negated = True
        tokens.pop()
    if tokens.peek() == "]":
        prev_character = tokens.pop()
    while tokens.peek() != "]":
        if creating_range:
            codepoint_range = range(ord(prev_character), 1 + ord(tokens.pop()))
            characters.update(map(chr, codepoint_range))
            creating_range = False
            prev_character = None
        elif tokens.peek() == "-" and prev_character is not None:
            creating_range = True
            tokens.pop()
        else:
            if prev_character is not None:
                characters.add(prev_character)
            prev_character = tokens.pop()
    tokens.pop()
    if creating_range:
        # Class ended with a hyphen, treat it as a literal hyphen
        characters.add("-")
    if prev_character is not None:
        characters.add(prev_character)
    branches = ["|"]
    if not negated:
        branches.extend(char for char in ASCII_CHARS if char in characters)
    else:
        branches.extend(char for char in ASCII_CHARS if char not in characters)
    return branches

def parse_numeric_expr(tokens):
    return parse_addition_expr(tokens)

def parse_addition_expr(tokens):
    expression = parse_multiplication_expr(tokens)
    while tokens.peek() in ["+", "-"]:
        operator = tokens.pop()
        rhs = parse_multiplication_expr(tokens)
        expression = [operator, expression, rhs]
    return expression

def parse_multiplication_expr(tokens):
    expression = parse_negation_expr(tokens)
    while tokens.peek() in ["*", "/", "%"]:
        operator = tokens.pop()
        rhs = parse_negation_expr(tokens)
        expression = [operator, expression, rhs]
    return expression

def parse_negation_expr(tokens):
    if tokens.peek() == "-":
        operator = tokens.pop()
        rhs = parse_negation_expr(tokens)
        return [operator, rhs]
    else:
        return parse_atomic_expr(tokens)

def parse_atomic_expr(tokens):
    next_token = tokens.peek()
    if next_token.isdigit():
        number = tokens.pop()
        while tokens.peek().isdigit():
            number += tokens.pop()
        return number
    elif isbackreference(next_token):
        return tokens.pop()
    elif next_token in [",", "}"]:
        return ""
    else:
        raise ValueError(f"expected arithmetic expression, got {next_token}")


class MatchState:
    def __init__(self, string="", pos=0, direc=1, offset=0,
                 extend_forward=True, extend_back=True, inputs=None):
        self.string = str(string)
        try:
            self.pos = int(pos)
        except (TypeError, ValueError):
            self.pos = 0
        if direc == 1:
            self.direc = 1
        else:
            self.direc = -1
        try:
            self.offset = int(offset)
        except (TypeError, ValueError):
            self.offset = 0
        self.extend_back = extend_back
        self.extend_forward = extend_forward
        if inputs is None:
            self.inputs = []
        else:
            self.inputs = list(inputs)
        self.groups = {}

    def __str__(self):
        return self.string

    def copy(self):
        new_state = MatchState(self.string, self.pos, self.direc,
                               self.offset, self.extend_back,
                               self.extend_forward, self.inputs)
        new_state.groups = self.groups.copy()
        return new_state


def match_literal_string(string, match_state):
    "Returns a new match state if match succeeds or None if it fails."
    new_state = match_state.copy()
    for char in string:
        index = new_state.pos + new_state.offset
        if 0 <= index < len(new_state.string):
            # Match the character
            if new_state.string[index] == char:
                new_state.pos += new_state.direc
            else:
                return None
        elif index == len(new_state.string):
            # Extend the match string forward if possible
            if match_state.extend_forward:
                new_state.string += char
                new_state.pos += new_state.direc
            else:
                return None
        elif index == -1:
            # Extend the match string backward if possible
            if match_state.extend_back:
                new_state.string = char + new_state.string
                new_state.pos += new_state.direc
            else:
                return None
    return new_state

def eval_numeric(expression, match_state):
    "Evaluates the expression and returns a number."
    if isinstance(expression, int):
        result = expression
    elif isinstance(expression, list):
        operator, *operands = expression
        operands = [eval_numeric(operand, match_state)
                    for operand in operands]
        if None in operands:
            return None
        if operator == "+":
            result = operands[0] + operands[1]
        elif operator == "-":
            if len(operands) == 1:
                result = -operands[0]
            else:
                result = operands[0] - operands[1]
        elif operator == "*":
            result = operands[0] * operands[1]
        elif operator == "/":
            if operands[1] == 0:
                result = None
            else:
                result = operands[0] // operands[1]
        elif operator == "%":
            if operands[1] == 0:
                result = None
            else:
                result = operands[0] % operands[1]
    elif not expression:
        result = 0
    elif expression.isdigit():
        result = int(expression)
    elif isbackreference(expression):
        # Resolve backreference and cast result to integer
        backref_string = resolve_backreference(expression, match_state)
        if backref_string is None:
            result = None
        else:
            try:
                result = int(backref_string)
            except ValueError:
                result = None
    else:
        raise ValueError(f"Can't evaluate {expression} numerically")
    return result

def resolve_backreference(expression, match_state):
    "Returns the referenced quantity as a string or None if it fails."
    if expression[1] == "~":
        # Backreference to one of the inputs
        backref_index = int(expression[2:])
        group_contents = match_state.inputs[backref_index-1]
    else:
        # Backreference to a matched group
        backref_index = int(expression[1:])
        group_contents = match_state.groups.get(backref_index, None)
    if group_contents is None:
        return None
    else:
        if expression[0] == "$":
            # Get the contents of the group/input
            backref_string = group_contents
        elif expression[0] == "#":
            # Get the length of the group/input
            backref_string = str(len(group_contents))
        return backref_string

def match(regex, match_state):
    if regex is None:
        yield match_state
##    elif regex == "~":
##        # TODO: Reverse direction
##        new_state = match_state.copy()
##        new_state.direc = -new_state.direc
##        new_state.extend_forward, new_state.extend_back = (
##            new_state.extend_back, new_state.extend_forward)
##        new_state.pos += new_state.direc
    elif type(regex) is str:
        # Either some kind of escape sequence or a literal character;
        # in any case, match a literal string
        if len(regex) == 1:
            # Match a literal character
            string_to_match = regex
        elif isbackreference(regex):
            # Backreference to an input or a group
            string_to_match = resolve_backreference(regex, match_state)
        elif regex[0] == "\\":
            # Escape sequence
            if regex[1] == "n":
                string_to_match = "\n"
            else:
                string_to_match = regex[1]
        else:
            raise ValueError(f"unrecognized sequence: {regex}")
        if string_to_match is not None:
            new_state = match_literal_string(string_to_match, match_state)
            if new_state is not None:
                yield new_state
    elif regex[0] == "|":
        # Alternation
        for subexpression in regex[1:]:
            for new_state in match(subexpression,
                                   match_state):
                yield new_state
    elif regex[0] == "!":
        # Like alternation, but stop trying other options as soon as
        # we find one that works
        found_match = False
        for subexpression in regex[1:]:
            for new_state in match(subexpression,
                                   match_state):
                yield new_state
                found_match = True
            if found_match:
                break
    elif regex[0] == "":
        # Concatenation; match one at a time, recursively
        if not regex[1:]:
            # Base case: nothing left to match
            yield match_state
        else:
            # Recursive case: match the first item in the alternation,
            # and then match the rest
            first_part = regex[1]
            rest = [""] + regex[2:]
            for first_part_match in match(first_part,
                                          match_state):
                for rest_match in match(rest,
                                        first_part_match):
                    yield rest_match
    elif isinstance(regex[0], list):
        # Repetition
        lower_bound, upper_bound = (eval_numeric(expr, match_state)
                                    for expr in regex[0])
        if regex[0][1] == "":
            # An empty upper bound represents infinity
            upper_bound = INFINITY
        if lower_bound is None or upper_bound is None:
            # One of the bounds contained a backreference that failed
            # or a division by 0
            return
        if lower_bound < 0:
            lower_bound = 0
        subexpression = regex[1]
        for reps in range_from_to(lower_bound, upper_bound):
            if reps == 0:
                yield match_state
            else:
                for first_match in match(subexpression,
                                         match_state):
                    rest = [[reps - 1, reps - 1], subexpression]
                    for rest_match in match(rest,
                                            first_match):
                        yield rest_match
    elif regex[0] == "(":
        # Capture group
        group_num, subexpression = regex[1:]
        start_index = match_state.pos
        for new_state in match(subexpression,
                               match_state):
            end_index = new_state.pos
            matched_string = new_state.string[start_index:end_index]
            new_state.groups[group_num] = matched_string
            yield new_state
    elif regex[0] == "${":
        value = eval_numeric(regex[1], match_state)
        if value is not None:
            new_state = match_literal_string(str(value), match_state)
            if new_state is not None:
                yield new_state


def main(regex, inputs=None, result_limit=1, match_sep="\n",
         trailing_newline=True, verbose=False):
    if verbose:
        verbose_separator = "-----"
        print(verbose_separator)
    if inputs is None:
        inputs = []
    if verbose:
        print("Regex:")
        print(regex)
        print(verbose_separator)
    scanned_regex = scan(regex)
    if verbose:
        print("Tokenized:")
        print(scanned_regex)
        print(verbose_separator)
    parsed_regex = parse(scanned_regex)
    if verbose:
        print("Parse tree:")
        pprint.pprint(parsed_regex)
        print(verbose_separator)
    for i, match_result in enumerate(match(parsed_regex,
                                     MatchState(inputs=inputs))):
        if i > 0:
            print(match_sep, end="")
        print(match_result, end="")
        if i + 1 >= result_limit:
            break
    if trailing_newline:
        print()


def parse_options():
    argparser = argparse.ArgumentParser()
    regex_source = argparser.add_mutually_exclusive_group()
    match_limit = argparser.add_mutually_exclusive_group()
    regex_source.add_argument("-r",
                              "--regex",
                              help="use the given regex")
    regex_source.add_argument("-f",
                              "--file",
                              help="read regex from file")
    regex_source.add_argument("-i",
                              "--stdin",
                              action="store_true",
                              help="enter regex on stdin")
    match_limit.add_argument("-l",
                             "--limit",
                             type=int,
                             default=1,
                             help="maximum number of matches to return")
    match_limit.add_argument("-a",
                             "--all",
                             action="store_true",
                             help="return all matches (may cause "
                             "infinite output)")
    argparser.add_argument("-s",
                           "--sep",
                           default="\n",
                           help="separator between successive matches")
    argparser.add_argument("-n",
                           "--no-newline",
                           action="store_false",
                           help="don't output a trailing newline")
    argparser.add_argument("-v",
                           "--verbose",
                           action="store_true",
                           help="show extra messages")
    argparser.add_argument("args",
                           nargs="*",
                           help="inputs (available as groups $~1, $~2, etc.)")

    if len(sys.argv) == 1:
        # With no args given, display the help message
        argparser.parse_args(["--help"])
    else:
        options = argparser.parse_args()

    if options.regex:
        # Regex specified on the command line
        pass
    elif options.stdin:
        # Get regex from stdin, stopping at EOF
        options.regex = ""
        try:
            while True:
                options.regex += input() + "\n"
        except EOFError:
            pass
        # Remove final newline
        if options.regex.endswith("\n"):
            options.regex = options.regex[:-1]
    elif options.file:
        # Try to read the regex from the given file
        try:
            with open(options.file) as f:
                options.regex = f.read()
        except:
            print("Could not read from file", options.file, file=sys.stderr)
            sys.exit(1)
    elif options.args:
        # Try options.args[0] as a file, and if that doesn't work,
        # as a regex
        arg0 = options.args.pop(0)
        try:
            with open(arg0) as f:
                options.regex = f.read()
        except:
            options.regex = arg0
    else:
        print("No regex specified (use -h option for usage information)",
              file=sys.stderr)
        sys.exit(1)

    if options.all:
        options.limit = INFINITY

    return options


if __name__ == "__main__":
    options = parse_options()
    main(options.regex, inputs=options.args, result_limit=options.limit,
         match_sep=options.sep, trailing_newline=options.no_newline,
         verbose=options.verbose)

