#!/usr/bin/env node
const fs = require("fs");
const Ajv = require("ajv");
const addFormats = require("ajv-formats");
const ajv = new Ajv({allErrors:true, strict:true}); addFormats(ajv);
const schema = JSON.parse(fs.readFileSync("schema.json","utf8"));
const validate = ajv.compile(schema);
const files = fs.readdirSync(".").filter(f => /^#\d{3}_.*\.json$/.test(f));
let fail = 0;
for (const f of files) {
  const data = JSON.parse(fs.readFileSync(f,"utf8"));
  const ok = validate(data);
  if (!ok) { fail++; console.error("❌", f, validate.errors); }
}
if (fail) process.exit(1);
console.log("✅ all tablets valid");
