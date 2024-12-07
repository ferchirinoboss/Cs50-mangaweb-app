# Cs50-mangaweb-app
### Video Demo:  <URL HERE>
### Description:

This proyect is a web app for reading manga using flask and Mangadex's API. I will now explain what does each file does. 

## app.py
At the top of the file after initializing Flask app we have 2 functions:

#### def add_manga 
This function takes a list and appends to it a dictionary with the id, title, covert_art_id, cover_fileName, cover_img, and description for a manga 

#### def add_chapter 
This function returns a dictionary with the id, volume, chapter, and its title for a manga chapter. 

#### @app.before_request
This part makes the connection with the database, gets the user id and username, and stores this data in "g." to be able to access them in all routes. Basically, it makes the equivalent of python's global variables. 

#### @app.teardown_appcontext
This part ensures the database is closed correctly.

### Routes

#### '/'
This is the homepage of the website and it gets via a request method to the Mangadex API 5 mangas that have been recently updated or modified. In the for loop inside this route we get the necessary information to make a list of dictionaries called manga_collection using the add_manga funtion.

Finally, it renders the home.html template and passes the manga_collection the user id and the username. 

#### '/save'
This route works as a saving functionality to add mangas to your library if your are logged in. It recevies a manga_id and it inserts it with the user id to the saved_mangas table on the databse. If your are logged in it redirects you to the library, otherwise it redirects you to the login page. 

#### '/delete'
This route works similarly as the '/save' route except it deletes the manga from the database and redirects you to the library. 


#### '/library'
This part gets all the saved mangas the user has on the database and makes all the necessary request to the API to get all the information to make the manga_collection and this is passed to the library template. If the user is not logged in the manga_collection will be empty and the library page won't show anything. 

#### '/proxy-cover'
This part serves as a proxy to get the images from the API because otherwise the images wouldn't display properly due to CORS issues. (Thanks ChatGpt for this solution because I didn't have the slightest idea on how to solve this problem.)

#### '/search'
This part makes a request to the API to search mangas according to the title provided by a form in the layout.html. Since the API has a limit of 100 results per request, fetching all results at once would slow down the app. To address this, a pagination function is implemented. Initially, only the first 5 results are displayed. If the user wants to see more results, they can load additional pages, each showing 5 more results. This process continues until the API returns no additional results for the given search.

Finally, it renders the search.html page