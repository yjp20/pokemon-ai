/*
 * This file runs multiple pokemon battles syncronously.  Because the
 * majority of the time taken when simulating a battle is used on
 * loading the dex, we should be able to significantly speed up
 * execution through this file.
 *
 * In fact, preliminary testing shows that this method is around an order of
 * magnitude faster for the easiest algorithm in which case the time to execute
 * is negligible.
 *
 * At just one test, it takes around 3 seconds, while at 100 tests it takes
 * around 0.3 second per test.
 */

const DistLocation = '../thirdparty/Pokemon-Showdown'
const BattleTextStream = require(DistLocation+'/.sim-dist/battle-stream').BattleTextStream
const Streams = require(DistLocation+'/.lib-dist/streams')
const readline = require('readline')
const fs = require('fs')

var debug = false
var stdin = new Streams.ReadStream(process.stdin)
var stdout = new Streams.WriteStream(process.stdout)

function dbg(n, s) {
	if (n && debug) fs.appendFile(n, s, (err) => {})
}

async function write(i, o, n) {
	dbg(n, "--NEW--\n")
	let output = '';
	while ((output = await i.read())) {
		dbg(n, output)
		dbg("wowlen", output.length + '\n')
		if (output.includes('\x04')) {
			dbg(n, "--BREAK--\n")
			dbg(n, output+"\n")
			dbg(n, "---------\n")
			break;
		}
		o.write(output)
	}
}

async function start() {
	while (1) {
		var bs = new BattleTextStream()
		bs.start()
		const s1 = write(stdin, bs, "wow")
		const s2 = write(bs, stdout, "wowza")
		stdout.write("START\n")
		await s2
		dbg("wowza", "--FIN--\n")
		stdout.write("END\n")
		await s1
		dbg("wow", "--FIN--\n")
		bs.destroy()
	}
}

start()
