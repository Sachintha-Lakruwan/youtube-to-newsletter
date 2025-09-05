const express = require("express");
const router = express.Router();
const supabase = require("../helpers/supabase");

router.get("/", async (req, res) => {
  const email = req.query.email;
  const { data, error } = await supabase
    .from("users")
    .select("preferences")
    .eq("email", email);
  if (error) return res.status(500).json({ error: error.message });
  try {
    res.json(data[0]["preferences"]["topic"].split(" , "));
  } catch {
    res.json([]);
  }
});

router.post("/", async (req, res) => {
  const email = req.body.email;
  const keywords = req.body.keywords.join(" , ");

  const { data, error } = await supabase
    .from("users")
    .upsert(
      {
        email: email,
        preferences: { topic: keywords },
      },
      { onConflict: "email" } // ensures existing email rows are updated
    )
    .select(); // get the updated or inserted row

  if (error) return res.status(500).json({ error: error.message });
  res.json(data[0]);
});

module.exports = router;
