# Scoring Server

## Endpoints:
 - `/team/<team_name>`
    - The `<team_name>` should be the name of a team which needs thier code rescored.
 - `/attack/<attack_name>`
    - The `<attack_name>` should be the name of an attack in the server's upload directory which needs to be added to the attack list.
    - Note: this call will result in all currently tracked teams' programs being scored against it.
 - `/results` (MAY BE REMOVED)
    - This simply dumps the results table from Mongo.
    - I created this endpoint to allow end to end testing.
    - It return a list of results where a result is a dictionary containing `team_id`, `commit`, `attack_id` and `passed`.

# Internal Docs

## Scoring Server Arch

There are three main parts to the scorer: **Server**, **Tasker** and **Worker**.
These three parts are organized into a pipeline, where the output of the Server feeds into the Tasker and so on.
The data is passed between parts using Redis.
The final result is saved to a Mongo collection.

A overview of the current arch:
![Arch Design](images/scorer_arch_v2.png)

### Server

The server simply supports the [endpoints](#Endpoints).

### Tasker

The tasker takes the updates received through the server's endpoints and decides which scoring task need to be done.
A scoring task is a team-attack pair, meaning that the team's program should be run with the attack and compare to gold.

### Worker

The worker actually does the scoring. The workers wait till the tasker assigns them a scoring task and then they do it.


## Attack Manager
The attack manager currently stores all the attacks in the `ATTACKS_DIR`.
This directory contains all the attacks in directory format.
The name of the directory is a hash of the contains.
This way two attacks that are the same would hash to the same value and result in only a single attack being stored.

