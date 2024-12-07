from flask import Flask, redirect, render_template, request, session, Response, g
import requests
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)



def add_manga(list, id, title, cover_art_id, cover_fileName, cover_img, description):
    list.append({
        "id": id,
        "title": title,
        "cover_art_id": cover_art_id,
        "cover_fileName": cover_fileName,
        "cover_img": cover_img, 
        "manga_description": description
    })

def add_chapter(id, volume, chapter, title):
    {
        "id": id,
        "volume": volume,
        "chapter": chapter,
        "title": title
    }

@app.before_request
def load_user():
    user_id = session.get("user_id")
    g.db_connection = sqlite3.connect('mangaweb.db', check_same_thread=False)
    g.db_connection.row_factory = sqlite3.Row
    g.db = g.db_connection.cursor()
    if user_id is not None:
        g.user_id = user_id
        username = g.db.execute("SELECT username FROM users WHERE id=?;", (int(user_id),)).fetchone()

        if username:
            g.username = username[0]
        else:
            g.username - None
    else:
        g.username = None 
        g.user_id = None

@app.teardown_appcontext
def close_db(error):       # ENSURES THE DB IS CLOESED 
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def index():
    base_url = "https://api.mangadex.org"
    manga_collection = []

    response = requests.get(
        f"{base_url}/manga",
            params={
                "order[updatedAt]": "desc", 
                "limit": 5,
            }
    )

    for manga in response.json()["data"]:
            manga_id =  manga["id"]
            try:
                manga_title = manga["attributes"]["title"]["en"]
            except:
                manga_title = manga["attributes"]["title"]["ja-ro"]

            try:
                manga_description = manga["attributes"]["description"]["en"]
            except: manga_description = 'no english description available'

            for relationship in manga["relationships"]:
                if relationship["type"] == "cover_art":
                    cover_art_id = relationship["id"]


                    cover_fileName_response = requests.get(
                        f"{base_url}/cover/{cover_art_id}"
                    )
                    cover_fileName = cover_fileName_response.json()["data"]["attributes"]["fileName"]
            
            if cover_fileName:
                cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{cover_fileName}"  

                # use the proxy route 
                proxy_cover_url = f"/proxy-cover?url={cover_url}"

            add_manga(manga_collection, manga_id, manga_title, cover_art_id, cover_fileName, proxy_cover_url, manga_description)


    return render_template("home.html", manga_collection=manga_collection, user_id=g.user_id, username=g.username)


@app.route('/save', methods=["POST"])
def save():
    if request.method == 'POST':
        if g.user_id:
            manga_id = request.form['manga_id']

            g.db.execute("INSERT INTO saved_mangas(user_id, manga_id) VALUES(?,?);", (g.user_id, str(manga_id)))
            g.db_connection.commit()
            
            return redirect("/library")
        else:
            return redirect("/login")

@app.route('/delete', methods=["POST"])
def delete():
    if request.method == "POST":
        manga_id = request.form["manga_id"]

        g.db.execute("DELETE FROM saved_mangas WHERE user_id = ? AND manga_id = ?;", (g.user_id, manga_id))
        g.db_connection.commit()

        return redirect("/library")
    

@app.route('/library')
def library():
    cursor = g.db_connection.execute("SELECT * FROM saved_mangas WHERE user_id =?;", (g.user_id,)).fetchall()
    saved_mangas = [dict(row) for row in cursor]
    manga_collection = []
    base_url = "https://api.mangadex.org"
    manga_id = 0

    for row in saved_mangas:
        manga_id = row['manga_id']

        response = requests.get(
            f"{base_url}/manga/{manga_id}",
        )
        manga = response.json()["data"]
        try:
            manga_title = manga["attributes"]["title"]["en"]
        except:
            manga_title = manga["attributes"]["title"]["ja-ro"]

        try:
            manga_description = manga["attributes"]["description"]["en"]
        except: manga_description = 'no english description available'

        for relationship in manga["relationships"]:
            if relationship["type"] == "cover_art":
                cover_art_id = relationship["id"]

                cover_fileName_response = requests.get(
                    f"{base_url}/cover/{cover_art_id}"
                )
                cover_fileName = cover_fileName_response.json()["data"]["attributes"]["fileName"]
        
        if cover_fileName:
            cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{cover_fileName}"  

            # use the proxy route 
            proxy_cover_url = f"/proxy-cover?url={cover_url}"

        add_manga(manga_collection, manga_id, manga_title, cover_art_id, cover_fileName, proxy_cover_url, manga_description)

    return render_template("library.html", user_id=g.user_id, username=g.username, manga_collection=manga_collection, manga_id=manga_id)

@app.route('/proxy-cover')    # PROXY FOR GETTING THE COVER IMG 
def proxy():
    cover_url = request.args.get('url')
    response = requests.get(cover_url, stream=True)
    if response.status_code == 200:
        return Response(response.content, content_type=response.headers['Content-Type'])
    else:
        return Response(f"Error fetching image: {response.status_code}", status=response.status_code)
    

@app.route('/search', methods=["GET", "POST"])
def search():
    manga_collection = []

    if request.method == 'POST':
        try:
            manga_name = request.form["search_query"]
        except:
            manga_name = request.args.get("search_query")
        base_url = "https://api.mangadex.org"
        limit = 5
        page = request.args.get('page', 1, type=int)
        offset = (page - 1) * limit

        response = requests.get(
            f"{base_url}/manga",
            params={
                "title": manga_name,
                "limit": limit,
                "offset": offset
            }
        )
        total_chapters = response.json()["total"]
        next_page = page + 1 if offset + limit < total_chapters else None
        prev_page = page - 1 if offset > 0 else None

        for manga in response.json()["data"]:
            manga_id =  manga["id"]
            try:
                manga_title = manga["attributes"]["title"]["en"]
            except:
                manga_title = manga["attributes"]["title"]["ja-ro"]

            try:
                manga_description = manga["attributes"]["description"]["en"]
            except: manga_description = 'no english description available'

            for relationship in manga["relationships"]:
                if relationship["type"] == "cover_art":
                    cover_art_id = relationship["id"]


                    cover_fileName_response = requests.get(
                        f"{base_url}/cover/{cover_art_id}"
                    )
                    cover_fileName = cover_fileName_response.json()["data"]["attributes"]["fileName"]
            
            if cover_fileName:
                cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{cover_fileName}"  

                # use the proxy route 
                proxy_cover_url = f"/proxy-cover?url={cover_url}"

            add_manga(manga_collection, manga_id, manga_title, cover_art_id, cover_fileName, proxy_cover_url, manga_description)
            

        return render_template("search.html", manga_collection=manga_collection, query=manga_name, prev_page=prev_page, next_page=next_page, user_id=g.user_id, username=g.username)


@app.route('/forManga/<manga_id>/<cover_fileName>')
def forManga(manga_id, cover_fileName):
    base_url = "https://api.mangadex.org"
    volume_list = []
    limit = 100
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * limit


    manga_resp = requests.get(
        f'{base_url}/manga/{manga_id}'
    )

    manga_resp_data = manga_resp.json()["data"]
    manga_title = manga_resp_data["attributes"]["title"]["en"]
    try:
        manga_description = manga_resp_data["attributes"]["description"]["en"]
    except: manga_description = 'no english description available'

    cover_url = f"https://uploads.mangadex.org/covers/{manga_id}/{cover_fileName}"  

    # use the proxy route to get the cover image
    proxy_cover_url = f"/proxy-cover?url={cover_url}"


    response = requests.get(
            f"{base_url}/manga/{manga_id}/feed",
            params={
                "offset": offset,
                "limit": limit,
                "translatedLanguage[]": "en",
                "order[volume]": "desc",
                "order[chapter]": "desc"
            }
    )
    total_chapters = response.json()["total"]
    next_page = page + 1 if offset + limit < total_chapters else None
    prev_page = page - 1 if offset > 0 else None
    
    for chapter in response.json()["data"]:
        chapter_id = chapter['id']
        chapter_num = chapter['attributes']['chapter']
        volume = chapter['attributes']['volume']
        title = chapter['attributes']['title']

        volume_entry = next((v for v in volume_list if v["volume"] == volume), None)
        if not volume_entry:
            volume_entry = {
                "volume": volume,
                "chapters": []
                }
            volume_list.append(volume_entry)
        chapter_data = {
            "id": chapter_id,
            "chapter": chapter_num,
            "title": title
        }

        volume_entry["chapters"].append(chapter_data)
        
        # volume_list["chapters"].append(add_chapter(chapter_id, volume, chapter_num, title))


    return render_template("formanga.html", manga_title=manga_title, manga_description=manga_description, proxy_cover_url=proxy_cover_url, volume_list=volume_list, next_page= next_page, prev_page=prev_page, manga_id=manga_id, cover_fileName=cover_fileName, user_id=g.user_id, username=g.username)

@app.route('/chapter/<chapter_num>/<chapter_id>')
def chapter(chapter_num, chapter_id):
    base_url = "https://api.mangadex.org/at-home/server/"

    response = requests.get(
        f'{base_url}{chapter_id}'
    )

    img_baseUrl = response.json()['baseUrl']
    data = response.json()['chapter']
    hash = data["hash"]
    imgs_FileNames = data["data"]

    return render_template('chapter_reader.html', img_baseUrl=img_baseUrl, hash=hash, imgs_FileNames=imgs_FileNames, chapter_num=chapter_num, user_id=g.user_id, username=g.username)


@app.route('/login', methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        alert_message = None

        if not username or not password:
            alert_message = 'username and password required'

        rows = g.db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):  
            alert_message = 'invalid username or password'
        else:
            session["user_id"] = rows[0]["id"]
            return redirect("/")
        
        
        return render_template("login.html", alert_message=alert_message, user_id=g.user_id, username=g.username)
    return render_template("login.html", user_id=g.user_id, username=g.username)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        confirmation = request.form["confirmation"]
        alert_message = None
        hashed_password = generate_password_hash(password, salt_length=2)

        try:
            g.db.execute("INSERT INTO users(username, hash) VALUES(?,?);", (username, hashed_password))
        except ValueError:
            alert_message = 'Problem with username'

        if not password or not confirmation:
            alert_message = 'Problem with password'
        elif password != confirmation:
            alert_message = 'Problem with password'
        

        return render_template("register.html", alert_message=alert_message, user_id=g.user_id, username=g.username)
    
    return render_template("register.html", user_id=g.user_id, username=g.username)

@app.route('/logout')
def logout():
    session.clear()

    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)



