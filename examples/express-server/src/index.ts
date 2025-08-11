import "./instrumentation.ts";

import express from "express";

const app = express();
const port = process.env.PORT || 9999;

app.get("/", (req, res) => {
  res.send("Hello, World!");
});

app.post("/v1/write", (req, res) => {
  console.log("Received a POST request to /v1/write");
  console.log("Request body:", req.body);
  res.status(200).send("Data received successfully");
})

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
