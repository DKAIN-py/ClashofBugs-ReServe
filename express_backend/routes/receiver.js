const express=require("express");
const router=express.Router();
const wrapAsync=require("../../utils/wrapAsync.js");
const recieverController=require("../controllers/donor.js");
const multer  = require('multer');
const {storage}=require("../cloudConfig.js");
const upload = multer({  storage });

router.get("/",wrapAsync(recieverController.dashboardRender));
router.post("/",isLoggedIn,upload.single('donorItem[image]'),wrapAsync(recieverController.createListing))
module.exports=router;