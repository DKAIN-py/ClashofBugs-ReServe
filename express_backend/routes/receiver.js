const express=require("express");
const router=express.Router();
const wrapAsync = require("../utils/wrapAsync.js");
const receiverController = require("../controllers/receiver.js");
const {saveRedirectUrl,isLoggedIn}=require("../middleware.js");


router.get("/",wrapAsync(receiverController.dashboardRender));

router.post('/filter', isLoggedIn,receiverController.filterDonations);

router.get("/filter", isLoggedIn, receiverController.showFilteredDonations);
router.get("/:id",wrapAsync(receiverController.showListing))
module.exports=router;