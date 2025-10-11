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
module.exports.signup=async (req,res,next)=>{
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
        res.redirect(`/${registeredUser.role}`);
    })
    } catch(e){
        console.log("ERROR MESSAGE:", e.message); 
        console.log("FULL ERROR:", e); 
        req.flash("error",e.message);
        res.redirect(`/${role}/signup`);
    }
};
module.exports.login = async (req, res) => {
    req.flash("success", "Welcome back to StayQuest!");
    
    let redirectUrl = res.locals.redirectUrl || `/${req.user.role}`;
    
    console.log(`User ${req.user.username} with role ${req.user.role} redirecting to ${redirectUrl}`);
    
    res.redirect(redirectUrl);
};

module.exports.logout=(req,res,next)=>{
    req.logout((err)=>{
       if(err){
        return next(err);
       } 
       req.flash("sucess","You are logged out!");
       res.redirect("/main");
    })
};
module.exports.profile=async(req,res)=>{
    let {id}=req.params;
    console.log(id);
    let userData=await User.findById(id);
    console.log(userData);
    if(userData){
        res.render("users/profile",{userData});
    }else{
        res.render("error","Login to access this feature");
    }
    
}
module.exports.renderApproach=async(req,res)=>{
    res.render("users/approach");
}

module.exports.renderImpact=async(req,res)=>{
    res.render("users/impact");
}