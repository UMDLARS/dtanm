# Echo Challenge

The sloths and the eagles are at all-out war. The eagles control the skies and
have managed to get the sloths completely surrounded. Now the sloths have
decided to engage in some psychological warfare: they will escalate the conflict
by simply repeating everything the eagles say until the eagles go mad. The
eagles, of course, are determined to test the limits of this mockery, and have
set their foremost experts to coming up with phrases like "Sloths smell funny"
which can be said by the eagles but not echoed by the sloths, turning their own
devastating psychological warfare against them!

Of course, all of this is happening on the computer. You are one of the sloth
programmers tasked with writing the program to repeat everything said by the
eagles. Your goal is to make sure that your program echoes exactly the input
given under every condition.

### THE GAME

You are tasked with finding issues in the `echo` program and fixing them, while
simultaneously identifying the sources of these bugs and writing "attacks" that
exploit them, and that other teams won't pass. Your score is the count of those
attacks that you pass.

### Fixing Your Code and How to Submit

Your team will have its own copy of the `echo` source that you can test with
input strings. Then, you can fix the flaws you discover in that program to
make your version more robust. When you have a version of `echo` that you think
is improved, you should push it up to be tested. 

### Collecting Flaws

Once you have found a bug in the source provided, create an attack that will
exploit this bug. Then, upload it on the "<a href="/attacks/submit">Submit
an Attack</a>" page to have it run against each team's program.

### Scoring
Your score is on the website, with a list of attacks you pass and attacks you
do not.

### Desired Behavior
Your program should print to `stdout` all arguments passed to the program.
For example, running `./echo one two three` should print `one two three`.
Given the way shells parse arguments, `./echo one     two three` should have
the same result. However, `./echo "one      two three"` should print the extra
whitespace. 

### The Gold Standard

In order to help the sloths, the Vizards of Vim Mountain (led by the powerful
Brammoolenaar), provided the sloths with a "perfect" Golden Echo program,
called 'gold'. The sloths can use 'gold' to test their programs's behavior,
but due to DRM and other licensing issues, the Vizards won't let the sloths use
'gold' in production. Still, you can run gold with arguments to test the
"proper" behavior of your program.

Of course, it's possible that you might find flaws in gold that the Vizards
overlooked. If that happens, simply cry out the Vizards in a loud voice about
the problem, and they'll fix it.

### Test cases

For some tests to check your code against before submitting, check out
[these examples](examples)
