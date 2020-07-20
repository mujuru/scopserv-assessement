const http = require("http");
const bodyParser = require("body-parser");
const cors = require("cors");
const express = require("express");
const router = express.Router();
const app = express();
var mysql = require("mysql");
var os = require("os");

const port = 8085;

var con = mysql.createConnection({
  host: "db",
  user: "root",
  password: "paulo123",
  port: 3306,
});

con.connect(function (err) {
  if (err) throw err;
  con.query("CREATE DATABASE IF NOT EXISTS user", function (err, result) {
    if (err) throw err;
  });

  con.changeUser({ database: "user" }, function (err) {
    if (err) throw err;
  });

  con.query(
    "CREATE TABLE IF NOT EXISTS doc(" +
      "id int NOT NULL AUTO_INCREMENT," +
      "email varchar(32)," +
      " name varchar(32)," +
      " phone varchar(15)," +
      "PRIMARY KEY (id));",
    function (err, result) {
      if (err) throw err;
    }
  );

  con.query(
    "CREATE TABLE IF NOT EXISTS tel(" +
      "id int NOT NULL AUTO_INCREMENT," +
      "date_of_birth varchar(10)," +
      " postal_code varchar(4)," +
      "PRIMARY KEY (id));",
    function (err, result) {
      if (err) throw err;
    }
  );
});

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(cors());

//Web App save details route
app.post("/doc/add", (req, res) => {
  var email = req.body.email;
  var name = req.body.name;
  var phone = req.body.phone;

  var sql = "INSERT INTO doc (email, name, phone) VALUES ?";
  var values = [[email, name, phone]];
  con.query(sql, [values], function (err, result) {
    if (err) throw err;
    res.json({ id: result.insertId });
  });
});

//Web App retrieve details route
app.get("/doc", (req, res) => {
  con.query(
    "SELECT email, name, phone FROM doc WHERE id = " + req.param("id"),
    function (err, result, fields) {
      if (err) throw err;
      var doc = {
        email: result[0].email,
        name: result[0].name,
        phone: result[0].phone,
      };

      res.json(doc);
    }
  );
});

//Telephony App save data route
app.post("/tel/add", (req, res) => {
  var date_of_birth = req.body.dob;
  var postal_code = req.body.pc;

  var sql = "INSERT INTO tel (date_of_birth, postal_code) VALUES ?";
  var values = [[date_of_birth, postal_code]];
  con.query(sql, [values], function (err, result) {
    if (err) throw err;
    res.json({ id: result.insertId });
  });
});

app.listen(port, () =>
  console.log(`Backend app listening at http://localhost:${port}`)
);
