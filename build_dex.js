#!/usr/bin/env node
/* Mediator file to import pokedex information.
*
* Writes dex data from the official Pokemon-Showdown project's dex
* to JSON files in the data folder.
*/

const dex = require('./thirdparty/Pokemon-Showdown/sim/dex.js');
const fs = require('fs');

function writeJSON(genstr, moddeddex) {
	let data = JSON.stringify(moddeddex.dataCache, null, 2)
	fs.writeFileSync(`./data/dex/${genstr}.json`, data)
}

function buildLookupTable() {
	for (let i=1; i<=7; i++) {
		let genstr = `gen${i}`;
		writeJSON(genstr, new dex.ModdedDex(genstr))
	}
}

buildLookupTable()
