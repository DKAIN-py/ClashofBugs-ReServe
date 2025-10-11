const express=require("express");
const router=express.Router();
const User=require("../models/user.js");
const wrapAsync = require("../utils/wrapAsync.js");
const passport = require("passport");
const userController=require("../controllers/user.js");
const {saveRedirectUrl,isLoggedIn}=require("../middleware.js");

router.get("/main",userController.mainpage);
router.route("/:role/signup")
.get(userController.renderSignupForm)
.post(wrapAsync(userController.signup));

router.route("/login")
.get(userController.renderLoginForm)
.post(saveRedirectUrl,passport.authenticate("local",{failureRedirect:"/login",failureFlash:true}),userController.login);
router.get("/profile/:id",isLoggedIn,userController.profile);
router.get("/logout",userController.logout);
router.get("/approach",userController.renderApproach);
router.get("/impact",userController.renderImpact);
module.exports=router;