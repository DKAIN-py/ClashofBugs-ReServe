if(process.env.NODE_ENV != "production"){
    require('dotenv').config();
}
const express=require("express");
const app=express();
const path=require("path");
const ejsMate = require('ejs-mate');
const mongoose=require("mongoose");
const passport=require('passport');
const axios=require('axios');
const localStrategy=require('passport-local');
const User=require('./models/user.js');
const session=require('express-session');
const flash=require('connect-flash');
const ExpressError=require("./utils/ExpressError.js");

const sessionOptions={
    secret:"sghcvhgsvcghsd",
    resave:false,
    saveUninitialized:true,
    cookie:{
        expires:Date.now() + 7*24*60*60*1000,
        maxAge:7*24*60*60*1000,
        httpOnly:true,
    }
}
app.set("view engine","ejs");
app.set("views",path.join(__dirname,"views"));
app.use(express.urlencoded({extended:true}));
app.use(express.json());
app.use(express.static(path.join(__dirname,"public")));
app.engine('ejs', ejsMate);

app.use(session(sessionOptions));
app.use(flash());

app.use(passport.initialize());
app.use(passport.session());
passport.use(new localStrategy(User.authenticate()));
// use static serialize and deserialize of model for passport session support
passport.serializeUser(User.serializeUser());
passport.deserializeUser(User.deserializeUser());

const port=8080;
//routes requiring
const userRouter=require("./routes/user.js");
const donorRouter=require("./routes/donor.js");
main()
.then(res=>console.log("connection success with db reserve"))
.catch(err=>console.log(err));
async function main(){
    await mongoose.connect("mongodb://localhost:27017/reserve");
}
app.use((req,res,next)=>{
    res.locals.success=req.flash("sucess");
    res.locals.error=req.flash("error");
    res.locals.currUser=req.user;
    next();
})
app.get("/",(req,res)=>{
    res.redirect("/main");
})
app.use("/",userRouter);
app.use("/donor",donorRouter);

app.use((req, res, next) => {
    next(new ExpressError(404, "page not found"));
});
app.use((err,req,res,next)=>{
    let {statusCode=500,message="some error occured"}=err;
    res.status(statusCode).render("error.ejs",{message});
    // res.status(statusCode).send(message);
})
app.listen(port,()=>{
    console.log("the server is working on port",port);
})