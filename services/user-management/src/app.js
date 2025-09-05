const express = require("express");
const app = express();
const authJwt = require("./helpers/jwt");
const bodyParser = require("body-parser");
const morgan = require("morgan");
const mongoose = require("mongoose");
const cors = require("cors");

// Load environment variables
require("dotenv").config();

const api = process.env.API_URL || "/api/v1";
const mongoUri = process.env.MONGO_URI;
const port = process.env.PORT || 8080;

//MongoDB connection
mongoose
  .connect(mongoUri, { dbName: "news-letters" })
  .then(() => {
    console.log("Connected to MongoDB");
  })
  .catch((err) => {
    console.error("Failed to connect to MongoDB:", err);
  });

//middleware
app.use(bodyParser.json());
app.use(cors());
app.use(morgan("tiny")); // logs errors with a short summary
app.use(authJwt());

// Health check endpoint for Vercel (under API path)
app.get(`${api}/health`, (req, res) => {
  res.status(200).json({ status: "OK", message: "Server is running" });
});

//Routes
const keyWordsRouter = require("./routers/keywords");
app.use(`${api}/keywords`, keyWordsRouter);

const preferencesRouter = require("./routers/preferences");
app.use(`${api}/preferences`, preferencesRouter);

// Root endpoint
app.get("/", (req, res) => {
  res.status(200).json({
    message: "Youtube to Newsletter - User manager API is running",
    version: "1.0.0",
    endpoints: {
      health: `${api}/health`,
      keywords: `${api}/keywords`,
      preferences: `${api}/preferences`,
    },
  });
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});

module.exports = app;
