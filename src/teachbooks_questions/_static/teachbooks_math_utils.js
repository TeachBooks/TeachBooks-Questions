// Shared math utility helpers for TeachBooks question scripts.

import { ComputeEngine } from "https://esm.run/@cortex-js/compute-engine@0.55.6";

const ce = new ComputeEngine();

function jaroWinkler(a, b) {
  if (a === b) return 1;

  const m = Math.floor(Math.max(a.length, b.length) / 2) - 1;
  let matches = 0;
  let transpositions = 0;
  const aMatches = [];
  const bMatches = [];

  // matching window
  for (let i = 0; i < a.length; i++) {
    const start = Math.max(0, i - m);
    const end = Math.min(i + m + 1, b.length);
    for (let j = start; j < end; j++) {
      if (!bMatches[j] && a[i] === b[j]) {
        aMatches[i] = bMatches[j] = true;
        matches++;
        break;
      }
    }
  }
  if (!matches) return 0;

  // transpositions
  let k = 0;
  for (let i = 0; i < a.length; i++) {
    if (aMatches[i]) {
      while (!bMatches[k]) k++;
      if (a[i] !== b[k]) transpositions++;
      k++;
    }
  }
  transpositions /= 2;

  const jaro = (
    (matches / a.length) +
    (matches / b.length) +
    ((matches - transpositions) / matches)
  ) / 3;

  // Winkler prefix
  let prefix = 0;
  for (let i = 0; i < Math.min(4, a.length, b.length); i++) {
    if (a[i] === b[i]) prefix++;
    else break;
  }

  return jaro + prefix * 0.05 * (1 - jaro);
}

export function tunedSimilarity(student, correct) {
  const s = student.normalize("NFC").trim().toLowerCase();
  const c = correct.normalize("NFC").trim().toLowerCase();

  if (s === c) return 1;

  const base = jaroWinkler(s, c);

  // 1. prefix penalty (detects un-, in-, dis-, non-, mis-, etc.)
  const prefixFlips = ["un", "in", "im", "il", "ir", "non", "dis", "mis"];
  let prefixPenalty = 0;

  for (const p of prefixFlips) {
    if (correct.startsWith(p) !== student.startsWith(p)) {
      prefixPenalty += 0.08;
    }
  }

  // 2. keyword sensitivity: important words in the correct answer
  const keywords = correct
    .toLowerCase()
    .match(/[a-zA-Z]+/g)
    .filter((w) => w.length >= 4);

  let keywordPenalty = 0;
  keywords.forEach((word) => {
    if (!student.toLowerCase().includes(word)) {
      keywordPenalty += 0.02;
    }
  });

  // 3. length ratio penalty
  const lenRatio = student.length / correct.length;
  let lengthPenalty = 0;
  if (lenRatio < 0.75 || lenRatio > 1.35) {
    lengthPenalty = 0.05;
  }

  // final combined score
  let score = base - prefixPenalty - keywordPenalty - lengthPenalty;
  score = Math.max(0, Math.min(1, score));

  return score;
}

export function valueInInterval(value, interval) {
  const parts = interval.replace(/\s+/g, "").split("x");
  const nValue = ce.parse(value).evaluate().valueOf();

  // If the first part is empty, we have a format with one bound
  if (parts[0] === "") {
    if (parts[1].startsWith("<=")) {
      const bound = ce.parse(parts[1].split("<=")[1]).evaluate().valueOf();
      return nValue <= bound;
    }
    if (parts[1].startsWith("<")) {
      const bound = ce.parse(parts[1].split("<")[1]).evaluate().valueOf();
      return nValue < bound;
    }
    if (parts[1].startsWith(">=")) {
      const bound = ce.parse(parts[1].split(">=")[1]).evaluate().valueOf();
      return nValue >= bound;
    }
    if (parts[1].startsWith(">")) {
      const bound = ce.parse(parts[1].split(">")[1]).evaluate().valueOf();
      return nValue > bound;
    }
    console.error("Invalid interval format: ", interval);
    return false;
  }

  if (parts[1] === "") {
    console.error("Invalid interval format: ", interval);
    return false;
  }

  // We have a format with two bounds, so we need to check both.
  let left = false;
  let right = false;

  if (parts[0].endsWith("<=")) {
    const bound = ce.parse(parts[0].split("<=")[0]).evaluate().valueOf();
    if (nValue >= bound) left = true;
  } else if (parts[0].endsWith("<")) {
    const bound = ce.parse(parts[0].split("<")[0]).evaluate().valueOf();
    if (nValue > bound) left = true;
  }

  if (parts[1].startsWith("<=")) {
    const bound = ce.parse(parts[1].split("<=")[1]).evaluate().valueOf();
    if (nValue <= bound) right = true;
  } else if (parts[1].startsWith("<")) {
    const bound = ce.parse(parts[1].split("<")[1]).evaluate().valueOf();
    if (nValue < bound) right = true;
  }

  return left && right;
}

export function valueInIntervalNumerical(value, interval) {
  const parts = interval.replace(/\s+/g, "").split("x");
  const nValue = ce.parse(value).N().valueOf();

  // If the first part is empty, we have a format with one bound
  if (parts[0] === "") {
    if (parts[1].startsWith("<=")) {
      const bound = ce.parse(parts[1].split("<=")[1]).N().valueOf();
      return nValue <= bound;
    }
    if (parts[1].startsWith("<")) {
      const bound = ce.parse(parts[1].split("<")[1]).N().valueOf();
      return nValue < bound;
    }
    if (parts[1].startsWith(">=")) {
      const bound = ce.parse(parts[1].split(">=")[1]).N().valueOf();
      return nValue >= bound;
    }
    if (parts[1].startsWith(">")) {
      const bound = ce.parse(parts[1].split(">")[1]).N().valueOf();
      return nValue > bound;
    }
    console.error("Invalid interval format: ", interval);
    return false;
  }

  if (parts[1] === "") {
    console.error("Invalid interval format: ", interval);
    return false;
  }

  // We have a format with two bounds, so we need to check both.
  let left = false;
  let right = false;

  if (parts[0].endsWith("<=")) {
    const bound = ce.parse(parts[0].split("<=")[0]).N().valueOf();
    if (nValue >= bound) left = true;
  } else if (parts[0].endsWith("<")) {
    const bound = ce.parse(parts[0].split("<")[0]).N().valueOf();
    if (nValue > bound) left = true;
  }

  if (parts[1].startsWith("<=")) {
    const bound = ce.parse(parts[1].split("<=")[1]).N().valueOf();
    if (nValue <= bound) right = true;
  } else if (parts[1].startsWith("<")) {
    const bound = ce.parse(parts[1].split("<")[1]).N().valueOf();
    if (nValue < bound) right = true;
  }

  return left && right;
}

export function checkAbsolutePrecision(value, correct, precision) {
  const lowerBound = ce.box(["Subtract", ce.parse(correct), ce.parse(precision)]).toLatex();
  const upperBound = ce.box(["Add", ce.parse(correct), ce.parse(precision)]).toLatex();
  const interval = `${lowerBound} <= x <= ${upperBound}`;
  return valueInIntervalNumerical(value, interval);
}

export function checkRelativePrecision(value, correct, precision) {
  const absCenter = ce.box(["Abs", ce.parse(correct)]);
  const absPrecision = ce.box(["Multiply", absCenter, ce.parse(precision)]).toLatex();
  return checkAbsolutePrecision(value, correct, absPrecision);
}

export function containsError(node) {
  if (node === null || node === undefined) return false;

  // If it's an Error expression
  if (Array.isArray(node) && node[0] === "Error") {
    return true;
  }

  // If it's an array, recursively check all children
  if (Array.isArray(node)) {
    return node.some((child) => containsError(child));
  }

  // If it's an object, scan values recursively
  if (typeof node === "object") {
    return Object.values(node).some((value) => containsError(value));
  }

  // Primitive values have no nested error expression
  return false;
}
