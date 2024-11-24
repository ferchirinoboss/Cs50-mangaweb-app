from flask import Flask, redirect, render_template, request, session
import requests

app = Flask(__name__)

def add_manga(list, id, title, cover_art_id, cover_fileName):
    list.append({
        "id": id,
        "title": title,
        "cover_art_id": cover_art_id,
        "cover_fileName": cover_fileName,
        "cover_img": f"https://uploads.mangadex.org/covers/{id}/{cover_fileName}" 
    })

@app.route('/')
def index():
    return render_template("home.html")


@app.route('/library')
def library():
    return render_template("library.html")

@app.route('/search', methods=["GET", "POST"])
def search():
    manga_collection = []

    if request.method == 'POST':
        manga_name = request.form["search_query"]
        base_url = "https://api.mangadex.org"

        response = requests.get(
            f"{base_url}/manga",
            params={"title": manga_name}
        )

        for manga in response.json()["data"]:
            manga_id =  manga["id"]
            manga_title = manga["attributes"]["title"]["en"]

            for relationship in manga["relationships"]:
                if relationship["type"] == "cover_art":
                    cover_art_id = relationship["id"]


            cover_fileName_response = requests.get(
                f"{base_url}/cover/{cover_art_id}"
                # params={"id": cover_art_id}
            )
            cover_fileName = cover_fileName_response.json()["data"]["attributes"]["fileName"]

            add_manga(manga_collection, manga_id, manga_title, cover_art_id, cover_fileName)
            

        return render_template("search.html", manga_collection=manga_collection, cover_fileName_response=cover_fileName_response)

if __name__ == '__main__':
    app.run(debug=True)



