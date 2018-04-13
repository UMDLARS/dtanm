var express = require('express'),
    User = require('../models/user.js'),
    router = express.Router(),
    multer = require('multer'),
    bcrypt = require('bcryptjs'),
    base64url = require('base64url'),
    validator = require('validator'),
    storage =   multer.diskStorage({
        destination: function (req, file, callback) {
            const dir = __dirname + '/attacks/' + req.session.team;
            mkdirp(dir, err => callback(err, dir));
        },
         filename: function (req, file, callback) {
           callback(null, file.fieldname);
         }
    }),
    upload = multer({storage: storage});



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
                req.session.userId = user._id;
                req.session.team = user.team
                return res.redirect('/');
            }
        });


    } else if(req.body.logemail && req.body.logpassword) {
        User.authenticate(req.body.logemail, req.body.logpassword, (err, user) =>{
            if(err || !user){
                var err = new Error('Wrong email or password');
                err.status = 401;
                return next(err);
            } else {
                req.session.userId = user._id;
                req.session.team = user.team;
                return res.redirect('/');
            }
        });
    } else {
        var err = new Error('All fields required to register');
        err.status = 400;
        return next(err);
    }
});

router.get('/logout', (req, res) => {
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

router.get('/', (req, res) => {
    console.log("root");
    res.end();
    // Update views
});

//Universal upload, definitely not ideal but just a proof of concept for now.
router.post('/upload', upload.any() ,(req, res) => {
    console.log(req.body);
    console.log(req.files);
    console.log("upload");
    res.end();
});

router.post('/attack', (req, res) => {
    console.log(req.body);
    fs.appendFile('attacklist.txt', req.body.attack, (err) => {
        if(err)
            console.log(err)
        console.log("wrote to file");
    });
    res.sendStatus(200);
});

router.post('/attackupload', upload.any() ,(req, res) => {
    console.log(req.body);
    console.log(req.files);
    console.log("upload");
    res.end();
});

module.exports = router;
