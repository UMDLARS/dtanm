# Design

## Attack
An attack is a set of input to be used to run a program.
An attack can be in two different forms in this framework but both follow the same format. The first is a directory containing files describing the input for the program. The other is a tarball containing the aforementioned directory.

The directory layout:  
 - The attack directory (the users may name an uploaded tarball whatever they wish; it will be ignored)
    - `cmd_args` - This file contains a string of the arguments that you would pass to the proogram.
    - `stdin` - This file contains the input to be piped into the stdin of the program (text or data).
    - `env` - This file contains a list of environment variables that should be present when the program is run.
    - `files` - This directory contains any files to be copied into the working directory of the program when it is run.
    - Note: any other files or directories here will be ignored (at least for now).

## Attack Manager
The attack manager currently stores all the attacks in the `ATTACKS_DIR`.
This directory contains all the attacks in directory format, as well as their respective tarballs.
The name of the directory is its id in the database.
This way two attacks that are the same would hash to the same value and result in only a single attack being stored.

## Pack
A pack is a directory containing all the needed information to run a certain competition.
To run a pack the root directory of the pack should be placed (or symlinked to) in the root directory of this dtanm repo, and should be called `pack`.

Information on creating packs is available at https://github.com/UMDLARS/dtanm_pack.
To obtain a prebuilt pack, talk to the developers.


# Internal Design

## File System
The docker containers share a file system volumn mounted at `/cctf`. It is used
to share data between the web server and workers, and has the following  file
structure:
- `/cctf` - the root of the shared file system
  - `attacks/{attack_id/,attack_id.tar.gz}` - contains the uploaded attacks
  - `repos/{team_id}/` - contains each team's source code
