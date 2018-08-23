# Server Design

This document contains the design of the public facing server.

## Questions
 - How do we assign teams?
 - Does each team have a single user or multiple users?
   - If each team has multiple users how are passwords setup?
 - Will we have a (hack) machine that the users can ssh into to be able to code and etc.?

## Setup
 - An admin should be able to setup the server with predefined teams.  
 - We would like the setup to be minimal for a user.  
 - The password should be preset in order to be printed out before the event.  
 - We should make it so that users don't have to type a password in order to push code to the git repo.  
   - We could use this: https://stackoverflow.com/questions/35942754/how-to-save-username-and-password-in-git


## Server API endpoints
TODO: create a list of rest api endpoints that will allow us the features we need.

## Client Site
TODO: write about what info the user needs to see and what the user needs to do.

 - The user should be able to upload an attack
 - The user should be able to see the current score.
