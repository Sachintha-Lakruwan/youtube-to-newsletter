const express = require("express");
const router = express.Router();
const KeyWords = require("../model/keywords");

// GET all keywords
router.get("/", async (req, res) => {
  try {
    const keywords = await KeyWords.find().select("-__v");
    res.status(200).send(keywords);
  } catch (err) {
    res.status(500).send({
      message: "Failed to get keywords",
      error: err.message,
    });
  }
});

// POST a new keyword
router.post("/", async (req, res) => {
  const keyword = new KeyWords({
    keyword: req.body.keyword,
  });
  try {
    const savedKeyWord = await keyword.save();
    res.status(201).send(savedKeyWord);
  } catch (err) {
    res.status(500).send({
      message: "Failed to save keyword",
      error: err.message,
    });
  }
});

// POST a bacth of new keywords
router.post("/batch", async (req, res) => {
  const keywords = req.body.keywords;

  if (keywords.length == 0 || !Array.isArray(keywords)) {
    return res
      .status(400)
      .send({ message: "Keywords must be a non-empty array" });
  }

  try {
    const savedKeywords = [];

    for (const word of keywords) {
      const keyword = new KeyWords({ keyword: word });
      const savedKeyword = await keyword.save();
      savedKeywords.push(savedKeyword);
    }

    res.status(201).send(savedKeywords);
  } catch (err) {
    res.status(500).send({
      message: "Failed to save kategories",
      err: err.message,
    });
  }
});

module.exports = router;
