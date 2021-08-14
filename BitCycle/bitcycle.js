
// Define magic numbers and other constants

const WEST = 0;
const NORTH = 1;
const EAST = 2;
const SOUTH = 3;

const ZERO_BIT = 1;
const ONE_BIT = 2;

const BIT_SHAPE_RADIUS = 7;
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

function intToUnary(number) {
    number = Math.trunc(number);
    return "1".repeat(Math.abs(number));
}

function intToSignedUnary(number) {
    number = Math.trunc(number);
    if (number <= 0) {
        return "0" + "1".repeat(Math.abs(number));
    } else {
        return "1".repeat(number);
    }
}

function unaryToInt(unary) {
    return unary.length;
}

function signedUnaryToInt(unary) {
    if (unary[0] === "0") {
        return -(unary.length - 1);
    } else {
        return unary.length;
    }
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
function Source(x, y, inputString, ioFormat) {
    this.x = x;
    this.y = y;
    if (ioFormat === "unsigned") {
        inputString = inputString.split(",").map(intToUnary).join("0");
    } else if (ioFormat === "signed") {
        inputString = inputString.split(",").map(intToSignedUnary).join("0");
    }
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
function Sink(idNumber, ioFormat) {
    this.idNumber = idNumber;
    this.ioFormat = ioFormat;
    this.buffer = "";
}

Sink.prototype.output = function(bit) {
    if (this.ioFormat === "raw") {
        this.buffer += bit.value;
        this.flush();
    } else if (this.ioFormat === "unsigned") {
        if (bit.value === 1) {
            this.buffer += bit.value;
        } else {
            this.flush();
        }
    } else if (this.ioFormat === "signed") {
        if (bit.value === 1 || this.buffer === "") {
            this.buffer += bit.value;
        } else {
            this.flush();
        }
    }
}

Sink.prototype.flush = function() {
    var outputArea = document.getElementById('output' + this.idNumber);
    if (this.ioFormat === "raw") {
        outputArea.textContent += this.buffer;
    } else if (this.ioFormat === "unsigned") {
        if (outputArea.textContent !== "") {
            outputArea.textContent += ",";
        }
        outputArea.textContent += unaryToInt(this.buffer);
    } else if (this.ioFormat === "signed") {
        if (outputArea.textContent !== "") {
            outputArea.textContent += ",";
        }
        outputArea.textContent += signedUnaryToInt(this.buffer);
    }
    this.buffer = "";
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
function Program(codeLines, inputLines, speed, ioFormat, expand) {
    var sinkNumber = 0;
    
    this.setSpeed(speed);
    this.done = false;
    this.paused = true;
    
    if (expand) {
        // Add a blank line every other line and an empty column every other column
        for (var y = codeLines.length - 1; y >= 0; y--) {
            var newLine = " " + codeLines[y].split("").join(" ") + " ";
            codeLines.splice(y, 1, "", newLine);
        }
        codeLines.push("");
    }
    
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
                    var source = new Source(x, y, inputData, ioFormat);
                    if (source.open) {
                        this.sources.push(source);
                    }
                    row.push(source);
                } else if (chr === "!") {
                    // An exclamation point is a sink
                    var sink = new Sink(sinkNumber, ioFormat);
                    this.sinks.push(sink);
                    row.push(sink);
                    // Create an output area for this sink
                    var outputArea = document.createElement('div');
                    outputArea.setAttribute("id", "output" + sinkNumber + "Area");
                    outputArea.setAttribute("class", "output");
                    var outputLabel = document.createElement('span');
                    outputArea.setAttribute("id", "output" + sinkNumber + "Label");
                    outputLabel.textContent = "Out" + (sinkNumber + 1) + ": ";
                    outputArea.appendChild(outputLabel);
                    var output = document.createElement('span');
                    output.setAttribute("id", "output" + sinkNumber);
                    output.textContent = "";
                    outputArea.appendChild(output);
                    document.getElementById('output-container').appendChild(outputArea);
                    sinkNumber++;
                } else if (chr === "0" || chr === "1") {
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
    this.paused = false;
    this.tick();
    if (!this.done) {
        this.timeout = window.setTimeout(this.run.bind(this), 1000 / this.speed);
    }
}

Program.prototype.tick = function() {
    if (this.done) {
        haltProgram();
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
                            haltProgram();
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
            haltProgram();
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
    this.paused = true;
}

Program.prototype.halt = function() {
    this.done = true;
    this.pause();
    for (var s = 0; s < this.sinks.length; s++) {
        this.sinks[s].flush();
    }
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
        var centerX = (x + 0.5) * GRID_SQUARE_SIZE;
        var centerY = (y + 0.5) * GRID_SQUARE_SIZE;
        if (bitCode === ZERO_BIT) {
            drawCircle(centerX, centerY, BIT_SHAPE_RADIUS, BLUE);
        } else if (bitCode === ONE_BIT) {
            drawDiamond(centerX, centerY, BIT_SHAPE_RADIUS, GREEN);
        } else {  // Both a zero and a one bit
            drawCircle(centerX, centerY, BIT_SHAPE_RADIUS, BLUE);
            drawDiamond(centerX, centerY, BIT_SHAPE_RADIUS, GREEN);
        }
    }
}

function drawCircle(x, y, radius, color) {
    context.fillStyle = color;
    context.beginPath();
    context.arc(x, y, radius, 0, 2*Math.PI);
    context.fill();
}

function drawDiamond(x, y, radius, color) {
    context.fillStyle = color;
    context.beginPath();
    context.moveTo(x - radius, y);
    context.lineTo(x, y - radius);
    context.lineTo(x + radius, y);
    context.lineTo(x, y + radius);
    context.fill();
}

function drawDeviceAt(device, x, y) {
    var textX = (x + 0.5) * GRID_SQUARE_SIZE - 0.3 * GRID_FONT_SIZE;
    var textY = (y + 0.5) * GRID_SQUARE_SIZE + 0.25 * GRID_FONT_SIZE;
    context.fillStyle = BLACK;
    context.fillText(device.toString(), textX, textY);
}

function urlDecode(value) {
    try {
        return atob(value.replaceAll("_", "="));
    } catch (error) {
        console.log("Error while decoding " + value);
        console.log(error);
        return "";
    }
}

function urlEncode(value) {
    try {
        return btoa(value).replaceAll("=", "_");
    } catch (error) {
        console.log("Error while encoding " + value);
        console.log(error);
        return "";
    }
}

function loadFromQueryString() {
    var sourceCode = document.getElementById('source'),
        inputs = document.getElementById('inputs'),
        ioFormatSelect = document.getElementById('io-format');
    var queryString = location.search.slice(1);
    
    for (const param of queryString.split("&")) {
        var key;
        var value;
        [key, value] = param.split("=");
        if (key === "p") {
            sourceCode.value = urlDecode(value);
        } else if (key === "i") {
            inputs.value = urlDecode(value);
        } else if (key === "f") {
            ioFormatSelect.selectedIndex = value;
            if (ioFormatSelect.selectedIndex === -1) {
                // Not a valid selection; select the default format instead
                ioFormatSelect.selectedIndex = 0;
            }
        }
    }
}

function generateQueryString() {
    var sourceCode = document.getElementById('source'),
        inputs = document.getElementById('inputs'),
        ioFormatSelect = document.getElementById('io-format');
    var params = [
        ["p", urlEncode(sourceCode.value.replaceAll(/[^ -~\n]/g, "."))],
        ["i", urlEncode(inputs.value)],
        ["f", ioFormatSelect.selectedIndex]
    ].filter(([key, value]) => value).map(pair => pair.join("="));
    return "?" + params.join("&");
}

function generatePermalink() {
    return location.origin + location.pathname + generateQueryString();
}

function showEditor() {
    var editor = document.getElementById('editor'),
        interpreter = document.getElementById('interpreter'),
        startEdit = document.getElementById('start-edit'),
        permalink = document.getElementById('permalink'),
        executionControls = document.getElementById('execution-controls'),
        sourceCode = document.getElementById('source');
    
    editor.style.display = "block";
    interpreter.style.display = "none";
    startEdit.value = "Execute";
    
    permalink.style.display = "inline-block";
    executionControls.style.display = "none";
    
    sourceCode.focus();
}

function hideEditor() {
    var editor = document.getElementById('editor'),
        interpreter = document.getElementById('interpreter'),
        startEdit = document.getElementById('start-edit'),
        permalink = document.getElementById('permalink'),
        executionControls = document.getElementById('execution-controls');
    
    editor.style.display = "none";
    interpreter.style.display = "block";
    startEdit.value = "Edit";
    
    permalink.style.display = "none";
    executionControls.style.display = "block";
}

function loadProgram() {
    var sourceCode = document.getElementById('source'),
        ticksPerSecond = document.getElementById('ticks-per-second'),
        inputs = document.getElementById('inputs'),
        ioFormatSelect = document.getElementById('io-format'),
        expand = document.getElementById('expand'),
        runPause = document.getElementById('run-pause'),
        step = document.getElementById('step'),
        done = document.getElementById('done'),
        haltRestart = document.getElementById('halt-restart');
    
    program = new Program(
        sourceCode.value.split(/\r?\n/),
        inputs.value.split(/\r?\n/),
        ticksPerSecond.innerHTML,
        ioFormatSelect.value,
        expand.checked
    );
    
    // Set up the canvas
    canvas.height = program.height * GRID_SQUARE_SIZE;
    canvas.width = program.width * GRID_SQUARE_SIZE;
    context = canvas.getContext("2d");
    context.font = "bold " + GRID_FONT_SIZE + "px Courier New";
    
    // Display the current state of the playfield
    displaySource(program.grid, program.activeBits);
    
    runPause.style.display = "block";
    step.style.display = "block";
    done.style.display = "none";
    runPause.value = "Run";
    haltRestart.value = "Halt";
}

function unloadProgram() {
    if (program !== null) {
        program.pause();
    }
    program = null;
    // Delete all output areas
    var outputContainer = document.getElementById('output-container');
    while (outputContainer.firstChild) {
        outputContainer.removeChild(outputContainer.lastChild);
    }
}

function haltProgram() {
    var runPause = document.getElementById('run-pause'),
        step = document.getElementById('step'),
        done = document.getElementById('done'),
        haltRestart = document.getElementById('halt-restart');
    
    program.halt();
    
    runPause.style.display = "none";
    step.style.display = "none";
    done.style.display = "block";
    haltRestart.value = "Restart";
}

function startEditBtnClick() {
    if (program === null) {
        loadProgram();
        hideEditor();
    } else {
        unloadProgram();
        showEditor();
    }
}

function runPauseBtnClick() {
    var runPause = document.getElementById('run-pause');
    if (program !== null && !program.done) {
        if (program.paused) {
            var ticksPerSecond = document.getElementById('ticks-per-second');
            program.setSpeed(ticksPerSecond.innerText);  // TBD: is innerText the best way to do this?
            runPause.value = "Pause";
            program.run();
        } else {
            program.pause();
            runPause.value = "Run";
        }
    }
}

function stepBtnClick() {
    var runPause = document.getElementById('run-pause');
    if (program !== null && !program.done) {
        program.pause();
        program.tick();
        runPause.value = "Run";
    }
}

function haltRestartBtnClick() {
    if (!program.done) {
        haltProgram();
    } else {
        unloadProgram();
        loadProgram();
    }
}

function permalinkBtnClick() {
    var permalink = generatePermalink();
    // Copy the permalink to the clipboard, and then (whether the copy succeeded or not)
    // go to the permalink URL
    navigator.clipboard.writeText(permalink).then(
        () => location.assign(permalink),
        () => location.assign(permalink)
    );
}

function canvasClick() {
    // TBD
    //unloadProgram();
}

var canvas;
var context;
var program;

window.onload = function() {
    canvas = document.getElementById("playfield");
    context = null;
    program = null;
    loadFromQueryString();
    showEditor();
}
