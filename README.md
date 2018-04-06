# Do This and Nothing More (DTANM)
## Introduction
Do This and Nothing More (DTANM) is a framework to run exercise modules that teach defensive programming and the "adversarial mindset" without requiring participants to have any special security knowledge.  Like most beginners, programming students usually focus on how to get a particular outcome to occur; they try to answer the question "how do I get the program to work?" and neglect (or completely ignore) the question "what could cause this program to fail?" DTANM tries to teach them to think about protecting against failure without requiring them to be security experts.

In the security world we often teach adversarial thinking through demonstrating and interacting with classic vulnerabilities that are common and easy enough for students to grasp. Things like buffer overflows, directory traversal, SQL injection, cross-site scripting (XSS), and the like. But in order for students to perform these attacks and remediate them, they need to understand those vulnerabilities, common exploits, and other security-specific information. And even if they get this far, security exercises are often solo efforts -- the student against a static, predetermined challenge. It's only adversarial insofar as students pretend it is adversarial. Security competitions can teach adversarial thinking, but these tend to require even more special security knowledge and greater practical expertise in order to be competitive. They're not the best for novices.

We wanted to create a scenario where students could learn about and practice adversarial thinking in addition to developing a "hacking mindset" -- while requiring as little special security knowledge as possible. In [Security in Computing](https://www.amazon.com/Security-Computing-5th-Charles-Pfleeger/dp/0134085043), Pfleeger, Pfleeger and Margulies say "Wheras most requirements say 'the system will do this,' security requirements add the phrase 'and nothing more.'" This got us thinking -- perhaps we can create scenarios where students adversarially test and debug each others' programs -- finding edge cases and situations where the program does not act as it should, but where they don't need special security knowledge.

## How it Works

In order to be a "fair fight," students need to be working on the same program. So, in DTANM competitions, teams are given the same copy of a base program and a description of what the base program is supposed to do. Of course, like pretty much all software, the base program does not actually 100% fulfill or obey the specification. The teams' job is to find ways that the program deviates from the specification. Once they find these "attack vectors", they write them into individual files. Then, the DTNAM framework takes those vectors and forces every team's copy of the program to run on that input -- causing programs that are still "vulnerable" to the bug to fail, while improved programs will operate correctly. In order to determine conclusively if a behavior is correct, we also create a 'gold' version of the base program that works as close to the specification as possible. Students can determine whether their program meets the requirement by comparing their own program to the performance of 'gold'. (Of course, they can't have gold's sourcecode...)

## DTANM Framework

Since every DTANM competition works essentially the same way, we decided to work on a framework that could support competitions using a variety of base programs, rather than a single, hard-coded program. That's what the DTANM Framework is -- a tool for running DTANM competitions in conjunction with a "program pack" (which are packaged separately). The rest of this document describes how to install and start a generic DTANM competition; specific instructions for each "program pack" are included in their own documentation. 

# Instructions for Installing and Running a DTANM Competition

## Installation and Operation

* install Ubuntu 16.04
* install `git` with `sudo apt-get install git`
  * You may also wish to install preferred editors, such as `vim` or `emacs`.
* clone DTANM from one of two locations:
  * https://github.com/UMDLARS/dtanm.git (public release repo)
  * https://github.umn.edu/UMDLARS/cctf.git (private development repo)
* obtain a pack from the developers at <dtanm-dev@d.umn.edu> and place its directory alongside the DTANM repo (so both directories are in the same directory).
* create a symlink inside the DTANM repo named `pack` that points to the pack folder. This probably requires you to run `ln -s  ../packname pack` from inside the DTANM repo pointing to the pack folder `packname` in the parent directory.)
* Inside the `cctf` directory, run `./setup.sh NUMTEAMS` where `NUMTEAMS` is the number of teams you want to use.
* log in to the host as the `cctf` user
* cd into the `bin` directory
* run `screen`
* in the first screen, run `./manager.py`. This program controls the main game mechanism.
* create a new screen window ([screen tutorial](https://linode.com/docs/networking/ssh/using-gnu-screen-to-manage-persistent-terminal-sessions/)) and run `./scorebot.py`.
* Once these programs are running, students can start
  * keep an eye on both proccesses; if they crash, restart them
  * the scoreboard will report an error until all teams have compiled their initial code (see below)

## Student Instructions
### Logging In

* ssh to the server as your team user, e.g., `ssh team1@server.school.edu`
* run `tips` to see helpful tips

### Compiling and Submitting Your Code
* run `make` to compile your source code.
* run `submit` to submit your compiled code for scoring.

### Creating Attack 'Vectors'
* to create "attack vectors", write command-line input to the program in the `~/attacks` directory (one line per file).
  * For example, if `calc "1 + 2"` causes an error in the initial program, create a file in `~/attacks` with the content `"1 + 2"`. The game server will consume these attacks from your `~/attacks` directory and test all copies of the program against this vector.
 * to see the list of attacks, `cat /var/cctf/attacklist.txt`

### Scoring
* to check your team's score, run `score`
* to see the tests your code passes and fails, `cat /var/cctf/dirs/teamN/score.txt` (where `N` is your team number)

### Pack-specific Instructions
* for instructions specific to the game pack you are using, see the file `docs/instructions.md` that came along with the pack. When installed, this file should be available at `http://server.school.edu/instructions.html`.

## Questions or Contributions?
Email the devteam at <dtanm-dev@d.umn.edu> -- or better yet, [join it by subscribing to our list](https://groups.google.com/a/d.umn.edu/forum/#!forum/dtanm-dev).
