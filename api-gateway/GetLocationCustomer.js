const path = require('path');
const dotenv = require('dotenv');
const cors = require('cors');
const express = require('express');
const axios = require('axios');

// Load environment variables
dotenv.config({ path: path.resolve(__dirname, '.env') });

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

const DRIVER_SERVICE_URL = process.env.DRIVER_SERVICE_URL || 'http://driver-service:3003';

// POST /api/get-data-location-customer
app.post('/api/get-data-location-customer', async (req, res) => {
  const {
    customer_id,
    pickup_lat,
    pickup_lng,
    destination_lat,
    destination_lng,
    timestamp
  } = req.body;

  // Validate required fields
  if (!customer_id || !pickup_lat || !pickup_lng || !destination_lat || !destination_lng) {
    return res.status(400).json({
      error: 'Missing required fields (customer_id, pickup_lat, pickup_lng, destination_lat, destination_lng)'
    });
  }

  try {
    // Forward data to DriverService (for matching logic)
    const response = await axios.post(`${DRIVER_SERVICE_URL}/find-driver`, {
      customer_id,
      pickup_lat,
      pickup_lng,
      destination_lat,
      destination_lng,
      timestamp: timestamp || new Date().toISOString()
    });

    // Forward DriverService response back to Frontend
    res.status(response.status).json(response.data);
  } catch (error) {
    console.error('Error contacting DriverService:', error.message);
    res.status(502).json({
      error: 'DriverService unavailable',
      details: error.message
    });
  }
});

module.exports = app;
