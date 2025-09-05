const mongoose = require("mongoose");

const keyWordSchema = new mongoose.Schema({
  keyword: { type: String, required: true },
});

module.exports = mongoose.model("KeyWord", keyWordSchema);
