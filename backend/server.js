const express = require("express");
const cors = require("cors");

const chatbotRoutes = require("./routes/chatbot");
const marketRoutes = require("./routes/market");
<<<<<<< HEAD
const authRoutes = require("./routes/auth");
=======
>>>>>>> d6b66db (first commit)

const app = express();

app.use(cors());

<<<<<<< HEAD

app.use(express.json());

app.use("/auth", authRoutes);
=======
// 🔥 VERY IMPORTANT (must be BEFORE routes)
app.use(express.json());

>>>>>>> d6b66db (first commit)
app.use("/chatbot", chatbotRoutes);
app.use("/market", marketRoutes);

app.listen(5000, "0.0.0.0", () => {
  console.log("Server running on port 5000");
});