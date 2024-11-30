from flask import Flask, redirect, render_template, request, session, Response
import requests

app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template("home.html")


@app.route('/library')
def library():
    return render_template("library.html")

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
        manga_name = request.form["search_query"]
        base_url = "https://api.mangadex.org"

        response = requests.get(
            f"{base_url}/manga",
            params={
                "title": manga_name,
                "limit": 10,
            }
        )

        for manga in response.json()["data"]:
            manga_id =  manga["id"]
            manga_title = manga["attributes"]["title"]["en"]
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
            

        return render_template("search.html", manga_collection=manga_collection)


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


    return render_template("formanga.html", manga_title=manga_title, manga_description=manga_description, proxy_cover_url=proxy_cover_url, volume_list=volume_list, next_page= next_page, prev_page=prev_page, manga_id=manga_id, cover_fileName=cover_fileName)

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

    return render_template('chapter_reader.html', img_baseUrl=img_baseUrl, hash=hash, imgs_FileNames=imgs_FileNames, chapter_num=chapter_num)

if __name__ == '__main__':
    app.run(debug=True)



