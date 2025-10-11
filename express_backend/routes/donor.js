const express=require("express");
const router=express.Router();

const wrapAsync=require("../utils/wrapAsync.js");
const donorController=require("../controllers/donor.js");
const multer  = require('multer');
const {storage}=require("../cloudConfig.js");
const upload = multer({  storage });
const {saveRedirectUrl,isLoggedIn}=require("../middleware.js");

router.get("/",donorController.dashboardRender);
router.get("/donate",donorController.donateFormRender);
router.post("/donate",isLoggedIn,upload.single('donorItem[image]'),wrapAsync(donorController.donationSend));
module.exports=router;