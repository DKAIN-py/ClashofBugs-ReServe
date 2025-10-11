module.exports.dashboardRender=(req,res)=>{
    res.render("donors/dashboard.ejs");
}
module.exports.donateFormRender=(req,res)=>{
    res.render("donors/donorform.ejs");
}