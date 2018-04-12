var mongoose = require('mongoose');
var bcrypt = require('bcryptjs');

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
    }
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
    bcrypt.hash(user.password, 10, function(err, hash){
        if(err){
            return next(err);
        }
        user.password = hash;
        next();
    });
});

var User = mongoose.model('User', UserSchema);

module.exports = User;
