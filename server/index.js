var app = require('express')(),
    //cP = require('cookie-parser'),
    session = require('express-session'),
    bP = require('body-parser'),
    //cS = require('cookie-session'),
    fs = require('fs'),
    git_server = require('./app/gitserver.js')(),
    crypto = require('crypto'),
    mkdirp = require('mkdirp'),
    bcrypt = require('bcryptjs'),
    base64url = require('base64url'),
    User = require('./models/user.js'),
    mongoose = require('mongoose'),
    MongoStore = require('connect-mongo')(session),
    jwt = require('jsonwebtoken'),
    RateLimit = require('express-rate-limit');

/**
 * Rate limiting for brute force. Can change if we don't want to rate limit certain endpoints
 */

    var limiter = new RateLimit({
      windowMs: 15*60*1000, // 15 minutes
      max: 100, // limit each IP to 100 requests per windowMs
      delayMs: 0 // disable delaying - full speed until the max limit is reached
    });

    //  apply to all requests
    app.use(limiter);

/**
 * DB Connection
 */

    mongoose.connect('mongodb://' + (process.env.MONGO_HOST || 'localhost') + '/testAuth');
    var db  = mongoose.connection;

    db.on('error', console.error.bind(console, 'connection error:'));
    db.once('open', function(){
        console.log("open");
    });

/** Session setup **/
    app.use(session({
        secret: 'supersupersecret',
        resave: true,
        saveUninitialize: false,
        store: new MongoStore({
            mongooseConnection: db
        })
    }));

/** Allow JSON parsing **/
    app.use(bP.json());
/**
 * Query Teams (Outside of router due to middleware)
 **/
    app.get('/getAllTeams', (req,res, err) => {
        User.distinct('team', (err, docs) => {
            if(err){
                var err = new Error('Something is real wrong');
                err.status = 400;
                return next(err);
            }
            res.send({"teams": docs});
        });
    });

/**
 * This is our middleware to determine if we have been successfully authenticated
 */
    app.use((req,res,next) => {
        console.log("middleware");
      var token = req.body.token || req.query.token || req.headers['x-access-token'];
        if(token && req.session && req.session.userId){
            jwt.verify(token, "SUPERDUPERSECRET", function(err, decoded) {
                if (err) {
                    return res.json({ success: false, message: 'Failed to authenticate token.' });
                } else {
                // if everything is good, save to request for use in other routes
                    console.log("AUTHENTICATED");
                    req.decoded = decoded;
                    next();
                }
            });
        } else if(req.url === '/login'){
            return next();
        } else {
            var err = new Error('You need to be authenticated');
            err.status = 301;
            return next(err);
        }
    });
/**
 * Import routes to use for root.
 */
    var routes = require('./routes/route');
    app.use('/', routes);

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
