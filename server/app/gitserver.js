var gitServer = require('node-git-server'),
    path = require('path'),
    User = require('../models/user.js'),
    mongoose = require('mongoose'),
    requests = require('requests');
mongoose.connect('mongodb://' + (process.env.MONGO_HOST || 'localhost') +'/testAuth');
var db  = mongoose.connection;

const port = process.env.PORT || 7005;
const PY_PORT = process.env.PYTHON_PORT || 2000
const PY_SERVER = "http://" + (process.env.SCORER_HOST || 'localhost') + PY_PORT
var server = function(){
    const repos = new gitServer(path.resolve(__dirname, '../gitrepos'), {
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
                            console.log(repo);
                            console.log(user);
                            if(user.team !== repo){
                                var err = new Error('You can only push to a team repository of the same name');
                                err.status = 401;
                                return next(err);
                            }
                            requests(PY_SERVER + repo, function(err, res, body){
                                console.log("err", err);
                                console.log("res", res);
                            });
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
