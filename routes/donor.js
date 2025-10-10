const express=require("express");
const router=express.Router();
const wrapAsync=require("../utils/wrapAsync");
const donorController=require("../controllers/donor.js");
router.get("/",donorController.dashboardRender);
module.exports=router;