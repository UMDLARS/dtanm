var app = require('express')(),
    //cP = require('cookie-parser'),
    session = require('express-session'),
    bP = require('body-parser'),
    //cS = require('cookie-session'),
    fs = require('fs'),
    git_server = require('./app/gitserver.js')(),
    crypto = require('crypto'),
    mkdirp = require('mkdirp'),
    multer = require('multer'),
    bcrypt = require('bcryptjs'),
    base64url = require('base64url'),
    storage =   multer.diskStorage({
        destination: function (req, file, callback) {
            const dir = __dirname + '/attacks/' + req.session.team;
            mkdirp(dir, err => callback(err, dir));
        },
         filename: function (req, file, callback) {
           callback(null, file.fieldname);
         }
    }),
    upload = multer({storage: storage}),
    User = require('./models/user.js'),
    mongoose = require('mongoose'),
    MongoStore = require('connect-mongo')(session);

/** Sync */
function randomStringAsBase64Url(size) {
  return base64url(crypto.randomBytes(size));
}

/**
 * DB Connection
 */

mongoose.connect('mongodb://localhost/testAuth');
var db  = mongoose.connection;

db.on('error', console.error.bind(console, 'connection error:'));
db.once('open', function(){
    console.log("open");
});

/** Session setup **/
//app.use(cS({
    //name: 'session',
    //keys: ["mysupersecretlonglonglonglongphrasethatnoonewillguess", "anothersuperdankdankdankdankdumbthing"],
    //maxAge: 24 * 60 * 60 * 1000 // 24 hours
//}));
//
//Using express session instead
app.use(session({
    secret: 'supersupersecret',
    resave: true,
    saveUninitialize: false,
    store: new MongoStore({
        mongooseConnection: db
    })
}));

app.use(bP.json());

/**
 * This is our middleware to determine if we have been successfully authenticated
 */
app.use((req,res,next) => {
    console.log("middleware");
    if(req.session && req.session.userId){
        return next();
    } else if(req.url === '/login'){
        return next();   
    } else {
        var err = new Error('You need to be authenticated');
        err.status = 301;
        return next(err);
    }
});


app.post('/login', (req, res, next) => {
    if(req.body.password !== req.body.passwordConf){
        var err = new Error('Passwords much match');
        err.status = 400;
        return next(err);
    }

    if(req.body.email && req.body.username && req.body.password && req.body.passwordConf){
        var userData = {
            email: req.body.email,
            username: req.body.username,
            password: req.body.password,
            passwordConf: req.body.passwordConf,
        }
        console.log("create");
        User.create(userData, function(err, user) {
            if(err){
                return next(err);
            } else {
                req.session.userId = user._id;
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
                return res.redirect('/');
            }
        });
    } else {
        var err = new Error('All fields required to register');
        err.status = 400;
        return next(err);
    }
});

app.get('/logout', (req, res) => {
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

app.get('/', (req, res) => {
    console.log("root");
    res.end();
    // Update views
});

//Universal upload, definitely not ideal but just a proof of concept for now.
app.post('/upload', upload.any() ,(req, res) => {
    console.log(req.body);
    console.log(req.files);
    console.log("upload");
    res.end();
});

app.post('/attack', (req, res) => {
    console.log(req.body);
    fs.appendFile('attacklist.txt', req.body.attack, (err) => {
        if(err)
            console.log(err)
        console.log("wrote to file");
    });
    res.sendStatus(200);
});

app.post('/attackupload', upload.any() ,(req, res) => {
    console.log(req.body);
    console.log(req.files);
    console.log("upload");
    res.end();
});

// catch 404 and forward to error handler
app.use((req, res, next) => {
  var err = new Error('File Not Found');
  err.status = 404;
  next(err);
});

// error handler
// define as the last app.use callback
app.use((err, req, res, next) => {
  res.status(err.status || 500);
  res.send(err.message);
});

app.listen(5000, ()=>{console.log("listening on port 5000");});
