#!/usr/bin/python3

import os
import sys
import time
import argparse

# Any letter except V is acceptable as a collector name
collectorNames = "ABCDEFGHIJKLMNOPQRSTUWXYZ"

# Separator for decimal I/O formats
SEPARATOR = ","

# Magic numbers
RAW = 0
UNSIGNED_UNARY = 1
SIGNED_UNARY = 2
UNSIGNED_BINARY = 3
SIGNED_BINARY = 4
STEP = -1


class Playfield:
    def __init__(self, codeLines, inputs, ioFormat=RAW):
        self.height = len(codeLines)
        self.width = max(map(len, codeLines))
        self.collectors = {}
        self.openCollectors = []
        self.sources = []
        self.sinks = []
        self.activeBits = []
        self.grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if x < len(codeLines[y]):
                    char = codeLines[y][x]
                    if char.upper() in collectorNames:
                        # A letter, not v, is a collector
                        coll = Collector(char)
                        if coll.letter in self.collectors:
                            self.collectors[coll.letter].append(coll)
                        else:
                            self.collectors[coll.letter] = [coll]
                        row.append(coll)
                    elif char == "?":
                        # A question mark is a source
                        if inputs:
                            data = inputs.pop(0)
                            source = Source(x, y, data, ioFormat)
                            self.sources.append(source)
                            row.append(source)
                        else:
                            # Not enough inputs to give data to this source
                            # TBD: error message?
                            row.append(Source(x, y, ""))
                    elif char == "!":
                        # An exclamation point is a sink
                        sink = Sink(x, y, ioFormat)
                        self.sinks.append(sink)
                        row.append(sink)
                    elif char in "01":
                        # A 0 or 1 is a bit
                        bit = Bit(x, y, int(char))
                        self.activeBits.append(bit)
                        row.append(" ")
                    else:
                        row.append(char)
                else:
                    row.append(" ")
            self.grid.append(row)

    def __str__(self):
        displayGrid = [row.copy() for row in self.grid]
        for bit in self.activeBits:
            if displayGrid[bit.y][bit.x] not in [0, 1]:
                displayGrid[bit.y][bit.x] = bit.value
        return "\n".join("".join(str(device)
                                 for device in row)
                         for row in displayGrid)

    def tick(self):
        if self.sources:
            indicesToRemove = []
            for index, source in enumerate(self.sources):
                outBit = source.tick()
                if outBit:
                    self.activeBits.append(outBit)
                else:
                    # No output means that source is empty; remove it from
                    # the sources list
                    indicesToRemove.append(index)
            for index in reversed(indicesToRemove):
                # Iterate over the indices to remove from largest to smallest
                # so that removing smaller indices doesn't modify the
                # larger ones
                self.sources.pop(index)
        
        if self.openCollectors:
            indicesToRemove = []
            for index, collector in enumerate(self.openCollectors):
                outBit = collector.tick()
                if outBit:
                    self.activeBits.append(outBit)
                else:
                    # No output means that collector is empty; deactivate it
                    collector.open = False
                    indicesToRemove.append(index)
            for index in reversed(indicesToRemove):
                # Iterate over the indices to remove from largest to smallest
                # so that removing smaller indices doesn't modify the
                # larger ones
                self.openCollectors.pop(index)
                    
        if self.activeBits:
            indicesToRemove = []
            newBits = []
            for index, bit in enumerate(self.activeBits):
                bit.tick()
                if 0 <= bit.x < self.width and 0 <= bit.y < self.height:
                    device = self.grid[bit.y][bit.x]
                    if type(device) is Source:
                        # Bits that hit sources are deleted
                        indicesToRemove.append(index)
                    elif type(device) is Collector:
                        # Add the bit to the collector's queue
                        device.enqueue(bit)
                        indicesToRemove.append(index)
                    elif type(device) is Sink:
                        device.enqueue(bit)
                        indicesToRemove.append(index)
                    elif device in [">", "}"]:
                        bit.dx, bit.dy = 1, 0
                    elif device in ["<", "{"]:
                        bit.dx, bit.dy = -1, 0
                    elif device == "v":
                        bit.dx, bit.dy = 0, 1
                    elif device == "^":
                        bit.dx, bit.dy = 0, -1
                    elif device == "+":
                        # Turn right if bit is 1, left if 0
                        if bit.value == 1:
                            bit.dx, bit.dy = -bit.dy, bit.dx
                        elif bit.value == 0:
                            bit.dx, bit.dy = bit.dy, -bit.dx
                    elif device == "\\":
                        # Reflect bit and change to inactive state
                        bit.dx, bit.dy = bit.dy, bit.dx
                        self.grid[bit.y][bit.x] = "-"
                    elif device == "/":
                        # Reflect bit and change to inactive state
                        bit.dx, bit.dy = -bit.dy, -bit.dx
                        self.grid[bit.y][bit.x] = "|"
                    elif device == "~":
                        # Turn original bit right, create new one with
                        # opposite value going opposite direction
                        bit.dx, bit.dy = -bit.dy, bit.dx
                        newBits.append(Bit(bit.x, bit.y, 1 - bit.value,
                                           -bit.dx, -bit.dy))
                    elif device == "@":
                        # Terminate immediately
                        raise StopIteration
                    elif device == "=":
                        # Pass this bit straight through, but change to
                        # one of {} based on this bit's value
                        if bit.value == 1:
                            self.grid[bit.y][bit.x] = "}"
                        elif bit.value == 0:
                            self.grid[bit.y][bit.x] = "{"
                else:
                    # Bit went outside playfield; delete it
                    indicesToRemove.append(index)
            for index in reversed(indicesToRemove):
                # Iterate over the indices to remove from largest to smallest
                # so that removing smaller indices doesn't modify the
                # larger ones
                self.activeBits.pop(index)
            self.activeBits.extend(newBits)
        else:
            for letter in collectorNames:
                if letter not in self.collectors:
                    # No collectors in this program use that letter
                    continue
                if any(coll.queue for coll in self.collectors[letter]):
                    # Some collectors with this letter have bits in them:
                    # open these
                    self.openCollectors = self.collectors[letter].copy()
                    for coll in self.openCollectors:
                        coll.open = True
                    self.reset()
                    break
            else:
                # No active bits & no collectors with bits in them: end
                # the program
                raise StopIteration

    def reset(self):
        for y, row in enumerate(self.grid):
            for x, device in enumerate(row):
                if device == "|":
                    self.grid[y][x] = "/"
                elif device == "-":
                    self.grid[y][x] = "\\"
                elif device in ["{", "}"]:
                    self.grid[y][x] = "="


class Collector:
    def __init__(self, letter):
        self.letter = letter.upper()
        self.open = letter.islower()
        self.queue = []

    def __str__(self):
        if self.open:
            return self.letter.lower()
        else:
            return self.letter

    def tick(self):
        if self.open:
            if self.queue:
                bit = self.queue.pop(0)
                bit.dx = 1
                bit.dy = 0
                return bit
            else:
                self.open = False
                return None
        else:
            return None

    def enqueue(self, bit):
        self.queue.append(bit)


class Source:
    def __init__(self, x, y, data, ioFormat=RAW):
        self.x = x
        self.y = y
        self.ioFormat = ioFormat
        if ioFormat == RAW:
            # Inputs are already in bitstring form
            self.data = iter(data)
        elif ioFormat == UNSIGNED_UNARY:
            # Nonnegative integers become runs of 1's; separators become 0's
            decimalNumbers = data.split(SEPARATOR)
            unaryNumbers = []
            for decimalNumber in decimalNumbers:
                try:
                    decimalNumber = int(decimalNumber)
                except ValueError:
                    # Not an integer
                    # TODO: error?
                    continue
                if decimalNumber < 0:
                    # Negative integer
                    # TODO: error?
                    continue
                unaryNumbers.append("1" * decimalNumber)
            self.data = iter("0".join(unaryNumbers))
        elif ioFormat == SIGNED_UNARY:
            # Integers become runs of 1's, with 0 prepended to
            # nonpositive numbers; separators become 0's
            decimalNumbers = data.split(SEPARATOR)
            unaryNumbers = []
            for decimalNumber in decimalNumbers:
                try:
                    decimalNumber = int(decimalNumber)
                except ValueError:
                    # Not an integer
                    # TODO: error?
                    continue
                if decimalNumber <= 0:
                    unaryNumber = "0"
                else:
                    unaryNumber = ""
                unaryNumber += "1" * abs(decimalNumber)
                unaryNumbers.append(unaryNumber)
            self.data = iter("0".join(unaryNumbers))
        else:
            raise NotImplemented("Unknown I/O format: %s" % self.ioFormat)

    def __str__(self):
        return "?"

    def tick(self):
        try:
            bitValue = next(self.data)
            while bitValue not in ["0", "1"]:
                print(bitValue, file=sys.stderr)
                bitValue = next(self.data)
        except StopIteration:
            return None
        else:
            bit = Bit(self.x, self.y, int(bitValue))
            return bit


class Sink:
    def __init__(self, x, y, ioFormat=RAW):
        self.x = x
        self.y = y
        self.ioFormat = ioFormat
        self.queue = []
        self.output = ""
        self.rawOutput = ""

    def __str__(self):
        return "!"

    def tick(self):
        pass

    def enqueue(self, bit):
        self.rawOutput += str(bit)
        if self.ioFormat == RAW:
            self.output += str(bit)
        elif self.ioFormat == UNSIGNED_UNARY:
            if bit.value == 0:
                # 0 is separator; output the current queue value
                self.output += str(len(self.queue))
                self.output += SEPARATOR
                self.queue = []
            else:
                # Add a bit to the current queue value
                self.queue.append(bit)
        elif self.ioFormat == SIGNED_UNARY:
            if bit.value == 0 and self.queue:
                # 0 with nonempty queue is separator; output the current
                # queue value
                if self.queue[0].value == 0:
                    # A leading 0 on the value is a sign bit
                    self.queue.pop(0)
                    if self.queue:
                        # Output a minus sign unless the number was just
                        # the 0 bit (in which case it represents 0)
                        self.output += "-"
                self.output += str(len(self.queue))
                self.output += SEPARATOR
                self.queue = []
            else:
                # 0 with empty queue is sign bit; 1 is always part of a
                # number; add to the current queue value
                self.queue.append(bit)
        else:
            raise NotImplemented("Unknown I/O format: %s" % self.ioFormat)

    def finalize(self):
        if self.ioFormat == UNSIGNED_UNARY:
            self.output += str(len(self.queue))
        elif self.ioFormat == SIGNED_UNARY:
            if self.queue[0].value == 0:
                self.queue.pop(0)
                if self.queue:
                    self.output += "-"
            self.output += str(len(self.queue))


class Bit:
    def __init__(self, x, y, value, dx=1, dy=0):
        self.value = int(bool(value))
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    def tick(self):
        self.x += self.dx
        self.y += self.dy

    def __str__(self):
        return str(self.value)


def run(codeLines, pause, ioFormat, *inputs):
    if pause == STEP:
        # Manual step mode: buffer output and display the buffer at each step
        print("Press enter to step; type anything else or Ctrl-C to stop.")
        input()
    playfield = Playfield(codeLines, list(inputs), ioFormat)
    try:
        while True:
            if pause != 0:
                print(playfield)
                if len(playfield.sinks) == 1:
                    print("Sink:", playfield.sinks[0].rawOutput)
                else:
                    for sinkNum, sink in enumerate(playfield.sinks):
                        print("Sink %d:" % (sinkNum + 1), sink.rawOutput)
                if pause == STEP:
                    # Manual step mode
                    if input() != "":
                        break
                else:
                    time.sleep(pause)
            playfield.tick()
    except (StopIteration, KeyboardInterrupt, EOFError):
        pass
    if pause != 0:
        print()
        print("Output:")
    for sink in playfield.sinks:
        sink.finalize()
        print(sink.output)


testCode = r"""
 v        <
         C^
?>\ \  >B^  <
 >    A+^  ~
 +<A   \/ v
!\    /  <
       >    ^
   ^~v    >~
  v  < v~^>\
       A  +\
 v           <
      >     C^
@ /     ^
?>/        B^
""".splitlines()
testArgs = ["110100", "10"]
testPause = 0.15
testIOFormat = RAW

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Filename provided on command-line
        argparser = argparse.ArgumentParser()
        pauseOptions = argparser.add_mutually_exclusive_group()
        pauseOptions.add_argument("-p",
                                  "--pause",
                                  help="how long to pause between ticks")
        pauseOptions.add_argument("-s",
                                  "--step",
                                  help="execute one step at a time",
                                  action="store_true")
        ioOptions = argparser.add_mutually_exclusive_group()
        ioOptions.add_argument("-u",
                               "--unsigned-unary",
                               help="render decimal I/O as unsigned unary",
                               action="store_true")
        ioOptions.add_argument("-U",
                               "--signed-unary",
                               help="render decimal I/O as signed unary",
                               action="store_true")
        # Flags TODO:
        # -b  Translate decimal I/O as unsigned binary (little-endian)
        # -B width  Translate decimal I/O as fixed-width twos' complement
        #           signed binary (little-endian)
        # (Possibly something for ASCII I/O?)
        argparser.add_argument("filename",
                               help="name of code file")
        argparser.add_argument("args",
                               help="inputs to the program",
                               nargs="*")
        
        options = argparser.parse_args()
        if options.filename:
            try:
                with open(options.filename) as f:
                    code = f.read().splitlines()
            except:
                pass
            else:
                args = options.args
        pause = 0
        if options.step:
            pause = STEP
        elif options.pause:
            try:
                pause = float(options.pause)
            except:
                pass
            else:
                if pause < 0:
                    pause = 0
        ioFormat = RAW
        if options.unsigned_unary:
            ioFormat = UNSIGNED_UNARY
        elif options.signed_unary:
            ioFormat = SIGNED_UNARY
    else:
        code = testCode
        pause = testPause
        ioFormat = testIOFormat
        args = testArgs
    run(code, pause, ioFormat, *args)

