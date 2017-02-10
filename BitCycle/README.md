# BitCycle

A two-dimensional Turing-complete programming language that works by moving bits around a playfield, inspired by [><>](http://esolangs.org/wiki/Fish) and [Bitwise Cyclic Tag](http://esolangs.org/wiki/Bitwise_Cyclic_Tag).

## How it works

A program is a 2D grid of characters (the *playfield*), implicitly right-padded with spaces to form a full rectangle. During execution, *bits* move around this playfield, encountering various *devices* that change their direction, store them, create new bits, etc. All bits move at the same time (once per *tick*). Unlike in ><>, the playfield does not wrap: any bits that exit the playfield are destroyed.

### Direction changing

The devices `<`, `^`, `>`, and `v` change a bit's direction unconditionally, like in ><>.

The device `+` is a conditional direction change. An incoming `0` bit turns left (90 degrees clockwise); an incoming `1` bit turns right (90 degrees counterclockwise).

### Splitters and switches

The devices `\` and `/` are *splitters*. When the first bit hits them, they reflect it 90 degrees, like the mirrors in ><>. After one reflection, though, they change to their *inactive forms* `-` and `|`, which pass bits straight through.

The device `=` is a *switch*. The first bit that hits it passes straight through. If that bit is a `0`, the switch becomes a *left switch* `{`, which redirects all subsequent bits to the left (like `<`). If the bit is a `1`, the switch becomes a *right switch* `}`, which redirects all subsequent bits to the right (like `>`).

All splitters and switches on the playfield reset to their original states whenever one or more collectors come open (see below).

### Collectors

Any letter except `V` is a *collector*. A collector maintains a queue of bits, enqueuing bits as they come in. It has two states, *closed* (represented by an uppercase letter) and *open* (represented by the corresponding lowercase letter). When the collector is closed, incoming bits are stored in the queue. When it is open, bits are dequeued (one per tick) and sent out until the queue is empty, at which point the collector switches back to closed. Bits emerge from the right side of the collector and move rightward.

When there are no bits moving on the playfield (i.e. all the bits are in collectors), the earliest-lettered collector with a nonempty queue comes open. There may be multiple collectors with the same letter, in which case all of them come open at once.

For example: suppose there are four collectors, labeled `A`, `B`, `B`, and `C`, and no bits are moving on the playfield.

- If `A` contains any bits, `A` comes open. Other collectors remain closed, whether they contain any bits or not.
- If `A` is empty, and one or more of the `B` collectors contain bits, *both* `B` collectors come open.
- `C` will not open unless the previous three collectors are all empty.

### Sources and sinks

The device `?` is a *source*. It takes bits from input and sends them out (one per tick) to the right until its input is exhausted. A program may have multiple inputs mapping to multiple `?` devices. For the purposes of determining which input goes to which source, sources are ordered by their appearance in the program top-to-bottom and left-to-right. If a bit hits a `?`, the bit is destroyed.

The device `!` is a *sink*. Any bit that hits it is output and removed from the playfield.

### Other

The device `~`, *dupneg*, creates a negated copy of each incoming bit: if the bit is `0`, the copy is `1`, and vice versa. The original bit turns right, and the copy turns left.

A `0` or `1` in the program places a single bit of the specified type on the playfield at the start of execution, moving right.

When any bit hits the device `@`, the program terminates. The program also terminates if there are no bits remaining, either on the playfield or in collectors. The user can also halt execution with Ctrl-C.

All unassigned characters are no-ops.

Two or more bits can occupy the same space at the same time. The ordering between them if they hit a collector, splitter, switch, or sink simultaneously is undefined.

## Running a BitCycle program

The interpreter, written in Python 3, is `bitcycle.py`. Invoke it with the name of your code file and your inputs as command-line arguments. On Windows:

    python bitcycle.py cyclic_tag.btc 110100 10

On Linux:

    ./bitcycle.py cyclic_tag.btc 110100 10

### Flags

For ease of debugging and/or the pure pleasure of watching the code run, two flags are provided:

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

An input of `0` is directed up to the `+` in the middle, where it turns left and is output by the sink `!`.

An input of `1` turns right at the `+`. It hits the dupneg `~`, which sends it downward and its negated copy upward. The original `1` bit is directed by the `<` and `^` back to the `+`, creating an infinite loop. The `0` is dupneg'd a second time; it turns rightward off the playfield, while its negated copy `1` goes left, then down into the `!` to be output.

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