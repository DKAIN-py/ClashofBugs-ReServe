const mongoose = require("mongoose");
const passportLocalMongoose=require("passport-local-mongoose");

const userSchema = new mongoose.Schema({
    email: { 
      type: String, 
      required: true, 
      unique: true 
    },
    role: { 
      type: String, 
      enum: ["donor", "receiver"], 
      required: true 
    },
  
    // Restaurant-specific fields
    donorName: { type: String},
  
    // NGO-specific fields
    receiverName: { type: String },
    receiver_type: {
        type: String,
        enum: [
          "shelter",
          "community kitchen",
          "food bank",
          "mid day meal provider",
          "disaster relief",
          "homeless support"
        ]
      },
    // Common fields
    phone: { type: String,
        required: true 
     },
    address: { type: String,
        required: true 
     },
    about: { type: String,
        required: true
     }, // profile bio
  });
  userSchema.plugin(passportLocalMongoose);
  module.exports = mongoose.model('User', userSchema);