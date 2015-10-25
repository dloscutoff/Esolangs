// Define Stack class

function Stack() {
    this.stack = [];
    this.length = 0;
}

Stack.prototype.push = function(item) {
    this.stack.push(item);
    this.length++;
}

Stack.prototype.pop = function() {
    var result = 0;
    if (this.length > 0) {
        result = this.stack.pop();
        this.length--;
    }
    return result;
}

Stack.prototype.top = function() {
    var result = 0;
    if (this.length > 0) {
        result = this.stack[this.length - 1];
    }
    return result;
}

Stack.prototype.toString = function() {
    return "" + this.stack;
}

// Define Snake class
function Snake(code) {
    this.code = code;
    this.length = this.code.length;
    this.ip = 0;
    this.ownStack = new Stack();
    this.currStack = this.ownStack;
    this.alive = true;
    this.wait = 0;
    this.partialString = this.partialNumber = null;
}

Snake.prototype.step = function() {
    if (!this.alive) {
        return null;
    }
    if (this.wait > 0) {
        this.wait--;
        return null;
    }
    var instruction = this.code.charAt(this.ip);
    var output = null;
    console.log("Executing instruction " + instruction);
    if (this.partialString !== null) {
        // We're in the middle of a double-quoted string
        if (instruction == '"') {
            // Close the string and push its character codes in reverse order
            for (var i = this.partialString.length - 1; i >= 0; i--) {
                this.currStack.push(this.partialString.charCodeAt(i));
            }
            this.partialString = null;
        } else {
            this.partialString += instruction;
        }
    } else if (instruction == '"') {
        this.partialString = "";
    } else if ("0" <= instruction && instruction <= "9") {
        if (this.partialNumber !== null) {
            this.partialNumber = this.partialNumber + instruction;  // NB: concatenation!
        } else {
            this.partialNumber = instruction;
        }
        next = this.code.charAt((this.ip + 1) % this.length);
        if (next < "0" || "9" < next) {
            // Next instruction is non-numeric, so end number and push it
            this.currStack.push(+this.partialNumber);
            this.partialNumber = null;
        }
    } else if ("a" <= instruction && instruction <= "f") {
        // a-f push numbers 10 through 15
        var value = instruction.charCodeAt(0) - 87;
        this.currStack.push(value);
    } else if (instruction == "$") {
        // Toggle the current stack
        if (this.currStack === this.ownStack) {
            this.currStack = this.program.sharedStack;
        } else {
            this.currStack = this.ownStack;
        }
    } else if (instruction == "s") {
        this.currStack = this.ownStack;
    } else if (instruction == "S") {
        this.currStack = this.program.sharedStack;
    } else if (instruction == "l") {
        this.currStack.push(this.ownStack.length);
    } else if (instruction == "L") {
        this.currStack.push(this.program.sharedStack.length);
    } else if (instruction == ".") {
        var item = this.currStack.pop();
        this.currStack.push(item);
        this.currStack.push(item);
    } else if (instruction == "m") {
        var item = this.ownStack.pop();
        this.program.sharedStack.push(item);
    } else if (instruction == "M") {
        var item = this.program.sharedStack.pop();
        this.ownStack.push(item);
    } else if (instruction == "y") {
        var item = this.ownStack.top();
        this.program.sharedStack.push(item);
    } else if (instruction == "Y") {
        var item = this.program.sharedStack.top();
        this.ownStack.push(item);
    } else if (instruction == "\\") {
        var top = this.currStack.pop();
        var next = this.currStack.pop()
        this.currStack.push(top);
        this.currStack.push(next);
    } else if (instruction == "@") {
        var c = this.currStack.pop();
        var b = this.currStack.pop();
        var a = this.currStack.pop();
        this.currStack.push(c);
        this.currStack.push(a);
        this.currStack.push(b);
    } else if (instruction == ";") {
        this.currStack.pop();
    } else if (instruction == "+") {
        var b = this.currStack.pop();
        var a = this.currStack.pop();
        this.currStack.push(a + b);
    } else if (instruction == "-") {
        var b = this.currStack.pop();
        var a = this.currStack.pop();
        this.currStack.push(a - b);
    } else if (instruction == "*") {
        var b = this.currStack.pop();
        var a = this.currStack.pop();
        this.currStack.push(a * b);
    } else if (instruction == "/") {
        var b = this.currStack.pop();
        var a = this.currStack.pop();
        this.currStack.push(a / b);
    } else if (instruction == "%") {
        var b = this.currStack.pop();
        var a = this.currStack.pop();
        this.currStack.push(a % b);
    } else if (instruction == "_") {
        this.currStack.push(-this.currStack.pop());
    } else if (instruction == "I") {
        var value = this.currStack.pop();
        if (value < 0) {
            this.currStack.push(Math.ceil(value));
        } else {
            this.currStack.push(Math.floor(value));
        }
    } else if (instruction == ">") {
        var b = this.currStack.pop();
        var a = this.currStack.pop();
        this.currStack.push(+(a > b));
    } else if (instruction == "<") {
        var b = this.currStack.pop();
        var a = this.currStack.pop();
        this.currStack.push(+(a < b));
    } else if (instruction == "=") {
        var b = this.currStack.pop();
        var a = this.currStack.pop();
        this.currStack.push(+(a == b));
    } else if (instruction == "!") {
        this.currStack.push(+ !this.currStack.pop());
    } else if (instruction == "?") {
        this.currStack.push(Math.random());
    } else if (instruction == "n") {
        output = "" + this.currStack.pop();
    } else if (instruction == "o") {
        output = String.fromCharCode(this.currStack.pop());
    } else if (instruction == "r") {
        var input = this.program.io.getNumber();
        this.currStack.push(input);
    } else if (instruction == "i") {
        var input = this.program.io.getChar();
        this.currStack.push(input);
    } else if (instruction == "(") {
        this.length -= Math.floor(this.currStack.pop());
        this.length = Math.max(this.length, 0);
    } else if (instruction == ")") {
        this.length += Math.floor(this.currStack.pop());
        this.length = Math.min(this.length, this.code.length);
    } else if (instruction == "w") {
        this.wait = this.currStack.pop();
    } else {
        console.log("Hit else case");
    }
    if (this.ip >= this.length) {
        // We've swallowed the IP, so this snake dies
        this.alive = false;
        this.program.snakesLiving--;
    } else {
        // Increment IP and loop if appropriate
        this.ip = (this.ip + 1) % this.length;
    }
    return output;
}

Snake.prototype.getHighlightedCode = function() {
    var result = "";
    for (var i = 0; i < this.code.length; i++) {
        if (i == this.length) {
            result += '<span class="swallowedCode">';
        }
        if (i == this.ip) {
            if (this.wait > 0) {
                result += '<span class="nextActiveToken">';
            } else {
                result += '<span class="activeToken">';
            }
            result += escapeEntities(this.code.charAt(i)) + '</span>';
        } else {
            result += escapeEntities(this.code.charAt(i));
        }
    }
    if (this.length < this.code.length) {
        result += '</span>';
    }
    return result;
}

// Define Program class
function Program(source, speed, io) {
    this.sharedStack = new Stack();
    this.snakes = source.split(/\r?\n/).map(function(snakeCode) {
        var snake = new Snake(snakeCode);
        snake.program = this;
        snake.sharedStack = this.sharedStack;
        return snake;
    }.bind(this));
    this.snakesLiving = this.snakes.length;
    this.io = io;
    this.speed = speed || 10;
    this.halting = false;
}

Program.prototype.run = function() {
    this.step();
    if (this.snakesLiving) {
        this.timeout = window.setTimeout(this.run.bind(this), 1000 / this.speed);
    }
}

Program.prototype.step = function() {
   for (var s = 0; s < this.snakes.length; s++) {
        var output = this.snakes[s].step();
        if (output) {
            this.io.print(output);
        }
    }
    this.io.displaySource(this.snakes.map(function (snake) {
            return snake.getHighlightedCode();
        }).join("<br>"));
 }

Program.prototype.halt = function() {
    window.clearTimeout(this.timeout);
}

var ioFunctions = {print: function (item) {
                           var stdout = document.getElementById('stdout');
                           stdout.value += "" + item;
                       },
                   getChar: function () {
                           if (inputData) {
                               var inputChar = inputData[0];
                               inputData = inputData.slice(1);
                               result = inputChar.charCodeAt(0);
                           } else {
                               result = -1;
                           }
                           var stdinDisplay = document.getElementById('stdin-display');
                           stdinDisplay.innerHTML = escapeEntities(inputData);
                           return result;
                       },
                   getNumber: function () {
                           while (inputData && (inputData[0] < "0" || "9" < inputData[0])) {
                               inputData = inputData.slice(1);
                           }
                           if (inputData) {
                               var inputNumber = inputData.match(/\d+/)[0];
                               inputData = inputData.slice(inputNumber.length);
                               result = +inputNumber;
                           } else {
                               result = -1;
                           }
                           var stdinDisplay = document.getElementById('stdin-display');
                           stdinDisplay.innerHTML = escapeEntities(inputData);
                           return result;
                       },
                   displaySource: function (formattedCode) {
                           var sourceDisplay = document.getElementById('source-display');
                           sourceDisplay.innerHTML = formattedCode;
                       }
                   };

var program = null;
var inputData = null;

function showEditor() {
    var source = document.getElementById('source'),
        sourceDisplayWrapper = document.getElementById('source-display-wrapper'),
        stdin = document.getElementById('stdin'),
        stdinDisplayWrapper = document.getElementById('stdin-display-wrapper');
    
    source.style.display = "block";
    stdin.style.display = "block";
    sourceDisplayWrapper.style.display = "none";
    stdinDisplayWrapper.style.display = "none";
    
    source.focus();
}

function hideEditor() {
    var source = document.getElementById('source'),
        sourceDisplay = document.getElementById('source-display'),
        sourceDisplayWrapper = document.getElementById('source-display-wrapper'),
        stdin = document.getElementById('stdin'),
        stdinDisplay = document.getElementById('stdin-display'),
        stdinDisplayWrapper = document.getElementById('stdin-display-wrapper');
    
    source.style.display = "none";
    stdin.style.display = "none";
    sourceDisplayWrapper.style.display = "block";
    stdinDisplayWrapper.style.display = "block";
    
    var sourceHeight = getComputedStyle(source).height,
        stdinHeight = getComputedStyle(stdin).height;
    //alert("sourceHeight = " + sourceHeight + ", stdinHeight = " + stdinHeight);
    sourceDisplayWrapper.style.minHeight = sourceHeight;
    sourceDisplayWrapper.style.maxHeight = sourceHeight;
    stdinDisplayWrapper.style.minHeight = stdinHeight;
    stdinDisplayWrapper.style.maxHeight = stdinHeight;

    sourceDisplay.textContent = source.value;
    stdinDisplay.textContent = stdin.value;
}

function escapeEntities(input) {
    return input.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function resetProgram() {
    var stdout = document.getElementById('stdout');
    stdout.value = null;
    if (program !== null) {
        program.halt();
    }
    program = null;
    inputData = null;
    showEditor();
}

function initProgram() {
    var source = document.getElementById('source'),
        stepsPerSecond = document.getElementById('steps-per-second'),
        stdin = document.getElementById('stdin');
    program = new Program(source.value, +stepsPerSecond.innerHTML, ioFunctions);
    hideEditor();
    inputData = stdin.value;
}

function runBtnClick() {
    if (program === null || program.snakesLiving == 0) {
        resetProgram();
        initProgram();
    } else {
        program.halt();
        var stepsPerSecond = document.getElementById('steps-per-second');
        program.speed = +stepsPerSecond.innerHTML;
    }
    program.run();
}

function stepBtnClick() {
    if (program === null) {
        initProgram();
    } else {
        program.halt();
    }
    program.step();
}

function sourceDisplayClick() {
    resetProgram();
}