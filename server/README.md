# TODO
1. Implement Authentication
2. Allow users to select team names?
3. Allow uploading of tarballs for attacks
4. Restructure the server to reflect generic file structure
# Server DTANM

This is an attempt at transitioning the DTANM framework to a more flexible setup. Currently the DTANM framework relies on static pathing for all interaction with teams. This is an attempt to decentralize this setup such that any number of teams can interact with the server and compete.

##Current Implementation
Basic setup.

On connection establish a session, we do not care who it is an as such will create a directory for them (Security issue is obvious as this leaves open for DDOS). Improvement is to just add proper authentication.

Once established any future requests will utilize this session to upload and request information from the server. We will redirect back to the root of the application if there is no session associated with a given request.

###Curl
to make requests using curl we can run the following command to obtain session info:

```curl <URL> --cookie-jar cookie --cookie cookie```
```curl <URL> --cookie cookie -F "file=@filepath" enpoint ```
This saves the cookie obtained to the file cookie which is then used by the --cookie flag to generate the correct request.

###Docker
to build the image run 
```docker build -t cctf_calc .```
```docker run -ti --rm -v CCTF:/home cctf_cal -p 9000:80```
probably can omit the CCTF

### Modules
* cookie-session
* express
* body-parser
* node-git-server (early beta of module)
* mkdirp (creation of directories)
* multer (file uploading)
* ?


