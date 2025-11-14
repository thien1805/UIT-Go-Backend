const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const path = require('path');

// Import các module con (route handlers)
const GetLocationDriver = require('./GetLocationDriver.js');
const GetLocationCustomer = require('./GetLocationCustomer.js');

// Load biến môi trường
dotenv.config({ path: path.resolve(__dirname, '.env') });

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Gắn router con
app.use(GetLocationDriver);    // /api/get-data-location (tài xế)
app.use(GetLocationCustomer);  // /api/get-data-location-customer (khách hàng)

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`🚀 API Gateway running on port ${PORT}`);
});
