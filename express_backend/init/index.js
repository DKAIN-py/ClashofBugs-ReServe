const mongoose=require("mongoose");
const initData=require("./data");
const User=require("../models/user");
main()
.then(res=>console.log("connection build"))
.catch(err=>console.log(err));
async function main(){
    await mongoose.connect("mongodb://localhost:27017/reserve");
}
const initDB=async()=>{
    await User.deleteMany({});
    await User.insertMany(initData.data);
}
initDB();