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
        req.session.filteredDonations = flaskResponse.data;

        res.redirect("/receiver/filter");

        
        

    } catch (error) {
        console.error('Error filtering donations via Flask API:', error.message);
        
        
    }
};

module.exports.showFilteredDonations = async (req, res) => {
    try {
        const flaskData = req.session.filteredDonations;

        if (!flaskData || !flaskData.filtered_donations || flaskData.filtered_donations.length === 0) {
            req.flash("info", "No filtered donations available");
            return res.redirect("/receiver/dashboard");
        }

        // Get the array of AI-scored donations with their IDs and scores
        const aiScoredDonations = flaskData.filtered_donations; // Array of objects with _id and scores
        
        // Extract just the IDs in order
        const sortedDonationIds = aiScoredDonations.map(item => item._id);

        console.log('Sorted Donation IDs from AI:', sortedDonationIds);

        // Fetch all donations from MongoDB
        const donations = await DonorItem.find({ 
            _id: { $in: sortedDonationIds } 
        }).populate("donor", "username donorName receiverName email phone address");

        // Create a map for quick lookup: donationId -> donation object
        const donationMap = {};
        donations.forEach(donation => {
            donationMap[donation._id.toString()] = donation;
        });

        // Sort donations according to AI order and attach AI scores
        const sortedDonations = sortedDonationIds.map((id, index) => {
            const donation = donationMap[id];
            if (donation) {
                // Find the AI score data for this donation
                const aiScore = aiScoredDonations.find(item => item._id === id);
                
                // Attach AI score and rank to the donation object
                donation.aiScore = aiScore || {};
                donation.rank = index + 1;
                
                return donation;
            }
            return null;
        }).filter(d => d !== null); // Remove any null entries

        console.log(`Rendering ${sortedDonations.length} AI-sorted donations`);

        res.render("receiver/filteredDonations", {
            currUser: req.user,
            donations: sortedDonations,
            pageTitle: "AI Recommended Donations"
        });

    } catch (err) {
        console.error("Error rendering filtered donations:", err);
        req.flash("error", "Could not display filtered donations");
        res.redirect("/receiver/dashboard");
    }
};