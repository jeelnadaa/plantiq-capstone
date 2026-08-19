const express = require("express");
const router = express.Router();
const pool = require("../db");


// Add Coffee Listing
router.post("/add", async (req, res) => {

  console.log("REQ BODY:", req.body);

  try {
    const {
      farmer_id,
      coffee_type,
      processing_type,
      quantity,
      price,
      latitude,
      longitude
    } = req.body;

    const result = await pool.query(
      `INSERT INTO coffee_listings
      (farmer_id, coffee_type, processing_type, quantity, price, latitude, longitude)
      VALUES ($1,$2,$3,$4,$5,$6,$7) RETURNING *`,
      [
        farmer_id,
        coffee_type,
        processing_type,
        quantity,
        price,
        latitude,
        longitude
      ]
    );

    console.log("INSERT SUCCESS");

    res.json(result.rows[0]);

  } catch (err) {
    console.log("❌ ERROR:", err);
    res.status(500).json({ error: err.message });
  }
});

// Fetch Listings API
router.get("/listings", async(req,res)=>{

 const data = await pool.query(
  "SELECT * FROM coffee_listings"
 );

 res.json(data.rows);

});

router.get("/test", (req,res)=>{
  res.send("Market route working");
});

module.exports = router;