var express = require('express'),
    User = require('../models/user.js'),
    router = express.Router(),
    multer = require('multer'),
    mkdirp = require('mkdirp'),
    mmmagic = require('mmmagic').Magic,
    bcrypt = require('bcryptjs'),
    base64url = require('base64url'),
    validator = require('validator'),
    jwt = require('jsonwebtoken'),
    requests = require('requests'),
    storage =   multer.diskStorage({
        destination: function (req, file, callback) {
            //const dir = __dirname + '/attacks/' + req.session.team;
            const dir = __dirname + '../../uploads'; //Maybe we don't need to keep track of teams and attacks
            mkdirp(dir, err => callback(err, dir));
        },
         filename: function (req, file, callback) {
            var name = "Attack_" + (new Date() / 1000);
            const PY_PORT = process.env.SCORER_PORT || 2000;
            const PY_SERVER = "http://" + (process.env.SCORER_HOST || 'localhost') + PY_PORT
            requests(PY_SERVER + ":" + PY_PORT + "/attack/"+name, function(err, res, body) {
                console.log("error", err);
                console.log("status", res.statusCode);
            });
            callback(null, name);
         }
    }),
    upload = multer({storage: storage});

/**
 * LOGIN
 **/

router.post('/login', (req, res, next) => {
    if(req.body.password !== req.body.passwordConf){
        var err = new Error('Passwords much match');
        err.status = 400;
        return next(err);
    }

    if(req.body.email &&
        req.body.username &&
        req.body.password &&
        req.body.passwordConf &&
        req.body.team){
        var userData = {
            email: req.body.email,
            username: req.body.username,
            password: req.body.password,
            passwordConf: req.body.passwordConf,
            team: req.body.team,
        }
        console.log("create");
        User.create(userData, function(err, user) {
            if(err){
                return next(err);
            } else {
                var token = jwt.sign({ id: user._id }, "SUPERDUPERSECRET", {
                    expiresIn: 86400 // expires in 24 hours
                });

                req.session.userId = user._id;
                req.session.team = user.team
                req.session.token = token;
                res.status(200).send({ auth: true, token: token})
            }
        });


    } else if(req.body.logemail && req.body.logpassword) {
        User.authenticate(req.body.logemail, req.body.logpassword, (err, user) =>{
            if(err || !user){
                var err = new Error('Wrong email or password');
                err.status = 401;
                return next(err);
            } else {
                var token = jwt.sign({ id: user._id }, "SUPERDUPERSECRET", {
                    expiresIn: 86400 // expires in 24 hours
                });
                req.session.userId = user._id;
                req.session.team = user.team;
                req.session.token = token;
                res.status(200).send({ auth: true, token: token})
            }
        });
    } else {
        var err = new Error('All fields required to register');
        err.status = 400;
        return next(err);
    }
});

router.get('/loggedin', (req, res, next) =>{
    if(req.session){
        res.status(200).send({auth:true});
    }
})

router.get('/logout', (req, res, next) => {
    if(req.session){
        req.session.destroy(err => {
            if(err){
                return next(err);
            } else{
                return res.redirect('/');
            }
        });
    }
});


/**
 * UPLOAD
 */

router.post('/attack', upload.single("attack"), (req, res, next) => {
    console.log("Attack?");
    return next(200);
    //console.log(req.body);
    //fs.appendFile('attacklist.txt', req.body.attack, (err) => {
        //if(err)
            //console.log(err)
        //console.log("wrote to file");
    //});
});

//router.post('/attackupload', upload.any() ,(req, res) => {
    //console.log(req.body);
    //console.log(req.files);
    //console.log("upload");
    //res.end();
//});

/**
 * ROOT
 **/
router.get('/', (req, res) => {
    console.log("root");
    res.end();
    // Update views
});

module.exports = router;
