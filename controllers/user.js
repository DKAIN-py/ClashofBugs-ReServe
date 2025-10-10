const User=require("../models/user");
module.exports.mainpage=(req,res)=>{
    res.render("users/index");
}
module.exports.renderSignupForm=(req,res)=>{
    let {role}=req.params;
    console.log(role);
    res.render("users/signup",{role});
};
module.exports.renderLoginForm=(req,res)=>{
    res.render("users/login");
};
module.exports.signup=async (req,res)=>{
    try{
        let {role}=req.params;
        let {username,email,password,receiverName,donorName,receiver_type,phone,address,about}=req.body;
    const newUser=new User({
        username,
        email,
        donorName,
        receiverName,
        receiver_type,
        phone,
        address,
        about,
        role
    });
    console.log("newUser before register:", newUser);
        
    const registeredUser=await User.register(newUser,password);
    console.log("registeredUser after register:", registeredUser);
    req.login(registeredUser,(err)=>{
        if(err){
            return next(err)
        }
        req.flash("sucess","Welcome to StayQuest!");
        res.redirect("/role");
    })
    } catch(e){
        console.log("ERROR MESSAGE:", e.message); // ← यह add करो
        console.log("FULL ERROR:", e); // ← यह भी add करो
        req.flash("error",e.message);
        res.redirect(`/${role}/signup`);
    }
};
module.exports.login = async (req, res) => {
    req.flash("success", "Welcome back to StayQuest!");
    
    // Priority: stored redirect URL first, then role-based redirect
    let redirectUrl = res.locals.redirectUrl || 
                     (req.user.role === 'donor' ? "/donor" : "/receiver");
    
    console.log(`User ${req.user.username} with role ${req.user.role} redirecting to ${redirectUrl}`);
    
    res.redirect(redirectUrl);
};