# Design

## Current Open Questions
 - How will we handle "Good math". Basically how will we inject good test cases.
    - We could have a test suite that must pass in order to "qualify" for scoring.
    - We could reimplement the 50/50 good tests to attacks method.

## Attack
An attack is a set of input to be used to run a program.
An attack can be in two different forms in this framework but both follow the same format. The first is a directory containing files describing the input for the program. The other is a tarball containing the aforementioned directory.

The directory layout:  
 - The attack directory (The name of this directory is the name of the attack. If the attack is a tarball then the name is `<attack_name>.tar.gz`)
    - `cmd_args` - This file contains a json list of the arguments to be passed to the program. (like you would on the command line.)
    - `stdin` - This file contains the input to be piped into the stdin of the program.
    - `env` - This directory contains any files to be copied into the working directory of the program when it is run.
        - Note: any directories here will be ignore. (At least for now.)
<!--    - All other files not named `cmd_args` and `stdin` are files that should be copied into the working directory of the program when it is run. -->

## Attack Manager
The attack manager currently stores all the attacks in the `ATTACKS_DIR`.
This directory contains all the attacks in directory format.
The name of the directory is a hash of its contents.
This way two attacks that are the same would hash to the same value and result in only a single attack being stored.

## Pack
A pack is a directory containing all the needed information to run a certain competition.
To run a pack the root directory of the pack should be placed in the root directory of this dtanm repo. And should be called `pack`.

The structure:  
 - The root folder
    - `docs`
        - `tips` - This should be an executable that prints out helpful tips for the players of the competition.
        - `www` - This directory should contain all the files that you would like to serve using apache on port 80.
            - Normally this folder should contain an `index.html`
    - `env`
        - This directory should contain any files that you would like to be copied into the same folder as the players' program when being scored.
        - Note: These files are also copied into the current working directory of the gold as well.
        - Normally you would put some sample test input files into this directory.
    - `gold`
        - This directory should contain the gold program (a "perfect" version of the program.)
    - `info` - (We should change this to be a single file named `config.json`.)
        - `bin_name` - This should contain the name of the binary/script which is submitted.
        - `pack_name` - This should contain the name of the pack. Can be anything. Currently I don't think it is used for anything.
        - `src_name` - This should be the name of the source file. (NOTE: this should be removed in the next version.)
    - `src`
        - This directory should contain whatever code you would like all players to receive.


# Internal Design

## File System
The docker containers share a file system volumn mounted at `/cctf` and has the following structure.
- `/cctf` - the root of the shared file system
  - `attacks` - contains the uploaded attacks
  - `server/gitrepos` - contains each team's source code
  - `gold` - contains the gold source code
