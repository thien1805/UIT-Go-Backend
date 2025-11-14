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

// POST /api/get-data-location
app.post('/api/get-data-location', async (req, res) => {
  const { driver_id, lat, lng, status, timestamp } = req.body;

  // Validate required fields
  if (!driver_id || !lat || !lng) {
    return res.status(400).json({ error: 'Missing required fields (driver_id, lat, lng)' });
  }

  try {
    // Forward data to DriverService
    const response = await axios.post(`${DRIVER_SERVICE_URL}/charge`, {
      driver_id,
      lat,
      lng,
      status: status || 'online',
      timestamp: timestamp || new Date().toISOString()
    });

    // Return DriverService response to client
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
