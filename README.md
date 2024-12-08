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
This part serves as a proxy to get the images from the API because otherwise the images wouldn't display properly due to CORS issues. 
>Thanks ChatGpt for this solution because I didn't have the slightest idea on how to solve this problem.

#### '/search'
This part makes a request to the API to search mangas according to the title provided by a form in the layout.html. Since the API has a limit of 100 results per request, fetching all results at once would slow down the app. To address this, a pagination function is implemented. Initially, only the first 5 results are displayed. If the user wants to see more results, they can load additional pages, each showing 5 more results. This process continues until the API returns no additional results for the given search.

Finally, it renders the search.html page

#### '/forManga'
This route appears when you click on a manga on the '/search'. It makes a request with the manga_id to get the list of chapters. With this it creates a list of dictionaries with the existing volumes and inside this it creates another dictionary with the id, chapter, and title of each chapter that belongs to that volume. It also makes another request to get the title, description and cover image of the manga. This part also accepts pagination in case the chapters are more than 100. 

#### '/chapter/
This route basically gets every image for the chapter by making a request to the API with the base url + the chapter id. It then renders the chapter_reader.html

#### '/login'
This route takes the username and password recevied by a form in the login.html; it looks if this user exists on the database and if the hashed password matched the password recevied. If this operation succeed then it redirects the user to the home page; otherwise it displays an alert.

It also renders the login.html 

#### '/register'
This route takes a username, a password, and a confirmation to insert a new user in the database. If any of this data is missing or the password is not equal to the confirmation an alert is displayed. 

It also renders the register.html

#### '/logout'
Logs out the current user by clearing Flask's session. 

## mangaweb.db 
This is the database used for the app. It uses sqlite3. It has just 2 tables: 
- users
    - It stores the id, the username, and the hashed password
- saved_mangas
    - It stores the user_id and the manga_id for every saved manga 

## layout.html
This is the layout used for every other .html file on the app. It has the top bar that acts as a menu. Inside this top bar there is a checkbok at the top left of the page that when clicked it makes the vertical menu which has the library and return to home option as \<a> tags. 

The top bar also has at the right side a form that acts a search bar for looking for mangas. It takes the input and sends it via post to the '/search' route. At the right side of this form there is a user icon. When it is clicked it will show the user menu if the user is logged in; otherwise it will redirect the user to the '/login' route. 

Finally we have the user menu that shows an image, a username and a \<a> tag to logout. 
> The layout.html file uses the layout.js file to show the vertical menu and the user menu when the respective checkbox is clicked by the user. 

## search.html
This page shows in a grid the mangas found when user enter a title in the layout search form. For each manga it shows the cover image, the title and the description all of this inside a \<a> tag. When this tag is clicked the user is redirected to the '/forManga' route with the manga id and the cover fileName. This also has pagination in case there are more than 100 results and it only shows results in a groups of 5. 

## formanga.html 
It displays the cover image, the title, the description and a grid of the available volumes in a collapsed way with their respective chapters. For each chapter it shows the number of chapter and its title. When the user clicks on any chapter if redirects to the '/chapter' route. This also has pagination in case there are more than 100 chapters. 
> To expand the volumes and show their chapters it uses the forManga.js file.

It also has a form with a button that saves the manga by submitting the manga id to the '/save' route. 

## chapter_reader.html 
It shows one by one the images for the chapter for the user to read them. When the user clicks on the right side or the right arrow the next image is displayed and if the user clicks on the left side or the left arrow the previous image is displayed. 
> For this to work it uses the chapter_reade.js file. 

## home.html
It displays in a grid the last 5 mangas that have updated.
> This grid works exactly like the search.html grid  

## library.html 
It displays in a grid all the mangas saved by the user. 
> This grid works exactly like the search.html grid  

## register.html 
It displays a form with 3 inputs and 1 submit button. The inputs are the enterting the username, the password, and confirming the password. 

## login.html 
It displays a form with 2 inputs and 1 sumbit button. The inputs are for enering the username and the password. 

## layout.js
It checks for user inputs for opening and displaying the vertical menu and user menu when their respective checkbox or image is clicked. 

## forManga.js 
It expands or collapses the volumes to show or hide its chapters when clicked by the users by changing it height property.

## chapter_reader.js 
It makes sure to display only the active image. It also goes to the next image when user presses the right side or the right arrow key. For going to the previous image the user needs to click the left side or press the left key arrow. 

## CSS files 
I'm not going to explain each individual file. Each css file is link to the html file that has the same name. The only exceptions is the search.css which is shared by the search.html, the home.html, and the library.html. The css file for the layout.html is named style.css. 


## Thanks to 
### [Yacine](https://codepen.io/fromwireframes/pen/arMrYp)
For the idea and code for the checkbox icon for accessing the vertical menu. 

### [Iiyaxu123](https://uiverse.io/liyaxu123/warm-eel-62)
For the css for the search input for looking mangas. 

## Chatgpt 
For helping me solve bugs with my code and helping me with the javascript functionality 

> If you want to see the exact part where Yacine and Iiyaxu123 were given credit, it is mentioned in the comments inside the code.
