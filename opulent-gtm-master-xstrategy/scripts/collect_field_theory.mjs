import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { resolve } from "node:path";

const ft = "/Users/agent/.local/bin/fieldtheory";
const root = resolve(import.meta.dirname, "..");
const searchQueries = [
  "GTM", "sales", "marketing", "outbound", "pipeline", "ICP", "prospecting",
  "enrichment", "cold email", "LinkedIn", "CRM", "revenue", "growth",
  "distribution", "partnership", "founder led sales", "sales engineer",
  "company research", "buyer intent", "account research", "personalization",
  "pricing", "discovery call", "sales process", "follow up", "deliverability",
  "content marketing", "programmatic SEO", "competitor", "conference",
  "intent signal", "job postings", "public database", "technical sales",
  "champion", "deal desk", "demo", "post sale", "customer research",
  "positioning", "messaging", "account memory", "playbook", "human approval",
  "SDR", "PLG", "sales engineering", "growth engineer", "revenue engineer",
  "social selling", "case study", "referral", "customer success", "RevOps",
  "sales enablement", "product led", "sales call", "customer proof",
];
const libraryQueries = [
  "GTM", "sales", "outbound", "prospecting", "company research", "enrichment",
  "LinkedIn", "marketing", "revenue", "pipeline", "positioning", "messaging",
];

function runJson(args) {
  try {
    const output = execFileSync(ft, args, { encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
    return JSON.parse(output);
  } catch (error) {
    return { error: String(error.stderr || error.message || error) };
  }
}

const records = new Map();
const queryStats = [];
for (const query of searchQueries) {
  const result = runJson(["search", query, "--limit", "100", "--json"]);
  const items = Array.isArray(result) ? result : [];
  queryStats.push({ query, count: items.length });
  for (const item of items) {
    const existing = records.get(item.id) || { ...item, matchedQueries: [] };
    if (!existing.matchedQueries.includes(query)) existing.matchedQueries.push(query);
    records.set(item.id, existing);
  }
}

const library = [];
for (const command of ["grep", "find"]) {
  for (const query of libraryQueries) {
    const result = runJson([command, query, "--limit", "100", "--json"]);
    library.push({ command, query, result });
  }
}

const corpus = {
  generatedAt: new Date().toISOString(),
  fieldTheoryVersion: execFileSync(ft, ["--version"], { encoding: "utf8" }).trim(),
  queryStats,
  uniqueBookmarkCount: records.size,
  bookmarks: [...records.values()].sort((a, b) => String(b.postedAt).localeCompare(String(a.postedAt))),
  library,
};

writeFileSync(resolve(root, "research", "evidence", "field-theory-gtm-sales-corpus.json"), JSON.stringify(corpus, null, 2) + "\n");
console.log(JSON.stringify({ uniqueBookmarkCount: corpus.uniqueBookmarkCount, queryStats }, null, 2));
