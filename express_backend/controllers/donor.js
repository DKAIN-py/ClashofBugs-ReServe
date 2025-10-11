const DonorItem = require("../models/donor");

module.exports.dashboardRender=(req,res)=>{
    res.render("donors/dashboard.ejs");
}
module.exports.donateFormRender=(req,res)=>{
    res.render("donors/donorform.ejs");
}

module.exports.donationSend = async (req, res) => {
    console.log("=== DONATION SEND FUNCTION CALLED ===");
    console.log("req.body:", req.body);
    console.log("req.body.donorItem:", req.body.donorItem);
    console.log("req.file:", req.file);
    console.log("req.user:", req.user);
    try {
    console.log("Received data:", req.body.donorItem); 
      const { path: url, filename } = req.file;
  
      // create new donation
      const newDonation = new DonorItem(req.body.donorItem);
  
      // assign logged-in donor
      newDonation.donor = req.user._id;
  
      // assign image
      newDonation.image = { url, filename };
  
      // save in DB
      await newDonation.save();
  
      req.flash("success", "Donation created successfully!");
      res.redirect("/donor"); // wherever donor should go
    } catch (err) {
      console.log(err);
      req.flash("error", "Something went wrong!");
      res.redirect("/donor/donate");
    }
  };