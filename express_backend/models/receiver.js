const mongoose = require("mongoose");

const receiverSchema = new mongoose.Schema({
  receiver: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "User",  // The NGO or receiver who accepts the donation
    required: true,
  },
  donorItem: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "DonorItem",  // The specific food item being accepted
    required: true,
  },
  donor: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "User", // Reference to the donor user
    required: true,
  },
  status: {
    type: String,
    enum: ["pending", "accepted", "completed", "cancelled"],
    default: "pending", // initially pending until donor confirms
  },
  quantityReceived: {
    type: Number,
    required: true, // number of servings receiver is taking
  },
  receivedAt: {
    type: Date,
    default: Date.now, // auto log when accepted
  },
  remarks: {
    type: String,
    trim: true,
    maxlength: 200,
  },
});

module.exports = mongoose.model("ReceiverRequest", receiverSchema);
