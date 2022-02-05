
window.onload = function() {
    var rawCode = document.getElementById("raw-code");
    rawCode.oninput = function() {
        var formattedCode = document.getElementById("formatted-code");
        // Highlight the raw code and put into formattedCode
        formattedCode.innerHTML = formatProgram(this.value);
        // If the raw code ends with a blank line, we have to add an
        // extra newline at the end of formattedCode to get the last
        // blank line to show up
        if (/(^|\n)$/.test(this.value)) {
            formattedCode.innerHTML += "\n";
        }
        // Adjust rawCode's height to match the size of its contents
        this.style.height = "";
        this.style.height = (this.scrollHeight + 2) + "px";
    }
    rawCode.oninput();
    rawCode.focus();
}

function formatProgram(code) {
    var bracketId = 0;
    if (isMultiline(code)) {
        // In multiline mode, treat the whole program as a single unit
        // (only infer parentheses at the end)
        return formatSection(code, bracketId)[0];
    } else {
        // In single-line mode, treat each line as a single unit
        // (infer parentheses at the end of each line)
        var formattedSection;
        var formattedSections = [];
        for (const line of code.split("\n")) {
            [formattedSection, bracketId] = formatSection(line, bracketId);
            formattedSections.push(formattedSection);
        }
        return formattedSections.join("\n");
    }
}

function isMultiline(code) {
    // Determine whether the code is in single-line or multiline form:
    // In single-line form, the code is parsed one line at a time
    // with closing parentheses inferred at the end of each line.
    // In multiline form, the code is parsed as a whole, with closing
    // parentheses inferred only at the end. If any line in the code
    // contains more closing parens than opening parens, the code is
    // assumed to be in multiline form; otherwise, it's single-line
    return code.split("\n").some(line => line.split(")").length > line.split("(").length);
}

function formatSection(code, bracketId) {
    var tokens = tokenize(code);
    var formattedCode = "";
    var parsedExpr;
    while (tokens.length > 0) {
        [parsedExpr, bracketId] = parseExpr(tokens, bracketId);
        formattedCode += parsedExpr;
    }
    return [formattedCode, bracketId];
}

function tokenize(code) {
    return [...code.matchAll(/[()]|\s|[^()\s]+/g)].map(m => m[0]);
}

function parseExpr(tokens, bracketId) {
    var formattedExpr = "";
    if (tokens.length > 0) {
        var token = tokens.shift();
        if (token === "(") {
            // Parse the whole parenthesized expression recursively
            var currentBracketId = bracketId;
            formattedExpr += formatBracket(token, currentBracketId);
            formattedExpr += `<div id="grp-${currentBracketId}" class="bracket-contents">`;
            bracketId++;
            while (tokens.length > 0 && tokens[0] !== ")") {
                var subexpr;
                [subexpr, bracketId] = parseExpr(tokens, bracketId);
                formattedExpr += subexpr;
            }
            formattedExpr += `</div>`;
            if (tokens.length > 0) {
                formattedExpr += formatBracket(tokens.shift(), currentBracketId);
            } else {
                formattedExpr += formatBracket(")", currentBracketId, true);
            }
        } else if (token === ")") {
            // If execution ever gets here, we've got an unmatched close-paren
            formattedExpr = `<span class="unmatched-bracket" title="Unmatched parenthesis">${token}</span>`;
        } else {
            // Any token that's not a parenthesis is an atom
            formattedExpr = formatToken(token);
        }
    }
    return [formattedExpr, bracketId];
}

function formatBracket(bracket, bracketId, isImplied) {
    var mouseover = "";
    var cssClass = "bracket";
    if (isImplied) {
        cssClass += " implied";
        mouseover = `title="Implied parenthesis"`;
    }
    return `<span id="${bracket}-${bracketId}" class="${cssClass}" ${mouseover} onmouseover="bracketMouseOver.bind(this)()" onmouseout="bracketMouseOut.bind(this)()">${bracket}</span>`;
}

function formatToken(token) {
    var tokenType, hoverText;
    if (/^\s+$/.test(token)) {
        // Whitespace doesn't need to be highlighted at all
        return token;
    } else {
        if (/^\d+$/.test(token)) {
            tokenType = "number";
            hoverText = "Integer literal";
        } else if (/^(?:[acdehilqstv]|string|chars|disp|type|load|comment)$/.test(token)) {
            tokenType = "builtin";
            hoverText = "Builtin";
        } else if (/^(?:cons|head|car|tail|cdr|add2|sub2|less\?|equal\?|def|if|eval|nil)$/.test(token)) {
            tokenType = "alias";
            hoverText = "Library alias for builtin";
        } else if (/^(?:Int|List|Name|Builtin|list|macro|lambda|quote|neg|dec|inc|nil\?|zero\?|greater\?|positive\?|negative\?|type\?|cadr|cddr|htail|ttail|not|both|either|neither|_?length|nth|last|_?reverse|concat|_?insert|insert-end|contains\?|_?count-occurrences|_?(?:first|last)-index|_?all-indices|_?quote-each|_?substitute|_?(?:reverse-)?inclusive-range|[01]to|to[01]|range|_?repeat-val|all|any|apply|_?map\*?|_?filter|_?take-while|_?foldl|foldl-default|_?chain-last|partial|add-n(?:-2)?|abs|[-+*/]|sum|_?powers-of-2|_mul2-binary|mul2|product|_(?:div2|mod)-(?:positive|negative)|div2|mod|_?divides\?|even\?|odd\?|pow|_gcd-nonnegative|gcd|_?(?:to|from)-base|(?:max|min)2?|factorial|_?prime(?:\?|-factors)|_?main-diagonal|trace|_?transpose(?:-default)?|zip|_each-head-or-default|_?insertion-sort|_insert-in-sorted|_merge-sorted|_partition(?:-by-pivot)|merge-sort|single-char|spc|nl|strlen|strcat|starts-with\?|join2?)$/.test(token)) {
            tokenType = "lib-fn";
            hoverText = "Library function";
        } else {
            tokenType = "name";
            hoverText = "Name";
        }
        if (hoverText !== null) {
            return `<span class="${tokenType}" title="${hoverText}">${htmlEscape(token)}</span>`;
        } else {
            return `<span class="${tokenType}">${htmlEscape(token)}</span>`;
        }
    }
}

function htmlEscape(token) {
    return token.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
}

function bracketMouseOver() {
    var [bracketType, bracketNumber] = this.id.split("-");
    var otherBracketType = bracketType === "(" ? ")" : "(";
    var otherBracket = document.getElementById(`${otherBracketType}-${bracketNumber}`);
    var contents = document.getElementById(`grp-${bracketNumber}`);
    otherBracket.classList.add("primary-highlight");
    contents.classList.add("secondary-highlight");
}

function bracketMouseOut() {
    var [bracketType, bracketNumber] = this.id.split("-");
    var otherBracketType = bracketType === "(" ? ")" : "(";
    var otherBracket = document.getElementById(`${otherBracketType}-${bracketNumber}`);
    var contents = document.getElementById(`grp-${bracketNumber}`);
    otherBracket.classList.remove("primary-highlight");
    contents.classList.remove("secondary-highlight");
}
