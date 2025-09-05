const admin = require("firebase-admin");
require("dotenv").config();

// Initialize Firebase Admin (only once)
if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.applicationDefault(), // or use a service account JSON
  });
}

const authFirebase = () => {
  const api = process.env.API_URL;

  return async (req, res, next) => {
    // Skip paths that don’t require auth
    const openPaths = [
      `${api}/health`,
      "/",
      `${api}/keywords`,
      `${api}/keywords/batch`,
      `${api}/preferences`,
    ];
    if (openPaths.includes(req.path)) return next();

    try {
      const authHeader = req.headers.authorization || "";
      if (!authHeader.startsWith("Bearer ")) {
        return res.status(401).json({ message: "No token provided" });
      }

      const token = authHeader.split(" ")[1];

      // Verify Firebase token
      const decodedToken = await admin.auth().verifyIdToken(token);
      req.user = decodedToken; // attach user info to request
      next();
    } catch (err) {
      console.error(err);
      return res.status(401).json({ message: "Invalid or expired token" });
    }
  };
};

module.exports = authFirebase;
