var mongoose = require('mongoose');
var bcrypt = require('crypto');
var valid = require('validator');
var AttackSchema = new mongoose.Schema({
    checksum: {
        type: String,
        unique: true,
        required: true,
        trim: true,
    },
    id: {
        type: String,
        unique: true,
        required: true,
        trim: true,
        validate: {
            validator: function(v) {
                return valid.isAlphanumeric(v);
            },
            message: "{VALUE} id is not alphanumeric",

    },
});

// => this arrow removes the ability to use THIS apparently? Did not know that
AttackSchema.pre('save', function (next){
    next();
});

var Attack = mongoose.model('Attack', AttackSchema);

module.exports = Attack;
