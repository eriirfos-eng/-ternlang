// also validate no_domination.json against schemas/no_domination.schema.json
const ndSchema = JSON.parse(fs.readFileSync("schemas/no_domination.schema.json","utf8"));
const validateND = ajv.compile(ndSchema);
for (const f of ["no_domination/50_principles_of_no_domination.json"]) {
  if (!fs.existsSync(f)) continue;
  const data = JSON.parse(fs.readFileSync(f,"utf8"));
  const ok = validateND(data);
  if (!ok) { fail++; console.error("❌", f, validateND.errors); }
}
