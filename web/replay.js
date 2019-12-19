function linkStyle(url) {
	var linkEl = document.createElement('link');
	linkEl.rel = 'stylesheet';
	linkEl.href = url;
	document.head.appendChild(linkEl);
}
function requireScript(url) {
	var scriptEl = document.createElement('script');
	scriptEl.src = url;
	document.head.appendChild(scriptEl);
}

PREFIX="./web/pokemon-showdown-client"

linkStyle(PREFIX+'/style/font-awesome.css?');
linkStyle(PREFIX+'/style/battle.css');
linkStyle(PREFIX+'/style/replay.css');

requireScript(PREFIX+'/js/lib/jquery-1.11.0.min.js');
requireScript(PREFIX+'/js/lib/lodash.compat.js');
requireScript(PREFIX+'/js/lib/html-sanitizer-minified.js');
requireScript(PREFIX+'/js/lib/soundmanager2-nodebug-jsmin.js');
requireScript(PREFIX+'/js/config.js');
requireScript(PREFIX+'/js/battledata.js');
requireScript(PREFIX+'/data/pokedex-mini.js');
requireScript(PREFIX+'/data/pokedex-mini-bw.js');
requireScript(PREFIX+'/data/graphics.js');
requireScript(PREFIX+'/data/pokedex.js');
requireScript(PREFIX+'/data/moves.js');
requireScript(PREFIX+'/data/abilities.js');
requireScript(PREFIX+'/data/items.js');
requireScript(PREFIX+'/data/teambuilder-tables.js');
requireScript(PREFIX+'/js/battle-tooltips.js');
requireScript(PREFIX+'/js/battle.js');

var Replay = {
	init: function () {

		// Showdown
		const battle = $("#battle")
		const battle_log = $("#battle-log")
		const log = $("#log").text()
		this.battle = new Battle(battle, battle_log)
		this.battle.setQueue(log.split('\n'))
		this.battle.reset()

		// Gamestate loggers
		const options = {
			mode: "view",
			mainMenuBar: false,
		}
		this.gs1 = JSON.parse($("#bot1").text())
		this.gs2 = JSON.parse($("#bot2").text())
		this.gs1norm = JSON.parse($("#bot1-norm").text())
		this.gs2norm = JSON.parse($("#bot2-norm").text())

		var b1 = document.getElementById("bot1-viewer")
		var b2 = document.getElementById("bot2-viewer")
		var b1norm = document.getElementById("bot1-norm-viewer")
		var b2norm = document.getElementById("bot2-norm-viewer")

		this.gs1Editor = new JSONEditor(b1, options)
		this.gs2Editor = new JSONEditor(b2, options)
		this.gs1NormEditor = new JSONEditor(b1norm, options)
		this.gs2NormEditor = new JSONEditor(b2norm, options)

		this.gs1Editor.set()
		this.gs2Editor.set()
		this.gs1NormEditor.set()
		this.gs2NormEditor.set()

		this.editor = null
	},
	next: function () {
		this.battle.skipTurn()
	},
	back: function () {
		if (this.battle.turn) {
			this.battle.fastForwardTo(this.battle.turn - 1)
		}
	},
	reset: function () {
		this.battle.reset()
		this.battle.fastForwardTo(0)
	},
	nextEditor: function () {
		if (this.editor == null) this.setEditors(0)
		else this.setEditors(this.editor + 1)
	},
	backEditor: function () {
		this.setEditors(this.editor - 1)
	},
	setEditors: function (idx) {
		this.editor = idx
		if (idx != null) {
			this.gs1Editor.set(this.gs1[idx])
			this.gs2Editor.set(this.gs2[idx])
			this.gs1NormEditor.set(this.gs1norm[idx])
			this.gs2NormEditor.set(this.gs2norm[idx])
		}
		else {
			this.gs1Editor.set({})
			this.gs2Editor.set({})
			this.gs1NormEditor.set({})
			this.gs2NormEditor.set({})
		}
	},
	gamestate_logs: [],
	gs1: null,
	gs2: null,
	gs1Editor: null,
	gs2Editor: null,
	log: null,
}

window.onload = function () {
	Replay.init()
}
