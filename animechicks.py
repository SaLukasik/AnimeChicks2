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
			'SELECT RANK() OVER (ORDER BY chick_wins DESC) place, chick_name, chick_gender, anime_title, chick_wins, chick_losses FROM CHICKS LEFT JOIN ANIME ON chick_anime = anime_id WHERE chick_name = (?) AND anime_title = (?) ORDER BY place',
			 (request.form['charactername'], request.form['animename'])):
			data.append(row)
	elif len(request.form) > 0 and len(request.form['charactername']) > 0:
		for row in cur.execute(
			'SELECT RANK() OVER (ORDER BY chick_wins DESC) place, chick_name, chick_gender, anime_title, chick_wins, chick_losses FROM CHICKS LEFT JOIN ANIME ON chick_anime = anime_id WHERE chick_name = (?) ORDER BY place',
			 (request.form['charactername'],)):
			data.append(row)
	elif len(request.form) > 0 and len(request.form['animename']) > 0:
		for row in cur.execute(
			'SELECT RANK() OVER (ORDER BY chick_wins DESC) place, chick_name, chick_gender, anime_title, chick_wins, chick_losses FROM CHICKS LEFT JOIN ANIME ON chick_anime = anime_id WHERE anime_title = (?) ORDER BY place',
			 (request.form['animename'],)):
			data.append(row)
	else:
		for row in cur.execute(
			'SELECT RANK() OVER (ORDER BY chick_wins DESC) place, chick_name, chick_gender, anime_title, chick_wins, chick_losses FROM CHICKS LEFT JOIN ANIME ON chick_anime = anime_id ORDER BY place'):
			data.append(row)
	headings = ("Place", "Name", "Gender", "Anime", "Wins", "Losses")
	return render_template('stats.html', headings=headings, data=data)

@app.route('/stats/<name>')
def stats_name(name):
	data = []
	for row in cur.execute('SELECT chick_name, chick_gender, chick_wins, chick_losses FROM CHICKS WHERE chick_name = (?) ORDER BY chick_wins DESC', (name,)):
		data.append(row)
	headings = ("Name", "Gender", "Wins", "Losses")
	return render_template('stats.html', headings=headings, data=data)

@app.route('/character/<id>')
def character(id):
	for row in cur.execute('SELECT * FROM CHICKS WHERE chick_id = (?)', (id)):
		chick = row

	return render_template('stats.html', the_chik=chick)
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
			cur.execute('UPDATE pojedynek SET result1 = result1 + 1 WHERE id1 = (?)', (winner[0],))
		else:
			cur.execute('UPDATE pojedynek SET result2 = result2 + 1 WHERE id2 = (?)', (winner[0],))
		con.commit()
		return entry_page()
	except:
		return entry_page()


@app.route('/')
def entry_page():
	if 'clicked' not in session:
		session['clicked'] = 0 
	files = os.listdir('pickles/')

	for row in cur.execute('SELECT * FROM CHICKS ORDER BY RANDOM() LIMIT 1'):
		girl1 = row
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