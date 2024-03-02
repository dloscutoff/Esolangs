
// Define magic numbers and other constants

const WEST = 0;
const NORTH = 1;
const EAST = 2;
const SOUTH = 3;

const BIT_SHAPE_RADIUS = 7;
const QUEUE_BIT_SCALE = 0.25;
const GRID_SQUARE_SIZE = 24;
const GRID_FONT_SIZE = 14;

const DEFAULT_TICKS_PER_SECOND = 10;
const DEFAULT_FRAMES_PER_TICK = 1;

const BLUE = "#ABF";
const GREEN = "#6E6";
const TEAL = "#4A9";
const BLACK = "#000";
const WHITE = "#FFF";

const COLLECTOR_NAMES = "ABCDEFGHIJKLMNOPQRSTUWXYZ";
const SIMPLE_DEVICES = ">^<v~+={}/\\|-@";

const PLAIN_CHARS = "@! {>\\/|-^=}?\nv+<.~&`()[]#:;,*\"$'%";
const ENCODED_CHARS = Object.freeze("abcdeijlmnopqrstwxz_A_B_C_D_E_F_H_I_J_L_O_Q_S_T_X".match(/_?./g));

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
function Collector(x, y, chr) {
    this.x = x;
    this.y = y;
    this.chr = chr.toUpperCase();
    this.open = false;
    this.queue = [];
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
    this.queue = inputString.split("").map(value => new Bit(this.x, this.y, EAST, value));
    this.open = (this.queue.length > 0);
}

Source.prototype.tick = function() {
    var outBit = null;
    if (this.open) {
        outBit = this.queue.shift();
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
function Sink(x, y, idNumber, ioFormat) {
    this.x = x;
    this.y = y;
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
        if (outputArea.innerHTML !== "") {
            outputArea.innerHTML += ",<wbr />";
        }
        outputArea.innerHTML += unaryToInt(this.buffer);
    } else if (this.ioFormat === "signed") {
        if (outputArea.innerHTML !== "") {
            outputArea.innerHTML += ",<wbr />";
        }
        outputArea.innerHTML += signedUnaryToInt(this.buffer);
    }
    this.buffer = "";
}

Sink.prototype.toString = function() {
    return "!";
}

// Define Device class for generic devices that aren't Collectors, Sources, or Sinks
function Device(x, y, chr) {
    this.x = x;
    this.y = y;
    this.chr = chr;
}

Device.prototype.toString = function() {
    return this.chr;
}

// Define Program class
function Program(codeLines, inputLines, ticksPerSecond, framesPerTick, ioFormat, expand) {
    var sinkNumber = 0;
    
    this.setSpeed(ticksPerSecond, framesPerTick);
    this.frame = 0;
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
                    var collector = new Collector(x, y, chr);
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
                    var sink = new Sink(x, y, sinkNumber, ioFormat);
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
                    row.push(new Device(x, y, " "));
                } else if (SIMPLE_DEVICES.indexOf(chr) > -1) {
                    // A device without any storage capacity
                    row.push(new Device(x, y, chr));
                } else {
                    row.push(new Device(x, y, chr));
                }
            } else {
                row.push(new Device(x, y, " "));
            }
        }
        this.grid.push(row);
    }
}

Program.prototype.setSpeed = function(ticksPerSecond, framesPerTick) {
    // Don't modify the speed directly in case we're in the middle of a step;
    // instead, set attributes-in-waiting that will be copied over at the
    // beginning of the next step
    ticksPerSecond = Math.max(ticksPerSecond, 0);
    framesPerTick = Math.max(framesPerTick, 0);
    this._ticksPerSecond = Math.abs(ticksPerSecond) || this.ticksPerSecond || DEFAULT_TICKS_PER_SECOND;
    this._framesPerTick = Math.abs(framesPerTick) || this.framesPerTick || DEFAULT_FRAMES_PER_TICK;
    this._speed = this._ticksPerSecond * this._framesPerTick;
}

Program.prototype.run = function() {
    this.paused = false;
    this.step();
    if (!this.done) {
        this.timeout = window.setTimeout(this.run.bind(this), 1000 / this.speed);
    }
}

Program.prototype.step = function() {
    // Update the program speed, in case it's been modified since the last step
    this.ticksPerSecond = this._ticksPerSecond;
    this.framesPerTick = this._framesPerTick;
    this.speed = this._speed;
    
    // Step one frame forward
    this.frame++;
    
    if (this.frame >= this.framesPerTick) {
        // Move the program state forward one tick and display the current
        // state of the playfield
        this.tick();
    } else {
        // Display the current state of the playfield
        this.displayPlayfield();
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
                            if (bit.value) {
                                bit.direction = turnRight(bit.direction);
                            } else {
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
                            // to } if bit is 1, { if 0
                            if (bit.value) {
                                device.chr = "}";
                            } else {
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
    this.frame = 0;
    this.displayPlayfield();
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

Program.prototype.displayPlayfield = function() {
    clearCanvas();
    // Display all zero bits on the playfield first, followed by all one bits
    for (var bitType = 0; bitType <= 1; bitType++) {
        for (var b = 0; b < this.activeBits.length; b++) {
            if (this.activeBits[b].value === bitType) {
                drawBitOffset(this.activeBits[b], this.frame / this.framesPerTick );
            }
        }
    }
    // Then display devices
    for (var y = 0; y < this.grid.length; y++) {
        var row = this.grid[y];
        for (var x = 0; x < row.length; x++) {
            var device = row[x];
            drawDevice(device);
        }
    }
}

function clearCanvas() {
    if (context !== null) {
        context.clearRect(0, 0, canvas.width, canvas.height);
    }
}

function drawBitOffset(bit, offsetAmount) {
    var x = bit.x + 0.5 + dx(bit.direction) * offsetAmount;
    var y = bit.y + 0.5 + dy(bit.direction) * offsetAmount;
    drawBitAt(bit, x, y);
}

function drawDevice(device) {
    drawDeviceAt(device, device.x + 0.5, device.y + 0.5);
    if (device instanceof Collector || device instanceof Source) {
        if (device.queue.length > 0) {
            drawQueueAt(device.queue, device.x + 0.5, device.y + 1/7);
        }
    }
}

function drawBitAt(bit, x, y, scale=1) {
    // Draw a green diamond for a 1 bit, blue circle for a 0 bit
    if (bit.value) {
        drawDiamond(x * GRID_SQUARE_SIZE, y * GRID_SQUARE_SIZE, BIT_SHAPE_RADIUS * scale, GREEN);
    } else {
        drawCircle(x * GRID_SQUARE_SIZE, y * GRID_SQUARE_SIZE, BIT_SHAPE_RADIUS * scale, BLUE);
    }
}

function drawDeviceAt(device, x, y) {
    drawCharacter(device.toString(), x * GRID_SQUARE_SIZE, y * GRID_SQUARE_SIZE, BLACK);
}

function drawQueueAt(queue, x, y) {
    // Show up to first 6 bits in queue above device with a white background
    drawRectangle(x * GRID_SQUARE_SIZE, y * GRID_SQUARE_SIZE, GRID_SQUARE_SIZE, GRID_SQUARE_SIZE / 6, WHITE);
    for (let i = 0; i < Math.min(queue.length, 6); i++) {
        let bit = queue[i];
        drawBitAt(bit, x + 0.5 - (i + 1) / 7, y, QUEUE_BIT_SCALE);
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

function drawCharacter(character, x, y, color) {
    context.fillStyle = color;
    context.fillText(character, x - 0.3 * GRID_FONT_SIZE, y + 0.25 * GRID_FONT_SIZE);
}

function drawRectangle(x, y, width, height, color) {
    context.fillStyle = color;
    context.beginPath();
    context.moveTo(x - width / 2, y - height / 2);
    context.lineTo(x + width / 2, y - height / 2);
    context.lineTo(x + width / 2, y + height / 2);
    context.lineTo(x - width / 2, y + height / 2);
    context.fill();
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
            sourceCode.value = unpackCode(value);
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
        ["p", packCode(sourceCode.value)],
        ["i", urlEncode(inputs.value)],
        ["f", ioFormatSelect.selectedIndex]
    ].filter(([key, value]) => value).map(pair => pair.join("="));
    return "?" + params.join("&");
}

function generatePermalink() {
    return location.origin + location.pathname + generateQueryString();
}

function packCode(unpackedCode) {
    var packedCode;
    unpackedCode = unpackedCode.replaceAll(/[^ -~\n]/g, ".");
    packedCode = unpackedCode.replaceAll(/(.|\n)\1{0,8}/g, run => {
        var i = PLAIN_CHARS.indexOf(run[0]);
        var e;
        if (i >= 0) {
            e = ENCODED_CHARS[i];
        } else if (/[A-Z01]/.test(run)) {
            e = run[0];
        } else {
            e = "_" + run[0];
        }
        if (run.length === 1) {
            return e;
        } else {
            return e + run.length;
        }
    });
    return packedCode;
}

function unpackCode(packedCode) {
    var unpackedCode;
    unpackedCode = packedCode.replaceAll(/(_?.)([2-9]?)/g, (m, e, num) => {
        var i = ENCODED_CHARS.indexOf(e);
        var c;
        if (i >= 0) {
            c = PLAIN_CHARS[i];
        } else {
            c = e.slice(-1);
        }
        if (num === "") {
            num = 1;
        } else {
            num = +num;
        }
        return c.repeat(num);
    });
    return unpackedCode;
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

function toggleCheatSheet() {
    var cheatSheet = document.getElementById('cheat-sheet'),
        indicator = document.getElementById('cheat-sheet-indicator');
    
    if (cheatSheet.classList.contains("hide")) {
        cheatSheet.classList.remove("hide");
        indicator.innerText = "-";
    } else {
        cheatSheet.classList.add("hide");
        indicator.innerText = "+";
    }
}

function loadProgram() {
    var sourceCode = document.getElementById('source'),
        ticksPerSecond = document.getElementById('ticks-per-second'),
        framesPerTick = document.getElementById('frames-per-tick'),
        inputs = document.getElementById('inputs'),
        ioFormatSelect = document.getElementById('io-format'),
        expand = document.getElementById('expand'),
        runPause = document.getElementById('run-pause'),
        step = document.getElementById('step'),
        tick = document.getElementById('tick'),
        done = document.getElementById('done'),
        haltRestart = document.getElementById('halt-restart');
    
    program = new Program(
        sourceCode.value.split(/\r?\n/),
        inputs.value.split(/\r?\n/),
        ticksPerSecond.value,
        framesPerTick.value,
        ioFormatSelect.value,
        expand.checked
    );
    
    // Set up the canvas
    canvas.height = program.height * GRID_SQUARE_SIZE;
    canvas.width = program.width * GRID_SQUARE_SIZE;
    context = canvas.getContext("2d");
    context.font = "bold " + GRID_FONT_SIZE + "px Courier New";
    
    // Display the current state of the playfield
    program.displayPlayfield();
    
    runPause.style.display = "block";
    step.style.display = "block";
    if (framesPerTick.value > 1) {
        tick.style.display = "block";
    } else {
        tick.style.display = "none";
    }
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
        tick = document.getElementById('tick'),
        done = document.getElementById('done'),
        haltRestart = document.getElementById('halt-restart');
    
    program.halt();
    
    runPause.style.display = "none";
    step.style.display = "none";
    tick.style.display = "none";
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
        program.step();
        runPause.value = "Run";
    }
}

function tickBtnClick() {
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

function speedInputChange() {
    var ticksPerSecond = document.getElementById('ticks-per-second'),
        framesPerTick = document.getElementById('frames-per-tick'),
        tick = document.getElementById('tick');
    program.setSpeed(ticksPerSecond.value, framesPerTick.value);
    if (framesPerTick.value > 1) {
        tick.style.display = "block";
    } else {
        tick.style.display = "none";
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
