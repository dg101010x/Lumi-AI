#!/usr/bin/env node
"use strict";
// Minimal CLI for base64 encode/decode. Uses Node Buffer.
const fs = require('fs');

function usage() {
  console.error('Usage: cli.js <encode|decode> [--encoding utf8|ascii]');
  process.exit(2);
}

const argv = process.argv.slice(2);
if (argv.length === 0) usage();
const cmd = argv[0];
let encoding = 'utf8';
const encIndex = argv.indexOf('--encoding');
if (encIndex !== -1 && argv.length > encIndex + 1) encoding = argv[encIndex + 1];

const input = fs.readFileSync(0); // stdin as Buffer

if (cmd === 'encode') {
  let out;
  if (encoding === 'ascii') out = Buffer.from(input.toString('binary'), 'binary').toString('base64');
  else out = Buffer.from(input.toString('utf8'), 'utf8').toString('base64');
  process.stdout.write(out);
} else if (cmd === 'decode') {
  const b64 = input.toString('utf8').trim();
  const buf = Buffer.from(b64, 'base64');
  if (encoding === 'ascii') process.stdout.write(buf.toString('binary'));
  else process.stdout.write(buf.toString('utf8'));
} else {
  usage();
}
