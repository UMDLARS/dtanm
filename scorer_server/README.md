# Scoring Server

## TODO:
 - Make so scorer actaully runs the programs
 - Send results to nodejs server.

## Endpoints:
 - `/team/<team_name>`
    - The `<team_name>` should be the name of a team which needs thier code rescored.
 - `/attack/<attack_name>`
    - The `<attack_name>` should be the name of an attack in the server's upload directory which needs to be added to the attack list.
    - Note: this call will result in all currently tracked teams' programs being scored against it.
