# ADVERSARIAL PROGRAM DEBUGGING

Dingwall is at it again! This time he told the Eagles that "Hotel California" was a terrible album. As a result, Teshwan assigned his elite squadron of Eagle Hackers to find flaws in Dingwall's accounting software! Now the sloths are losing tons of green (cecropia leaves, their primary food source). Dingwall won't apologize for his opinions about popular music -- he has no choice but to fix the calculator. To do so, Dingwall divided his developers into teams and has assigned them to attack and repair the calculator software in a capture the flag style exercise.

You are a sloth programmer on one of those teams and have been given a copy of the calculator program, calc.c. Your goal is to find errors or incorrect behavior in the calculator program and fix them, while also attacking the calculators of your peers to see if they have fixed the flaws in their own programs.

The winning team is the team with the least number of flaws in their version of calc.c when time runs out.

# Table of Contents

 - [The Game](#the-game)
    - [Fixing Your Code and How to Submit](#fixing-your-code-and-how-to-submit)
    - [Collecting Flaws](#collecting-flaws)
    - [Scoring](#scoring)
 - [Calculator Behavior](#calculator-behavior)
    - [Compiling](#compiling)
    - [Input](#input)
    - [Output](#output)
    - [Handling Errors](#handling-errors)
    - [The Gold Standard](#the-gold-standard)
 - [Rules and Clarifications](#rules-and-clarifications)
 - [Tips and Tricks](#tips-and-tricks)

# THE GAME

You are competing against the other sloth teams to improve your version of calc.c while also attacking theirs. You will find flaws in calc.c and fix them, either improving the code or calling the function error(). At the same time, you will collect "attack strings" -- one attack per file. Those attacks will be automatically executed against the other teams' versions of calc.c. Every flaw in a teams' code will count against their score -- your goal is to be immune to as many flaws as possible.

## Fixing Your Code and How to Submit

Your team will have its own copy of the calc.c source that you can test with input strings. Then, you can fix the flaws you discover in calc.c to make your version more robust. When you have a version of calc.c that you think is improved, you should execute the command `submit`.

The program `submit` will compile your code. Then it will copy your source to the private directory /var/cctf/teamN/src/ and a binary will be copied to the public directory /var/cctf/teamN/bin/. The public binary can be tested by other teams to reveal the flaws in your code.

## Collecting Flaws

Each known flaw that your team discovers should be collected in the directory `/home/teamN/attacks/` (You can also use `~/attacks` to access this directory). You should use your favorite editor to write attack files -- one attack per file. So, for example, if "10 + 2" causes bad behavior, you can write "10 + 2" into a file and call it whatever you want (e.g., 10plus2). The scoring code will consume your attacks to test everyones' code.

## Scoring

Every second, an attack bot will pick the oldest attack from your attack directory and add it to the master list of attacks, stored in the public file /var/cctf/attacklist.txt. It will then remove the attack from your directory. Periodically (say every 30s), a score bot will test ALL public binaries against all the attacks in attacklist.txt. When it tests your binary, it will update a file /var/cctf/dirs/teamN/score.txt showing the attacks you passed and failed (which you can use to determine what needs fixing), and then it will update a file /var/cctf/scoreboard.txt showing how all teams are performing.

The scoreboard will show the number of tests you pass versus the number of attacks in attacklist.txt (i.e., PASS/NUM_ATTACKS). The "winning" team is the team with the score closest to 1 when the competition ends.

# CALCULATOR BEHAVIOR

'calc' is a very simple calculator program without a lot of features. Unfortunately, what it does have is a lot of bugs. Most of these bugs are not security issues, but recall that a program should do what it specifies *and nothing more*. For you to know whether behavior is an error, you need to know what the calculator is designed to do.

## Compiling

Compile calc using:

`make`

## Input

To use the calculator, call calc like so:

`./calc OPERATIONS`

... where `OPERATIONS` is a double quoted list of binary mathematical operations with whitespace separating each token (character) (e.g., A + B). The operations can be addition, subtraction, multiplication and division. The numerical arguments for A and B should be signed short integers, in other words ranging from -32,768 to 32,767.

For example, a valid value for OPERATIONS is:  
`"10 + 2"`

Multiple operations can be separated by a comma:  
`"10 + 2,9 / 3"`

Extra space characters should be ignored. For example:  
`" 10 + 2 , 9 / 3 "`

Tabs do not count as whitespace characters.

## Output

The output of the program is the numeric value of the computations, one per line. For example, with the input "10 + 2,9 / 3", the output would be:

 12  
 3

The output of division operations include the remainder as a simplified fraction. For example, given the input:

 "10 / 7"

... the output would be:

 1 3/7

## Handling Errors

Secure design principles tell us that a program should do what it is designed to do *and nothing more*.

There are basically two types of mistakes in the calc code -- erroneous calculations and undefined behavior. Erroneous calculations are the program not doing what it is designed to do. Undefined behavior includes accepting invalid input.

If an error results in an erroneous calculation, calc.c should be modified to perform the computation correctly. For example, if "-1 + 10" returned "11" instead of "9", then the calculator would need to be modified to handle negative numbers.

If calc.c accepts input it should not, or input causes calc to crash, or any other type of behavior that it shouldn't perform, calc should simply print "Error" and quit. For example, if calc is given no input at all, it should print Error and quit because ignoring a required argument should not be allowed. Similarly, accepting extra arguments that do not conform to the standard described above should also cause an Error to be thrown.

Conveniently, the calc.c code has a function, error() that does just this. Thus, if you encounter an error case such as this, simply call error().

## The Gold Standard

In order to help the sloths, the Vizards of Vim Mountain (led by the powerful Brammoolenaar), provided the sloths with a "perfect" Golden Calculator, called 'gold'. The sloths can use 'gold' to test their calculator's behavior, but due to DRM and other licensing issues, the Vizards won't let the sloths use 'gold' in production. Still, you can run gold with arguments to test the "proper" behavior of the calculator.

Of course, it's likely that you might find flaws in gold that the Vizards overlooked. If that happens, simply cry out the Vizards in a loud voice about the problem, and they'll fix it.

# RULES AND CLARIFICATIONS
 - Your code must not use the "*" operator to do multiplication. It is too fast for sloths.
 - Your code must not use the "/" operator to do integer division. It is too fast and scary for sloths.
 - You must not use any math libraries.
 - TAB characters are not considered whitespace.
 - Exact duplicates of existing attacks will be ignored.

# Tips and Tricks
To login to the server run:  
`ssh teamN@hack.d.umn.edu`

 - Since all team members are running as the same user, you might want to create your own working directory in the team home directory (e.g., `teamN/alice`, `teamN/bob`, etc.) and make your own copies of the file to work on. Otherwise, you will have errors if two people try to edit a file at the same time.
 - Remember to put attacks in `~/attacks` (one line per file)
 - Submit your code by running `submit` in your home directory.
 - To see the current score run `score` or `score -g` for a graph version.
 - To see all the current attacks run: `less /var/cctf/attacklist.txt`
 - To see what tests you pass and fail run: `less /var/cctf/dirs/teamN/score.txt`

