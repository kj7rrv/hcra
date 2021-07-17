function resize() {
	let bodyWidth = window.innerWidth
	let maxWidth = Math.min(bodyWidth - 60, 800)
	let bodyHeight = window.innerHeight
	let maxHeight = Math.min(bodyHeight - 60, 480)
	let equivalentHeight = maxWidth * 0.6
	if (equivalentHeight >= maxHeight) {
		displayHeight = Math.round(maxHeight)
		displayWidth = Math.round(maxHeight * (5/3))
	} else {
		displayWidth = Math.round(maxWidth)
		displayHeight = Math.round(maxWidth * 0.6)
	}
	img.style.width = displayWidth + 'px'
	img.style.height = displayHeight + 'px'
	errorbox.style.width = displayWidth + 'px'
	errorbox.style.height = displayHeight + 'px'
}


function setup() {
	ws = new WebSocket(localStorage.getItem('url'))
	ws.onmessage = function(e) {
		window.m = e
		let type, data, code, msg
		type = e.data.split('%')[0]
		if (type == 'ver') {
			ws.send('pass ' + localStorage.getItem('password'))
			setInterval(function(){ws.send('ack')}, 3000)
		} else if ( type == 'pic' ) {
			data = e.data.split('%')[2]
			img.src = data
			errorbox.style.display = 'none'
			img.style.display = 'block'
		} else if ( type == 'err' ) {
			code = e.data.split('%')[1]
			msg = e.data.split('%')[2]
			errorbox.textContent = msg
			errorbox.style.display = 'block'
			img.style.display = 'none'
			console.error('Server reported error: ' + code + ': ' + msg)
			if (code[0] == '*') {
				errorbox.innerHTML = msg + '<br>Please refresh page'
				ws.onclose = function(e){}
				ws.onerror = function(e){}
			}
		} else if (type == 'ack') {
			ws.send('ack')
		}
	}
	ws.onerror = function(e){
		errorbox.innerHTML = 'Connection lost<br>Please refresh page'
		errorbox.style.display = 'block'
		img.style.display = 'none'
	}
	ws.onclose = function(e){
		errorbox.innerHTML = 'Connection lost<br>Please refresh page'
		errorbox.style.display = 'block'
		img.style.display = 'none'
	}
	ws.onopen = function(e) {
		ws.send('maxver 1')
	}
}


function touch(e) {
	click_timeout = setTimeout(function() {
		is_short = false
	}, 1000)
	is_short = true
}


function release(e) {
	x = e.offsetX || e.layerX
	y = e.offsetY || e.layerY
	w = displayWidth
	length = is_short?false:true
	ws.send('touch ' + x + ' ' + y + ' ' + w + ' ' + length)
	clearTimeout(click_timeout)
	is_short = true
}


function connect(e) {
	e.preventDefault()
	holder.style.display = 'block'
	login.style.display = 'none'
	localStorage.setItem('url', url_el.value)
	localStorage.setItem('password', password_el.value)
	setup()
}


let img = document.querySelector('#img')
let errorbox = document.querySelector('#errorbox')

let login = document.querySelector('#login')
let holder = document.querySelector('#holder')

let url_el = document.querySelector('#url')
let password_el = document.querySelector('#password')
let start_button = document.querySelector('#start')

let is_short = true
let click_timeout

let displayWidth, displayHeight

let ws


resize()
window.onresize = resize

img.onmousedown = touch
img.onmouseup = release

start.onclick = connect
