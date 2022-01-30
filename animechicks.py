from flask import Flask, render_template, url_for, session, request
import random, os, pickle
import sqlite3

app = Flask(__name__)

con = sqlite3.connect('hotchicks2.db', check_same_thread=False)
cur = con.cursor()

def top_5():
	data = []
	for row in cur.execute('SELECT * FROM CHICKS ORDER BY chick_wins DESC LIMIT 5'):
		data.append(row)
	return data
		

@app.route('/stats', methods=["GET", "POST"])
def stats():
	data = []
	if len(request.form) > 0 and len(request.form['charactername']) > 0 and len(request.form['animename']):
		for row in cur.execute(
			'SELECT COUNT(*) place, A.chick_id, MAX(A.chick_name), MAX(A.chick_gender), MAX(anime_title), MAX(A.chick_wins), MAX(A.chick_losses) FROM ((chicks A LEFT JOIN chicks B ON A.chick_wins < B.chick_wins) LEFT JOIN anime ON A.chick_anime = anime_id) WHERE A.chick_name = (?) AND anime_title = (?) GROUP BY A.chick_id ORDER BY place',
			 (request.form['charactername'], request.form['animename'])):
			data.append(row)
	elif len(request.form) > 0 and len(request.form['charactername']) > 0:
		for row in cur.execute(
			'SELECT COUNT(*) place, A.chick_id, MAX(A.chick_name), MAX(A.chick_gender), MAX(anime_title), MAX(A.chick_wins), MAX(A.chick_losses) FROM ((chicks A LEFT JOIN chicks B ON A.chick_wins < B.chick_wins) LEFT JOIN anime ON A.chick_anime = anime_id) WHERE A.chick_name = (?) GROUP BY A.chick_id ORDER BY place',
			 (request.form['charactername'],)):
			data.append(row)
	elif len(request.form) > 0 and len(request.form['animename']) > 0:
		for row in cur.execute(
			'SELECT COUNT(*) place, A.chick_id, MAX(A.chick_name), MAX(A.chick_gender), MAX(anime_title), MAX(A.chick_wins), MAX(A.chick_losses) FROM ((chicks A LEFT JOIN chicks B ON A.chick_wins < B.chick_wins) LEFT JOIN anime ON A.chick_anime = anime_id) WHERE anime_title = (?) GROUP BY A.chick_id ORDER BY place',
			 (request.form['animename'],)):
			data.append(row)
	else:
		for row in cur.execute(
			'SELECT COUNT(*) place, A.chick_id, MAX(A.chick_name), MAX(A.chick_gender), MAX(anime_title), MAX(A.chick_wins), MAX(A.chick_losses) FROM ((chicks A LEFT JOIN chicks B ON A.chick_wins < B.chick_wins) LEFT JOIN anime ON A.chick_anime = anime_id) GROUP BY A.chick_id ORDER BY place'):
			data.append(row)

	for row in cur.execute(
			'SELECT SUM(chick_wins) FROM chicks'):
			count = row
	headings = ("Place", "Name", "Gender", "Anime", "Wins", "Losses")
	return render_template('stats.html', headings=headings, data=data, count=count)


@app.route('/character/<id>')
def character(id):
	data = []
	for row in cur.execute('SELECT id2, chick_name, result1, result2 FROM POJEDYNEK LEFT JOIN chicks ON id2 = chick_id WHERE id1 = (?)  UNION SELECT id1, chick_name, result2, result1 FROM POJEDYNEK LEFT JOIN chicks ON id1 = chick_id WHERE id2 = (?) ORDER BY result1 DESC', (id,id)):
		data.append(row)

	for row in cur.execute('SELECT chick_name, chick_gender, chick_image, chick_desc, chick_wins, chick_losses, anime_title FROM CHICKS LEFT JOIN ANIME ON chick_anime = anime_id WHERE chick_id = (?)', (id,)):
		character = row

	headings = ("ID", "Name", "Wins", "Losses")
	top = ("Gender", "Anime", "Wins", "Losses")
	return render_template('character.html', the_character = character, data = data, headings = headings, top = top)


@app.route('/vote/<direction>')
def click(direction):
	try:
		session['clicked'] += 1
		if (direction == 'left'):
			winner = session['girl1']
			loser = session['girl2']
		else:
			winner = session['girl2']
			loser = session['girl1']
		cur.execute('UPDATE chicks SET chick_wins = chick_wins + 1 WHERE chick_id = (?)', (winner[0],))
		cur.execute('UPDATE chicks SET chick_losses = chick_losses + 1 WHERE chick_id = (?)', (loser[0],)) 
		if winner[0] < loser[0]:
			cur.execute('UPDATE pojedynek SET result1 = result1 + 1 WHERE id1 = (?) AND id2 = (?)', (winner[0], loser[0]))
		else:
			cur.execute('UPDATE pojedynek SET result2 = result2 + 1 WHERE id2 = (?) AND id1 = (?)', (winner[0], loser[0]))
		con.commit()
		return entry_page()
	except:
		return entry_page()


@app.route('/', methods=["GET", "POST"])
def entry_page():
	if 'clicked' not in session:
		session['clicked'] = 0 
	for row in cur.execute('SELECT * FROM CHICKS ORDER BY RANDOM() LIMIT 1'):
		girl1 = row

	girl2 = girl1
	while (girl2 == girl1):
		for row in cur.execute('SELECT * FROM CHICKS ORDER BY RANDOM() LIMIT 1'):
			girl2 = row

	session['girl1'] = girl1
	session['girl2'] = girl2

	top5 = top_5()

	return render_template('index.html', the_chick1=list(girl1),
										 the_chick2=list(girl2),
										 the_top5 = top5,
										 the_click = session['clicked'])

app.secret_key = 'hdwhi3682bjd2'

if __name__ == '__main__':
	app.run(debug=True)