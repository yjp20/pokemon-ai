#!/usr/bin/env node
// maintainer: David Suh
// Mediator file to import pokedex information.

const dex = require('./thirdparty/Pokemon-Showdown/sim/dex.js');
const fs = require('fs');

function buildJSON(genstr, moddeddex) {
	// save all as json
	let data = JSON.stringify(moddeddex.dataCache, null, 2)
	fs.writeFileSync(`./data/dex/${genstr}.json`, data)
}

function buildLookupTable() {
	for (let i=1; i<=7; i++) {
		let genstr = `gen${i}`;
		buildJSON(genstr, new dex.ModdedDex(genstr))
	}
}

buildLookupTable()
