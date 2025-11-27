const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    await mongoose.connect(`${process.env.URL_MONGODB_SERVER}/trip-service`);
    console.log('MongoDB connected...');
  } catch (error) {
    console.error('Error connecting to MongoDB:', error);
    process.exit(1); 
  }
};

module.exports = connectDB;
