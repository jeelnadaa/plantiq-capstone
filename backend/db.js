const { Pool } = require("pg");

const pool = new Pool({
  user: "postgres",
  host: "localhost",
  database: "plantiq",
  password: "nidhi",
  port: 5432
});

module.exports = pool;