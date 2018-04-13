# Design

## Main server
Checkout the readme in the server directory for details on the main server.

## Scoring Server
Checkout the readme in the scorer_server directory for details on the scoring server.

## Attack
An attack is a set of input to be used to run a program.
An attack can be in two different forms in this framework but both follow the same format. The first is a directory containing files describing the input for the program. The other is a tarball containing the aforementioned directory.

The directory layout:  
 - The attack directory (The name of this directory is the name of the attack. If the attack is a tarball then the name is `<attack_name>.tar.gz`)
    - `cmd_args` - This file contains a json list of the arguments to be passed to the program. (like you would on the command line.)
    - `stdin` - This file contains the input to be piped into the stdin of the program.
    - All other files not named `cmd_args` and `stdin` are files that should be copied into the working directory of the program when it is run.
    - Note: any directories here will be ignore. (At least for now.)
