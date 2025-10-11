const mongoose = require("mongoose");

const donorSchema = new mongoose.Schema({
    donor: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",   // Donor user reference
      required: true,
    },
    receiver: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "User",   // Receiver bhi "User" hi hai (role: receiver)
      required: false, // initially null hoga
    },
    itemName: {
      type: String,
      required: true,
    },
    shelfLife: {
      days: { type: Number, min: 0, default: 0 },
      hours: { type: Number, min: 0, max: 23, required: true },
    },
    serving: {
      type: Number,
      required: true,
    },
    food_category: {
      type: String,
      enum: [
        "grains_and_rice",
        "breads",
        "lentils_and_pulses",
        "vegetables",
        "curries_and_gravies",
        "snacks_and_streetfood",
        "sweets_and_desserts",
        "breakfast_items",
        "dairy_products",
        "fruits",
        "beverages",
      ],
      required: true,
    },
    description: {
      type: String,
      required: true,
      trim: true,
      maxlength: 300 // optional limit for neatness
    },
    
    image: {
      url: String,
      filename: String
    },
    postedAt: {
      type: Date,
      default: Date.now, // jis waqt banda post karega
    }
  });

  module.exports = mongoose.model("DonorItem", donorSchema);
