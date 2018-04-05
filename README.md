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

* ssh to the server as your team user, e.g., `ssh team1@server.school.edu`
* run `make` to compile your source code.
* run `tips` to see helpful tips
* to create "attack vectors", write command-line input to the program in the `~/attacks` directory (one line per file).
  * For example, if `calc "1 + 2"` causes an error, create a file in `~/attacks` with the content `"1 + 2"`.
  * The game server will remove these attacks from your `~/attacks` directory and test all copies of the program against this vector. (INCOMPLETE)
