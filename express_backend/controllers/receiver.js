const Receiver=require("../models/receiver");

module.exports.dashboardRender=(req,res)=>{
    res.render("receiver/dashboard.ejs");
}