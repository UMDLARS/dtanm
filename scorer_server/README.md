# Scoring Server

## TODO v1
 - Make so scorer actually runs the programs
 - Send results to nodejs server.
 
## TODO v2
 - Migrate to a real task runner like Celery or RQ
    - This means that the scorer will have to access the database as well to send information to each of the tasks.

## Endpoints:
 - `/team/<team_name>`
    - The `<team_name>` should be the name of a team which needs thier code rescored.
 - `/attack/<attack_name>`
    - The `<attack_name>` should be the name of an attack in the server's upload directory which needs to be added to the attack list.
    - Note: this call will result in all currently tracked teams' programs being scored against it.

## Internal Docs

### Attack Manager
The attack manager currently stores all the attacks in the `ATTACKS_DIR`.
This directory contains all the attacks in directory format.
The name of the directory is a hash of the contains.
This way two attacks that are the same would hash to the same value and result in only a single attack being stored.