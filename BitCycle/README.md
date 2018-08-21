# BitCycle

A two-dimensional Turing-complete programming language that works by moving bits around a playfield, inspired by [><>](http://esolangs.org/wiki/Fish) and [Bitwise Cyclic Tag](http://esolangs.org/wiki/Bitwise_Cyclic_Tag).

## How it works

A program is a 2D grid of characters (the *playfield*), implicitly right-padded with spaces to form a full rectangle. During execution, *bits* move around this playfield, encountering various *devices* that change their direction, store them, create new bits, etc. All bits move at the same time (once per *tick*). Unlike in ><>, the playfield does not wrap: any bits that exit the playfield are destroyed.

### Direction changing

The devices `<`, `^`, `>`, and `v` change a bit's direction unconditionally, like in ><>.

The device `+` is a conditional direction change. An incoming `0` bit turns left; an incoming `1` bit turns right.

### Splitters and switches

The devices `\` and `/` are *splitters*. When the first bit hits them, they reflect it 90 degrees, like the mirrors in ><>. After one reflection, though, they change to their *inactive forms* `-` and `|`, which pass bits straight through.

The device `=` is a *switch*. The first bit that hits it passes straight through. If that bit is a `0`, the switch becomes `{`, which redirects all subsequent bits to the west (like `<`). If the bit is a `1`, the switch becomes `}`, which redirects all subsequent bits to the east (like `>`).

All splitters and switches on the playfield reset to their original states whenever one or more collectors come open (see below).

### Collectors

Any letter except `V`/`v` is a *collector*. A collector maintains a queue of bits. It has two states, *closed* (represented by an uppercase letter) and *open* (represented by the corresponding lowercase letter). In both states, bits that hit the collector are added to the end of its queue. When the collector is closed, bits stay in the queue. When it is open, bits are dequeued (one per tick) and sent out eastward from the collector. An open collector stays open until all its bits have been dequeued (including any that may have come in while it was open), at which point it switches back to closed.

There may be multiple collectors with the same letter. Each collector has a separate queue.

When there are no bits moving on the playfield (i.e. all the bits are in collectors), the program finds the earliest-lettered collector with a nonempty queue. All collectors with that letter come open.

For example: suppose there are four collectors, labeled `A`, `B`, `B`, and `C`, and no bits are moving on the playfield.

- If `A` contains any bits, `A` comes open. Other collectors remain closed, whether they contain any bits or not.
- If `A` is empty, and one or more of the `B` collectors contain bits, *both* `B` collectors come open.
- `C` cannot open unless the previous three collectors are all empty.

Once a collector is open, it stays open until its queue is emptied; but a closed collector will only open when there are no bits active on the playfield.

### Sources and sinks

The device `?` is a *source*. It takes bits from input and sends them out eastward (one per tick) until its input is exhausted. A program may have multiple inputs mapping to multiple `?` devices. For the purposes of determining which input goes to which source, sources are ordered by their appearance in the program top-to-bottom and left-to-right. If a bit hits a `?`, the bit is destroyed.

The device `!` is a *sink*. Any bit that hits it is output and removed from the playfield.

Conceptually, the inputs and the output are sequences of bits. For specifics on I/O methods, see below.

### Other

The device `~`, *dupneg*, creates a negated copy of each incoming bit: if the bit is `0`, the copy is `1`, and vice versa. The original bit turns right, and the copy turns left.

A `0` or `1` in the program places a single bit of the specified type on the playfield at the start of execution, moving east.

When any bit hits the device `@`, the program terminates. The program also terminates if there are no bits remaining, either on the playfield or in collectors. The user can also halt execution with Ctrl-C.

All unassigned characters are no-ops.

Two or more bits can occupy the same space at the same time. The ordering between them if they hit a collector, splitter, switch, or sink simultaneously is undefined.

## Running a BitCycle program

The interpreter, written in Python 3, is `bitcycle.py`. Invoke it with the name of your code file and your inputs as command-line arguments. On Windows:

    python bitcycle.py cyclic_tag.btc 110100 10

On Linux:

    ./bitcycle.py cyclic_tag.btc 110100 10

### Flags

Command-line flags must be specified before the code file name.

Two flags allow for decimal I/O:

- `-u` converts each command-line argument from a list of nonnegative decimal integers (e.g. `1,2,0,3`) to a series of unary numbers separated by `0`s (`101100111`), and performs the reverse transformation on the output.
- `-U` converts each command-line argument from a list of signed decimal integers to a series of *signed unary* numbers separated by `0`s. Signed unary represents each number with a leading `0` for negative numbers and zero, followed by the unary representation of the number's absolute value: `2` => `11`, `-2` => `011`, `0` => `0`. A command-line argument of `1,-2,0,3` would correspond to the signed unary numbers `1`, `011`, `0`, and `111`, and therefore the program's input would be `10011000111`. The reverse transformation is performed on the output.

Note for using the `-U` flag: if your first command-line input starts with a minus sign, you may need to include `--` before it so the interpreter doesn't try to interpret it as a flag.

Two flags are provided for ease of debugging and/or the pure pleasure of watching the code run:

- `-s` manually steps through the program, requiring the user to press enter at each tick
- `-p num` pauses for `num` seconds after each tick

Both of these options display the state of the playfield and the output at each tick.

## Example programs

### [Cat](http://esolangs.org/wiki/Cat_program)

    ?!

Bits from the source `?` proceed directly into the sink `!`.

### [Truth-machine](http://esolangs.org/wiki/Truth-machine)

    v ~
    !+~
    ?^<

An input of `0` is directed up to the `+` in the middle, where it turns left (west) and is output by the sink `!`.

An input of `1` turns right (east) at the `+` and hits the dupneg `~`, which makes it turn right (south) and its negated copy left (north). The original `1` bit is directed by the `<` and `^` back to the `+`, creating an infinite loop. The `0` is dupneg'd a second time; it turns right (east) and drops off the playfield, while its negated copy `1` goes left (west), then down into the `!` to be output.

### [Bitwise Cyclic Tag](http://esolangs.org/wiki/Bitwise_Cyclic_Tag) interpreter

We can show that BitCycle is Turing-complete by presenting an implementation of the Turing-complete language Bitwise Cyclic Tag:

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

The first input is the program-string and the second input is the data-string. This implementation requires the program-string to be at least two bits; in place of a program-string of `0` or `1`, use the equivalent program-strings `00` or `11`, respectively. The above BitCycle code will run the BCT program, outputting data-bits as they are deleted, and halting when the data-string is empty.