# SongSpotting

Mad shouts to Cam Linke and the folks at Real Python for this awesome blog post: https://realpython.com/blog/python/flask-by-example-part-1-project-setup

### Setup
1. Download this repository

2. Navigate to the root directory of the project
```
cd songspotting
```

3. Create a Virtual Environment and activate it
```
virtualenv env
source env/bin/activate
```

4. Install the required libraries
```
pip install -r requirements.txt
```

5. Establish Local Settings

To set up our application with environment variables, we’re going to use `autoenv`. This program executes commands stored in a `.env` file every time we cd into a directory cotaning that `.env` file. In order to use it, we will need to install it globally. First, exit out of your virtual environment in the terminal, install `autoenv`, then and add a `.env` file:

```
deactivate
pip install autoenv
touch .env
```

Next, in your `.env` file, add the following (remember to insert the full path to the project folder and remove the square brackets):
```
source [full-path-to-songspotting-folder]/env/bin/activate
export DEBUG=True
export APP_SECRET_KEY='Insert Flask App Secret Key'
export SPOTIFY_CLIENT_ID='Insert Spotify Client Id'
export SPOTIFY_CLIENT_SECRET='Insert Spotify Client Secret'
```

Now run the following to update then refresh your `.bash_profile`:
```
echo "source `which activate.sh`" >> ~/.bash_profile
source ~/.bash_profile
```

Now, if you move up a directory and then cd back into it, the virtual environment will automatically be started and the environment variables are declared. Close the current terminal and start a new one to confirm that it works in a new session.

####Please Note: If the above set of instructions doesn't work, you may need to use `.bashrc` rather than `.bash_profile`


### Running the app
Run the following command to start the app
```
python app.py
```


### Things to remember 

1. Every push to master will deploy that version to the Heroku server. Deploys happen automatically: be sure that this branch  is always in a deployable state and any tests have passed before you push.

2. If you install a new library, remember to add it to the requirements file. For example:
```
pip install gunicorn
pip freeze > requirements.txt
```
