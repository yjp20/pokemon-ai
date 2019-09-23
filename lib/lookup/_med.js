// maintainer: David Suh
// Mediator file to import pokedex information.

const filePath = `../../thirdparty/Pokemon-Showdown/mods/`;
const fs = require('fs');

function importShowdownModsFile(genstr, filename) {
    return require(filePath+genstr+'/'+filename);
}

function buildJSON(obj_table) {
    // save all as json
    Object.keys(obj_table).forEach((key, index) => {
        let data = JSON.stringify(obj_table[key])
        fs.writeFileSync(`./data/${key}.json`, data)
    })
}

function buildLookupTable(generation) {
    let genstr = `gen${generation}`;
    let inf = {};

    // import the neccessary files that are there for every generation
    inf.movedex = importShowdownModsFile(genstr, 'moves.js')
    inf.pokedex = importShowdownModsFile(genstr, 'pokedex.js')
    inf.status =  importShowdownModsFile(genstr, 'statuses.js')
    inf.formatData = importShowdownModsFile(genstr, 'formats-data.js')
    // import the files that exist only for certain generations

    if (generation >= 2) {
        inf.items = importShowdownModsFile(genstr, 'items.js')
    }

    if (generation >= 3) {
        inf.abilities = importShowdownModsFile(genstr, 'abilities.js')
    }

    buildJSON(inf)
}

//for now, import generation 1
buildLookupTable(1);

