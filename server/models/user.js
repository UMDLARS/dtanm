var mongoose = require('mongoose');
var bcrypt = require('bcryptjs');
var valid = require('validator');
var UserSchema = new mongoose.Schema({
    email: {
        type: String,
        unique: true,
        required: true,
        trim: true,
    },
    username: {
        type: String,
        unique: true,
        required: true,
        trim: true,
    },
    password: {
        type: String,
        required: true,
    },
    passwordConf: { 
        type: String,
        required: true,
    },
    team : {
        type: String,
        required: true,
        minlength: 1,
        maxlength: 25,
        validate: {
            validator: function(v) {
                return valid.isAlphanumeric(v);
            },
            message: "{VALUE} is not valid team name",
        },
    },
});

UserSchema.statics.authenticate = function(email, password, callback){
    User.findOne({email:email})
        .exec(function(err, user){
            if(err){
                return callback(err);
            } else if (!user){
                var err = new Error('User not found');
                err.status = 401;
                return callback(err);
            }
            bcrypt.compare(password, user.password,function(err, result){
                if(result === true){
                    return callback(null, user);
                } else {
                    return callback();
                }
            });
        });
}
// => this arrow removes the ability to use THIS apparently? Did not know that
UserSchema.pre('save', function (next){
    var user = this;
    console.log(valid.isLength(user.team, 1,25));
    console.log(valid.isAlphanumeric(user.team));
    if(!(valid.isLength(user.team,1,25)) && !(valid.isAlphanumeric(user.team))){
        console.log("In save");
        var err = new Error('Team name contains innapropriate characters');
        err.status(300);
        return next(err);
    }
    else {
        bcrypt.hash(user.password, 10, function(err, hash){
            if(err){
                return next(err);
            }
            user.password = hash;
            next();
        });
    }
});

var User = mongoose.model('User', UserSchema);

module.exports = User;
