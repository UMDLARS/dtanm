# TODO
1. Implement Authentication
   1. I think this is good for now?
2. Implement more internal HTTP calls to Python server
3. Allow users to select team names?
   1. Allow setting of static teams
4. Allow uploading of tarballs for attacks
   1. Validate extension and file type on submission
   2. Implement hashing and storage of hash to database.
5. Restructure the server to reflect generic file structure
6. *DONE* Implement Rate Limiting!!! (Prevent brute force on bcrypt)
7. *DONE* Implement Pre-Receive Hook to deny users not in team
  6a. Maybe just cheat and use team name registered under a user as the repo name

# Server DTANM

This is an attempt at transitioning the DTANM framework to a more flexible setup. Currently the DTANM framework relies on static pathing for all interaction with teams. This is an attempt to decentralize this setup such that any number of teams can interact with the server and compete.

## Current Implementation
Basic setup.

Jon and I have reworked the original idea to be as follows:

 	1. Node server to handle authentication/uploading/git repos of teams
	2. Python internal server to handle updates to attacks and team source files
    	1. Python server will, upon notice, spawn child processes to begin testing of the source and attacks
    	2. Upon team source push all past results will be invalidated and thus need to be recomputed
    	3. Upon attack push all teams must be ran against the new attack, thus less overhead for computation
	3. Mongodb
    	1. Users for auth
    	2. Attacks
        	1. Keep track of uploaded attacks and their hashes for denial of resubmission
    	3. Results
        	1. For Node server to obtain the results from the runs

## Testing

TODO implement mocha + chai testing

### Curl Requests for testing

to make requests using curl we can run the following command to obtain session info:  
```
curl <URL> --cookie-jar cookie --cookie cookie
```

```
curl <URL> --cookie cookie -F "file=@filepath" enpoint
```  
This saves the cookie obtained to the file cookie which is then used by the --cookie flag to generate the correct request.

### Run Docker
to build the image run the following commands from the directory where dtanm is cloned run:  
```
docker build -t cctf_calc .
```  
```
docker run -ti --rm cctf_calc -p 80:5000 -p 7005:7005
```  
probably can omit the CCTF

### Docker TODO 
On close we need a mounted volume to store a tar ball of all the git repos + results directory

Results need to be a full history and not just current results

### Node Modules
* express-session
* express
* body-parser
* node-git-server (early beta of module)
* mkdirp (creation of directories)
* multer (file uploading)
* bcryptjs
* mongoose
* MongoClient
* validator
* mmagic
* ?


