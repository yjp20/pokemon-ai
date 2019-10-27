/*
 * This file runs multiple pokemon battles syncronously.
 * Because the majority of the time taken when simulating a battle
 * is used on loading the dex, we should be able to significantly
 * speed up execution through this file.
 *
 * In fact, preliminary testing shows that this method is around an
 * order of magnitude faster for the easiest algorithm in which case the
 * time to execute is negligible.
 */

const DistLocation = './thirdparty/Pokemon-Showdown'
const BattleTextStream = require(DistLocation+'/.sim-dist/battle-stream').BattleTextStream
const Streams = require(DistLocation+'/.lib-dist/streams')
const readline = require('readline')
const fs = require('fs')

var debug = true
var stdin = new Streams.ReadStream(process.stdin)
var stdout = new Streams.WriteStream(process.stdout)

async function getnum() {
	var l = await stdin.readLine()
	return parseInt(l.trim())
}

function dbg(n, s) {
	if (n && debug) fs.appendFile(n, s, (err) => {})
}

async function write(i, o, n) {
	dbg(n, "--NEW--\n")
	let output = '';
	while ((output = await i.read())) {
		o.write(output)
		dbg(n, output)
		if (output.includes('\x04')) break;
	}
}

async function start() {
	var num = await getnum()
	while (num > 0) {
		dbg("wownum", num+'\n')
		var bs = new BattleTextStream()
		bs.start()
		const s1 = write(stdin, bs, "wow")
		const s2 = write(bs, stdout, "wowza")
		stdout.write("START\n")
		await s2
		stdout.write("END\n")
		await s1
		bs.destroy()
		num --;
	}
}

start()
