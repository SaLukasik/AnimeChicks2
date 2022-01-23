from flask import Flask, render_template, url_for, session
import random, os, pickle
import sqlite3

app = Flask(__name__)

con = sqlite3.connect('hotchicks.db', check_same_thread=False)
cur = con.cursor()

ile_lasek = 100

def top_5():
		chicks = []
		for file in os.listdir('pickles/'):
			if not file.startswith('.'):
				with open('pickles/'+file, 'rb') as dbfile:
					x = pickle.load(dbfile)
					chicks.append(x)

		sortedchicks = sorted(chicks, key=lambda i: i['count'], reverse=True)
		return sortedchicks[0], sortedchicks[1], sortedchicks[2], sortedchicks[3], sortedchicks[4]

@app.route('/stats')
def stats():
	data = []
	for row in cur.execute('SELECT chick_name, chick_gender, chick_desc FROM CHICKS ORDER BY chick_id'):
		data.append(row)
	headings = ("Name", "Gender", "Description")

	return render_template('stats.html', headings=headings, data=data)

app.route('/character/<id>')
def character(id):
	for row in cur.execute('SELECT * FROM CHICKS WHERE chick_id = (?)', (id)):
		chick = row

	return render_template('stats.html', headings=headings, data=data)

@app.route('/vote/<direction>')
def click(direction):
	try:
		session['clicked'] += 1
		girl = session['girl1'] if direction == 'left' else session['girl2']

		with open('pickles/'+girl, 'rb') as dbfile:
			chick = pickle.load(dbfile)
			chick['count'] += 1
		with open('pickles/'+girl, 'wb') as dbfile:
			pickle.dump(chick, dbfile)   

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

	top1, top2, top3, top4, top5 = top_5()

	return render_template('index.html', the_chick1=list(girl1),
										 the_chick2=list(girl2),
										 the_top1 = top1,
										 the_top2 = top2,
										 the_top3 = top3,
										 the_top4 = top4,
										 the_top5 = top5,
										 the_click = session['clicked'])

app.secret_key = 'hdwhi3682bjd2'

if __name__ == '__main__':
	app.run(debug=True)