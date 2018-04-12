var gitServer = require('node-git-server');
var path = require('path');
var User = require('../models/user.js');
var mongoose = require('mongoose');
mongoose.connect('mongodb://localhost/testAuth');
var db  = mongoose.connection;

const port = process.env.PORT || 7005;
var server = function(){
    const repos = new gitServer(path.resolve(__dirname, 'gitrepos'), {
        autoCreate: true,
        authenticate: (type, repo, user, next) => {
            if(type == 'push'){
                user((uname, upass) => {
                    console.log(uname, upass);
                    User.authenticate(uname, upass, (err, user) =>{
                        if(err || !user){
                            var err = new Error('Wrong email or password');
                            err.status = 401;
                            return next(err);
                        } else {
                            return next();
                        }
                    });
                });
            } else{
                return next();
            }
        }
    });
    
    repos.on('push', (push) => {
        console.log("push");
        push.accept();
    });

    repos.on('fetch', (fetch) => {
        console.log("fetch");
        fetch.accept();
    });

    repos.listen(port, () => {
        console.log("Git server running on port ", port);
    });

};


module.exports = server;
