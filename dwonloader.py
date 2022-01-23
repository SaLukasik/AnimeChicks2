import requests
import json
import sqlite3

CHICKSNUM = 1000

#Data base initialisation#########################################################################################
conn = sqlite3.connect('hotchicks2.db')
try:
    conn.execute('''CREATE TABLE CHICKS
             (CHICK_ID  NUMBER(6) PRIMARY KEY     NOT NULL,
             CHICK_ANIME   NUMBER(6)    NOT NULL,
             CHICK_NAME       TEXT     NOT NULL,
             CHICK_GENDER   TEXT,
             CHICK_IMAGE    TEXT,    
             CHICK_DESC     TEXT,
             CHICK_WINS    INT,
             CHICK_LOSSES   INT);''')
except:
    print('Chicks table has not been created')
try:
    conn.execute('''CREATE TABLE ANIME
             (ANIME_ID  NUMBER(6) PRIMARY KEY     NOT NULL,
             ANIME_TITLE    TEXT     NOT NULL);''')
except:
    print('Anime table has not been created')
try:
    conn.execute('''CREATE TABLE POJEDYNEK
             (ID1    NUMBER(6)    NOT NULL    REFERENCES CHICKS,
             ID2     NUMBER(6)    NOT NULL    REFERENCES CHICKS,
             RESULT1 NUMBER(6) NOT NULL,
	         RESULT2 NUMBER(6) NOT NULL,
	         CONSTRAINT pojedynek PRIMARY KEY (ID1,ID2));''')
except:
    print('Pojedynek table has not been created')
try:
    conn.execute('''CREATE TABLE RANKING
             (ID NUMBER(6) NOT NULL REFERENCES Character,
             PLACE NUMBER(6) NOT NULL,
	         CONSTRAINT ranking PRIMARY KEY (ID));''')
except:
    print('Ranking table has not been created')

#Pojedynek creation#########################################################################################
for i in range (1,CHICKSNUM+1):
    if (i == CHICKSNUM):
        break;
    for j in range(i+1, CHICKSNUM+1):
        conn.execute(f"INSERT OR REPLACE INTO POJEDYNEK (ID1,ID2, RESULT1, RESULT2) \
            VALUES ({i}, {j}, 0,0)");

##########################################################################################
#Characters and animes data loading#########################################################################################


url = 'https://www.animecharactersdatabase.com/api_series_characters.php?character_id=69'
headers = {
    'User-Agent': 'My User Agent 1.0',
    'From': 'youremail@domain.com'  # This is another valid field
}
def textclr(txt, char):
    if (char):
        txt['name'] = txt['name']. replace("'", "`")
        txt['desc'] = txt['desc']. replace("'", "`")
    else:
        txt['anime_name'] = txt['anime_name']. replace("'", "`")

def responder(url, headers):
    response = requests.get(url, headers=headers)
    if (response.status_code == 200):
        response = requests.get(url, headers=headers)
        return response.text
    else:
        print("Connection failed")


chicksList = []
animeList = []
animeid = -1
for i in range(1,CHICKSNUM+1):
    url = f'https://www.animecharactersdatabase.com/api_series_characters.php?character_id={i}'
    chickstr = responder(url, headers=headers)
    chickdic = json.loads(chickstr)
    chicksList.append(chickdic)
    textclr(chickdic, True)

    conn.execute(f"INSERT OR REPLACE INTO CHICKS (CHICK_ID,CHICK_ANIME, CHICK_NAME,CHICK_GENDER,CHICK_IMAGE,CHICK_DESC,CHICK_WINS, CHICK_LOSSES) \
         VALUES ({chickdic['id']},{chickdic['anime_id']},  '{chickdic['name']}', '{chickdic['gender']}', '{chickdic['character_image']}', '{chickdic['desc']}', 0,0)");

    conn.commit()
    print(f"{url} done")
    if (animeid != chickdic['anime_id']):
        animeid = chickdic['anime_id']
        url = f'https://www.animecharactersdatabase.com/api_series_characters.php?anime_id={animeid}'
        animestr = responder(url, headers=headers)
        animedic = json.loads(animestr)
        animeList.append(animedic)
        textclr(animedic, False)
        conn.execute(f"INSERT OR REPLACE INTO ANIME (ANIME_ID,ANIME_TITLE) \
            VALUES ({animedic['anime_id']}, '{animedic['anime_name']}')");
        conn.commit()
        print(f"{animedic['anime_name']} got added")
#print(chicksList[0])
#print(animeList[0])

'''cursor = conn.execute("SELECT CHICK_ID, CHICK_NAME, CHICK_IMAGE from CHICKS")
for row in cursor:
   print("ID = ", row[0])
   print( "NAME = ", row[1])
   print("SALARY = ", row[2], "\n")
cursor = conn.execute("SELECT * from ANIME")
for row in cursor:
   print("ID = ", row[0])
   print("SALARY = ", row[1], "\n")
cursor = conn.execute("SELECT * from POJEDYNEK")
for row in cursor:
   print("ID1 = ", row[0])
   print("ID2 = ", row[1])
   print("W1 = ", row[2])
   print("W2 = ", row[3], "\n")'''
conn.close()
print("Done!")

