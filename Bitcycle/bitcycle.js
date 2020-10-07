
// Define magic numbers and other constants

const WEST = 0;
const NORTH = 1;
const EAST = 2;
const SOUTH = 3;

const ZERO_BIT = 1;
const ONE_BIT = 2;

const CIRCLE_RADIUS = 6;
const GRID_SQUARE_SIZE = 16;
const GRID_FONT_SIZE = 14;

const BLUE = "#ABF";
const GREEN = "#6E6";
const TEAL = "#4A9";
const BLACK = "#000";

const COLLECTOR_NAMES = "ABCDEFGHIJKLMNOPQRSTUWXYZ";
const SIMPLE_DEVICES = ">^<v~+={}/\\|-@";

function dx(direction) {
	if (direction === WEST) {
		return -1;
	} else if (direction === EAST) {
		return 1;
	} else {
		return 0;
	}
}

function dy(direction) {
	if (direction === NORTH) {
		return -1;
	} else if (direction === SOUTH) {
		return 1;
	} else {
		return 0;
	}
}

function turnRight(direction) {
    var newDirection;
    switch (direction) {
        case NORTH:
            newDirection = EAST;
            break;
        case EAST:
            newDirection = SOUTH;
            break;
        case SOUTH:
            newDirection = WEST;
            break;
        case WEST:
            newDirection = NORTH;
            break;
        default:
            // This shouldn't happen
            break;
    }
    return newDirection;
}

function turnLeft(direction) {
    var newDirection;
    switch (direction) {
        case NORTH:
            newDirection = WEST;
            break;
        case EAST:
            newDirection = NORTH;
            break;
        case SOUTH:
            newDirection = EAST;
            break;
        case WEST:
            newDirection = SOUTH;
            break;
        default:
            // This shouldn't happen
            break;
    }
    return newDirection;
}

// Define Bit class
function Bit(x, y, direction, value) {
    this.x = x;
    this.y = y;
    if (+value) {
        this.value = 1;
    } else {
        this.value = 0;
    }
    this.direction = direction;
}

Bit.prototype.tick = function() {
    this.x += dx(this.direction);
    this.y += dy(this.direction);
}

Bit.prototype.toString = function() {
    if (this.value) {
        return "1";
    } else {
        return "0";
    }
}

// Define Collector class
function Collector(chr) {
    this.chr = chr.toUpperCase();
    this.open = false;
    this.queue = [];
    this.bitCode = 0;
}

Collector.prototype.tick = function() {
    var outBit = null;
    if (this.open) {
        if (this.queue.length > 0) {
            outBit = this.queue.shift();
            outBit.direction = EAST;
        } else {
            this.open = false;
        }
    }
    return outBit;
}

Collector.prototype.toString = function() {
    if (this.open) {
        return this.chr.toLowerCase();
    } else {
        return this.chr;
    }
}

// Define Source class
function Source(x, y, inputString) {
    this.x = x;
    this.y = y;
    this.queue = inputString.split("");
    this.open = (this.queue.length > 0);
}

Source.prototype.tick = function() {
    var outBit = null;
    if (this.open) {
        outBit = new Bit(this.x, this.y, EAST, this.queue.shift());
        if (this.queue.length === 0) {
            this.open = false;
        }
    }
    return outBit;
}

Source.prototype.toString = function() {
    return "?";
}

// Define Sink class
function Sink(x, y, idNumber) {
    this.x = x;
    this.y = y;
    this.idNumber = idNumber;
}

// TODO: handle multiple sinks--idNumber should determine which row they output to
Sink.prototype.output = function(bit) {
    var outputs = document.getElementById('outputs');
    outputs.value += bit.value;
}

Sink.prototype.toString = function() {
    return "!";
}

// Define Device class for generic devices that aren't Collectors, Sources, or Sinks
function Device(chr) {
    this.chr = chr;
    this.bitCode = 0;
}

Device.prototype.toString = function() {
    return this.chr;
}

// Define Program class
function Program(codeLines, inputLines, speed) {
    var sinkNumber = 0;
    
    this.setSpeed(speed);
    this.done = false;
    
    this.height = codeLines.length;
    this.width = Math.max(...codeLines.map(line => line.length));
    this.collectors = {};
    this.openCollectors = [];
    this.sources = [];
    this.sinks = [];
    this.activeBits = [];
    this.grid = [];
    
    for (var y = 0; y < this.height; y++) {
        var row = [];
        for (var x = 0; x < this.width; x++) {
            if (x < codeLines[y].length) {
                var chr = codeLines[y][x].toLowerCase();
                if (COLLECTOR_NAMES.indexOf(chr.toUpperCase()) > -1) {
                    // A letter (that isn't v) is a collector
                    var collector = new Collector(chr);
                    if (this.collectors[collector.chr]) {
                        this.collectors[collector.chr].push(collector);
                    } else {
                        this.collectors[collector.chr] = [collector];
                    }
                    row.push(collector);
                } else if (chr === "?") {
                    // A question mark is a source
                    var inputData;
                    if (inputLines.length > 0) {
                        inputData = inputLines.shift();
                    } else {
                        inputData = ""; 
                    }
                    var source = new Source(x, y, inputData);
                    if (source.open) {
                        this.sources.push(source);
                    }
                    row.push(source);
                } else if (chr === "!") {
                    // An exclamation point is a sink
                    var sink = new Sink(x, y, sinkNumber);
                    sinkNumber++;
                    this.sinks.push(sink);
                    row.push(sink);
                } else if ("01".indexOf(chr) > -1) {
                    // A 0 or 1 is a bit
                    this.activeBits.push(new Bit(x, y, EAST, chr));
                    row.push(new Device(" "));
                } else if (SIMPLE_DEVICES.indexOf(chr) > -1) {
                    // A device without any storage capacity
                    row.push(new Device(chr));
                } else {
                    row.push(new Device(chr));
                }
            } else {
                row.push(new Device(" "));
            }
        }
        this.grid.push(row);
    }
}

Program.prototype.setSpeed = function(speed) {
    this.speed = +speed || 10;
}

Program.prototype.run = function() {
    this.tick();
    if (!this.done) {
        this.timeout = window.setTimeout(this.run.bind(this), 1000 / this.speed);
    }
}

Program.prototype.tick = function() {
    if (this.done) {
        this.halt();
        return;
    }
    
    if (this.activeBits.length > 0) {
        // Move bits that are on the playfield
        for (var b = this.activeBits.length - 1; b >= 0; b--) {
            var bit = this.activeBits[b];
            bit.tick();
            if (0 <= bit.x && bit.x < this.width && 0 <= bit.y && bit.y < this.height) {
                var device = this.grid[bit.y][bit.x];
                if (device instanceof Collector) {
                    // Add the bit to the collector's queue and remove it from active bits
                    device.queue.push(bit);
                    this.activeBits.splice(b, 1);
                } else if (device instanceof Source) {
                    // Bits that hit sources are deleted
                    this.activeBits.splice(b, 1);
                } else if (device instanceof Sink) {
                    // Output the bit and remove it from active bits
                    device.output(bit);
                    this.activeBits.splice(b, 1);
                } else {
                    switch (device.chr) {
                        case ">":
                        case "}":
                            bit.direction = EAST;
                            break;
                        case "<":
                        case "{":
                            bit.direction = WEST;
                            break;
                        case "^":
                            bit.direction = NORTH;
                            break;
                        case "v":
                            bit.direction = SOUTH;
                            break;
                        case "+":
                            // Turn right if bit is 1, left if 0
                            if (bit.value === 1) {
                                bit.direction = turnRight(bit.direction);
                            } else if (bit.value === 0) {
                                bit.direction = turnLeft(bit.direction);
                            }
                            break;
                        case "/":
                            // Reflect bit and change mirror to inactive state
                            switch (bit.direction) {
                                case NORTH:
                                    bit.direction = EAST;
                                    break;
                                case EAST:
                                    bit.direction = NORTH;
                                    break;
                                case SOUTH:
                                    bit.direction = WEST;
                                    break;
                                case WEST:
                                    bit.direction = SOUTH;
                                    break;
                                default:
                                    // This shouldn't happen
                                    break;
                            }
                            device.chr = "|";
                            break;
                        case "\\":
                            // Reflect bit and change mirror to inactive state
                            switch (bit.direction) {
                                case NORTH:
                                    bit.direction = WEST;
                                    break;
                                case EAST:
                                    bit.direction = SOUTH;
                                    break;
                                case SOUTH:
                                    bit.direction = EAST;
                                    break;
                                case WEST:
                                    bit.direction = NORTH;
                                    break;
                                default:
                                    // This shouldn't happen
                                    break;
                            }
                            device.chr = "-";
                            break;
                        case "~":
                            // Turn original bit right, create new one with
                            // opposite value going opposite direction
                            this.activeBits.push(new Bit(bit.x, bit.y, turnLeft(bit.direction), !bit.value));
                            bit.direction = turnRight(bit.direction);
                            break;
                        case "=":
                            // Pass this bit straight through, but change device
                            // to one of {} based on this bit's value
                            if (bit.value === 1) {
                                device.chr = "}";
                            } else if (bit.value === 0) {
                                device.chr = "{";
                            }
                            break;
                        case "@":
                            // Halt execution
                            this.halt();
                            break;
                        default:
                            // No-op
                            break;
                    }
                }
            } else {
                // Bit went outside playfield; delete it
                this.activeBits.splice(b, 1);
            }
        }
    } else {
        // No bits are on the playfield; see if there's a collector we can open
        var nextCollectorName = null;
        for (var n = 0; n < COLLECTOR_NAMES.length; n++) {
            var name = COLLECTOR_NAMES[n];
            if (this.collectors[name] && this.collectors[name].length > 0) {
                var nonemptyCollector = false;
                for (var c = 0; c < this.collectors[name].length; c++) {
                    var collector = this.collectors[name][c];
                    if (collector.queue.length > 0) {
                        // At least one collector with this name has bits in it
                        nonemptyCollector = true;
                        break;
                    }
                }
                if (nonemptyCollector) {
                    nextCollectorName = name;
                    break;
                }
            }
        }
        if (nextCollectorName !== null) {
            // Open the collectors of the first name that has bits
            this.openCollectors = this.collectors[nextCollectorName].slice();
            for (var c = 0; c < this.openCollectors.length; c++) {
                this.openCollectors[c].open = true;
            }
            this.reset();
        } else if (this.sources.length === 0) {
            // If there are no collectors to open and no sources with data, halt
            this.halt();
        }
    }
    
    if (this.sources.length > 0) {
        // Send a bit out of each source that still has bits
        for (var s = this.sources.length - 1; s >= 0; s--) {
            var source = this.sources[s];
            var outBit = source.tick();
            if (outBit !== null) {
                this.activeBits.push(outBit);
                if (!source.open) {
                    // The source is now empty; remove it from the sources list
                    this.sources.splice(s, 1);
                }
            }
        }
    }
    
    if (this.openCollectors.length > 0) {
        // Send a bit out of each open collector that still has bits
        for (var c = this.openCollectors.length - 1; c >= 0; c--) {
            var collector = this.openCollectors[c];
            var outBit = collector.tick();
            if (outBit !== null) {
                this.activeBits.push(outBit);
            } else {
                // The collector is now empty; remove it from the open collectors list
                this.openCollectors.splice(c, 1);
            }
        }
    }
    
    // Display the current state of the playfield
    displaySource(this.grid, this.activeBits);
}

Program.prototype.reset = function() {
    for (var y = 0; y < this.height; y++) {
        var row = this.grid[y];
        for (var x = 0; x < this.width; x++) {
            var device = row[x];
            switch (device.toString()) {
                case "|":
                    device.chr = "/";
                    break;
                case "-":
                    device.chr = "\\";
                    break;
                case "{":
                case "}":
                    device.chr = "=";
                    break;
                default:
                    break;
            }
        }
    }
}

Program.prototype.pause = function() {
    window.clearTimeout(this.timeout);
}

Program.prototype.halt = function() {
    this.done = true;
    this.pause();
    endProgram();
}

function displaySource(grid, activeBits) {
    clearCanvas();
    // Attach active bits to the devices at those coordinates
    for (var b = 0; b < activeBits.length; b++) {
        var bit = activeBits[b];
        grid[bit.y][bit.x].bitCode |= (bit.value ? ONE_BIT : ZERO_BIT);
    }
    // Display active bits and devices
    for (var y = 0; y < grid.length; y++) {
        var row = grid[y];
        for (var x = 0; x < row.length; x++) {
            var device = row[x];
            drawBitsAt(device.bitCode, x, y);
            drawDeviceAt(device, x, y);
            device.bitCode = 0;
        }
    }
}

function clearCanvas() {
    if (context !== null) {
        context.clearRect(0, 0, canvas.width, canvas.height);
    }
}

function drawBitsAt(bitCode, x, y) {
    if (bitCode > 0) {
        var circleX = (x + 0.5) * GRID_SQUARE_SIZE;
        var circleY = (y + 0.5) * GRID_SQUARE_SIZE;
        var circleColor;
        if (bitCode === ZERO_BIT) {
            circleColor = BLUE;
        } else if (bitCode === ONE_BIT) {
            circleColor = GREEN;
        } else {  // Both a zero and a one bit
            circleColor = TEAL;
        }
        drawCircle(circleX, circleY, CIRCLE_RADIUS, circleColor);
    }
}

function drawCircle(x, y, radius, color) {
    context.fillStyle = color;
    context.beginPath();
    context.arc(x, y, radius, 0, 2*Math.PI);
    context.fill();
}

function drawDeviceAt(device, x, y) {
    var textX = (x + 0.5) * GRID_SQUARE_SIZE - 0.3 * GRID_FONT_SIZE;
    var textY = (y + 0.5) * GRID_SQUARE_SIZE + 0.25 * GRID_FONT_SIZE;
    context.fillStyle = BLACK;
    context.fillText(device.toString(), textX, textY);
}

function showEditor() {
    var sourceCode = document.getElementById('source'),
        inputs = document.getElementById('inputs'),
        canvasWrapper = document.getElementById('canvas-container'),
        run = document.getElementById('run'),
        pause = document.getElementById('pause'),
        step = document.getElementById('step'),
        done = document.getElementById('done');
    
    // Show the input fields and run/pause/step buttons, hide the canvas and Done message
    sourceCode.style.display = "block";
    inputs.style.display = "block";
    canvasWrapper.style.display = "none";
    run.style.display = "block";
    pause.style.display = "block";
    step.style.display = "block";
    done.style.display = "none";
    
    sourceCode.focus();
}

function hideEditor() {
    var sourceCode = document.getElementById('source'),
        inputs = document.getElementById('inputs'),
        canvasWrapper = document.getElementById('canvas-container');
    
    // Hide the input fields, show the canvas
    sourceCode.style.display = "none";
    inputs.style.display = "none";
    canvasWrapper.style.display = "block";
    
    // Set up the canvas
    canvas.height = program.height * GRID_SQUARE_SIZE;
    canvas.width = program.width * GRID_SQUARE_SIZE;
    context = canvas.getContext("2d");
    context.font = "bold " + GRID_FONT_SIZE + "px Courier New";
    
    // Display the current state of the playfield
    displaySource(program.grid, program.activeBits);
}

function resetProgram() {
    var outputs = document.getElementById('outputs');
    
    if (outputs !== null) {
        outputs.value = null;
    }
    if (program !== null) {
        program.pause();
    }
    program = null;
    showEditor();
}

function initProgram() {
    var sourceCode = document.getElementById('source'),
        ticksPerSecond = document.getElementById('ticks-per-second'),
        inputs = document.getElementById('inputs');
    
    program = new Program(
        sourceCode.value.split(/\r?\n/),
        inputs.value.split(/\r?\n/),
        ticksPerSecond.innerHTML
    );
    hideEditor();
}

function endProgram() {
    var run = document.getElementById('run'),
        pause = document.getElementById('pause'),
        step = document.getElementById('step'),
        done = document.getElementById('done');
    
    // Hide the run/pause/step buttons, show the Done message
    run.style.display = "none";
    pause.style.display = "none";
    step.style.display = "none";
    done.style.display = "block";
}

function runBtnClick() {
    if (program === null || program.done) {
        resetProgram();
        initProgram();
    } else {
        program.pause();
        var ticksPerSecond = document.getElementById('ticks-per-second');
        program.setSpeed(ticksPerSecond.innerHTML);
    }
    program.run();
}

function stepBtnClick() {
    if (program === null) {
        initProgram();
    } else {
        program.pause();
        program.tick();
    }
}

function canvasClick() {
    // TBD
    //resetProgram();
}

var program = null;
var canvas = document.getElementById("playfield");
var context = null;
