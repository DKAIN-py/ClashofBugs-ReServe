const Receiver=require("../models/receiver");
const DonorItem = require("../models/donor");
const wrapAsync = require("../utils/wrapAsync.js");
const axios = require('axios');
const FLASK_API_URL = 'http://localhost:3000';
module.exports.dashboardRender=async(req,res)=>{
    try {
        // Get ALL donations with proper population
        const allDonations = await DonorItem.find()
          .populate({
            path: "donor",
            select: "username donorName receiverName email phone address role"
          })
          .sort({ postedAt: -1 });
        
        console.log("=== DASHBOARD DEBUG ===");
        console.log("Donations found:", allDonations.length);
        console.log("Current user:", {
            username: req.user.username,
            role: req.user.role,
            donorName: req.user.donorName,
            receiverName: req.user.receiverName
        });
        
        if (allDonations.length > 0) {
            console.log("First donation donor:", allDonations[0].donor);
        }
        
        // Render dashboard view
        res.render("receiver/dashboard", {
          user: req.user,
          donations: allDonations,
        });
    
    } catch (err) {
        console.log("Error loading receiver dashboard:", err);
        req.flash("error", "Could not load dashboard");
        res.redirect("/");
    }
}

module.exports.filterDonations = async (req, res) => {
    try {
        const { category, nearestLocation } = req.body;
        
        // Fetch all available donor items with donor information
        const donations = await DonorItem.find({ 
            receiver: null  // Only unclaimed items
        }).populate('donor', 'username email donorName receiverName phone address');

        // Prepare donorlist array
        const donorlist = donations.map(donation => {
            // Get donor address from the donor (User model)
            const donorAddress = donation.donor?.address || 'Address not available';
            
            return {
                _id: donation.donor?._id?.toString() || 'unknown',
                address: donorAddress, // Keep as string, no geocoding needed
                food_category: [donation.food_category],
                quantity: donation.serving || 0
            };
        });

        // Get receiver location using Nominatim API
        let receiverLat = 22.7196; // Default Indore coordinates
        let receiverLon = 75.8577;
        
        if (req.user.address) {
            try {
                const geoResponse = await axios.get(
                    `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(req.user.address)}`,
                    {
                        headers: { 
                            "User-Agent": "reserve-app" 
                        },
                        timeout: 5000
                    }
                );
                
                if (geoResponse.data && geoResponse.data.length > 0) {
                    receiverLat = parseFloat(geoResponse.data[0].lat);
                    receiverLon = parseFloat(geoResponse.data[0].lon);
                    console.log(`Receiver location geocoded: [${receiverLat}, ${receiverLon}]`);
                } else {
                    console.warn('Nominatim API returned no results, using default location');
                }
            } catch (geoError) {
                console.error('Error geocoding receiver address:', geoError.message);
                console.warn('Using default Indore coordinates');
            }
        }
        
        // Prepare filters object
        const filters = {
            food_category: category || 'all',
            location: [receiverLat, receiverLon], // [latitude, longitude]
            nearest: nearestLocation === 'true',
            capacity: 10 // Hardcoded value
        };

        // Prepare final data to send to Flask API
        const requestData = {
            donorlist: donorlist,
            filters: filters
        };

        console.log('Sending to Flask API:', JSON.stringify(requestData, null, 2));

        // Send POST request to Flask API
        const flaskResponse = await axios.post(
            `${FLASK_API_URL}/receiver/filter`,
            requestData,
            {
                headers: {
                    'Content-Type': 'application/json'
                },
                timeout: 10000 // 10 second timeout
            }
        );
        console.log(flaskResponse.data);
        return flaskResponse.data;

        
        

    } catch (error) {
        console.error('Error filtering donations via Flask API:', error.message);
        
        
    }
};