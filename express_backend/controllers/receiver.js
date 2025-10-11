const Receiver=require("../models/receiver");

module.exports.dashboardRender=async(req,res)=>{
    try {
        // Get ALL donations (no filtering)
        const allDonations = await DonorItem.find()
          .populate("donor", "donorName address phone")
          .sort({ postedAt: -1 });
    
        // Render dashboard view
        res.render("receiver/dashboard", {
          user: req.user,
          donations: allDonations,
        });
    
      } catch (err) {
        console.log("Error loading receiver dashboard:", err);
      }
}

