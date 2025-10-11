const express=require("express");
const router=express.Router();
const wrapAsync=require("../utils/wrapAsync.js");
const donorController=require("../controllers/donor.js");

router.get("/",donorController.dashboardRender);
router.get("/donate",donorController.donateFormRender);
module.exports=router;