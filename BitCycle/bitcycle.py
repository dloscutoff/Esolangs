#!/usr/bin/python3

import os, sys, time, argparse

# Any letter except V is acceptable as a collector name
collectorNames = "ABCDEFGHIJKLMNOPQRSTUWXYZ"
STEP = -1


class Playfield:
    def __init__(self, codeLines, inputs, outputFunction=None):
        self.height = len(codeLines)
        self.width = max(map(len, codeLines))
        self.collectors = {}
        self.openCollectors = []
        self.sources = []
        self.outputFunction = outputFunction
        self.outputBuffer = ""
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
                            source = Source(data, x, y)
                            self.sources.append(source)
                            row.append(source)
                        else:
                            # Not enough inputs to give data to this source
                            # TBD: error message?
                            row.append(Source("", x, y))
                    elif char in "01":
                        # A 0 or 1 is a bit
                        bit = Bit(int(char), x, y)
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
            for index in indicesToRemove[::-1]:
                # Iterate over the indices to remove from largest to smallest
                # so that removing smaller indices doesn't modify the
                # larger ones
                self.sources.pop(index)
        
        if self.openCollectors:
            indicesToRemove = []
            for index, coll in enumerate(self.openCollectors):
                outBit = coll.tick()
                if outBit:
                    self.activeBits.append(outBit)
                else:
                    # No output means that collector is empty; deactivate it
                    coll.open = False
                    indicesToRemove.append(index)
            for index in indicesToRemove[::-1]:
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
                    elif device == "!":
                        # TODO: add multiple output options, probably make
                        # sinks their own class
                        self.output(bit.value)
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
                        newBits.append(Bit(1 - bit.value, bit.x, bit.y,
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
            for index in indicesToRemove[::-1]:
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

    def output(self, data):
        self.outputBuffer += str(data)
        if self.outputFunction:
            self.outputFunction(data)


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

    def enqueue(self, bit):
        self.queue.append(bit)


class Source:
    def __init__(self, data, x, y):
        self.data = iter(data)
        self.x = x
        self.y = y

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
            bit = Bit(int(bitValue), self.x, self.y)
            return bit

class Bit:
    def __init__(self, value, x, y, dx=1, dy=0):
        self.value = int(value)
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    def tick(self):
        self.x += self.dx
        self.y += self.dy


def run(codeLines, pause, *inputs):
    if pause == 0:
        # No-pause mode: display output as it is generated
        outputFunction = lambda *args: print(*args, end="", flush=True)
    elif pause == STEP:
        # Manual step mode: buffer output and display the buffer at each step
        outputFunction = None
        print("Press enter to step; type anything else or Ctrl-C to stop.")
        input()
    else:
        # Pause mode: buffer output and display the buffer at each tick
        outputFunction = None
    playfield = Playfield(codeLines, list(inputs), outputFunction)
    try:
        while True:
            if pause != 0:
                print(playfield)
                print("Output:", playfield.outputBuffer)
                if pause == STEP:
                    # Manual step mode
                    if input() != "":
                        break
                else:
                    time.sleep(pause)
            playfield.tick()
    except (StopIteration, KeyboardInterrupt, EOFError):
        pass

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

if __name__ == "__main__":
    code = testCode
    args = testArgs
    pause = testPause
    if len(sys.argv) > 1:
        # Filename provided on command-line
        argparser = argparse.ArgumentParser()
        argparser.add_argument("-p",
                               "--pause",
                               help="how long to pause between ticks")
        argparser.add_argument("-s",
                               "--step",
                               help="execute one step at a time",
                               action="store_true")
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
            pause = -1
        elif options.pause:
            try:
                pause = float(options.pause)
            except:
                pass
            else:
                if pause < 0:
                    pause = 0
    
    run(code, pause, *args)

