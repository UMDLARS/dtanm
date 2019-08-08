**This is the development version: Very unstable**

# Do This and Nothing More (DTANM)
### Introduction
Do This and Nothing More (DTANM) is a framework to run exercise modules that teach defensive programming and the "adversarial mindset" without requiring participants to have any special security knowledge.  Like most beginners, programming students usually focus on how to get a particular outcome to occur; they try to answer the question "how do I get the program to work?" and neglect (or completely ignore) the question "what could cause this program to fail?" DTANM tries to teach them to think about protecting against failure without requiring them to be security experts.

In the security world we often teach adversarial thinking through demonstrating and interacting with classic vulnerabilities that are common and easy enough for students to grasp. Things like buffer overflows, directory traversal, SQL injection, cross-site scripting (XSS), and the like. But in order for students to perform these attacks and remediate them, they need to understand those vulnerabilities, common exploits, and other security-specific information. And even if they get this far, security exercises are often solo efforts -- the student against a static, predetermined challenge. It's only adversarial insofar as students pretend it is adversarial. Security competitions can teach adversarial thinking, but these tend to require even more special security knowledge and greater practical expertise in order to be competitive. They're not the best for novices.

We wanted to create a scenario where students could learn about and practice adversarial thinking in addition to developing a "hacking mindset" -- while requiring as little special security knowledge as possible. In [Security in Computing](https://www.amazon.com/Security-Computing-5th-Charles-Pfleeger/dp/0134085043), Pfleeger, Pfleeger and Margulies say "Wheras most requirements say 'the system will do this,' security requirements add the phrase 'and nothing more.'" This got us thinking -- perhaps we can create scenarios where students adversarially test and debug each others' programs -- finding edge cases and situations where the program does not act as it should, but where they don't need special security knowledge.

### How it Works

In order to be a "fair fight," students need to be working on the same program. So, in DTANM competitions, teams are given the same copy of a base program and a description of what the base program is supposed to do. Of course, like pretty much all software, the base program does not actually 100% fulfill or obey the specification. The teams' job is to find ways that the program deviates from the specification. Once they find these "attack vectors", they write them into individual files. Then, the DTNAM framework takes those vectors and forces every team's copy of the program to run on that input -- causing programs that are still "vulnerable" to the bug to fail, while improved programs will operate correctly. In order to determine conclusively if a behavior is correct, we also create a 'gold' version of the base program that works as close to the specification as possible. Students can determine whether their program meets the requirement by comparing their own program to the performance of 'gold'. (Of course, they can't have gold's sourcecode...)

### DTANM Framework

Since every DTANM competition works essentially the same way, we decided to work on a framework that could support competitions using a variety of base programs, rather than a single, hard-coded program. That's what the DTANM Framework is -- a tool for running DTANM competitions in conjunction with a "program pack" (which are packaged separately). The rest of this document describes how to install and start a generic DTANM competition; specific instructions for each "program pack" are included in their own documentation. 

### Installing and Running a DTANM Competition

* [install Docker](https://github.com/wsargent/docker-cheat-sheet#installation)
* place a pack at `./pack` (this can be a symlink or a directory), including setting up `config.py`.
  Find instructions on building your pack at https://github.com/UMDLARS/cctf_pack, or contact the developers for pre-made packs.
* run `docker-compose up -d` to start servers
* visit the URL on which you're hosting (localhost:5000, commonly, if you're
  not proxying the service) and use the [admin panel](http://localhost:5000/admin)
  to set up teams and users.
* Set up reverse proxy. We use nginx and letsencrypt for proxying to HTTPS on port 443.

### Questions or Contributions?
Email the devteam at <dtanm-dev@d.umn.edu> -- or better yet, [join it by subscribing to our list](https://groups.google.com/a/d.umn.edu/forum/#!forum/dtanm-dev).
