# Instructions for Installing and Running a DTANM Competition

* install Ubuntu 16.04 along with Apache2.  
* clone DTANM from one of two locations:
  * https://github.com/UMDLARS/dtanm.git (public release repo)
  * https://github.umn.edu/UMDLARS/cctf.git (private development repo)
* obtain a pack from the developers at <dtanm-dev@d.umn.edu> and place it in the same directory as the DTANM repo
* create a symlink inside the DTANM repo named `pack` that points to the pack folder. This probably requires you to run `ln -s  ../packname pack` from inside the DTANM repo pointing to the pack folder `packname` in the parent directory.)
* Run `./setup.sh NUMTEAMS` where `NUMTEAMS` is the number of teams you want to use.
* log in to the host as the `cctf` user
* run `screen` (or `apt-get install screen` if it is not installed)
* in the first screen, cd into `bin` and run `./manager.py`. This program controls the main game mechanism.
* create a new screen window ([screen tutorial](https://linode.com/docs/networking/ssh/using-gnu-screen-to-manage-persistent-terminal-sessions/)), cd into `bin` and run `./scorebot.py`.
