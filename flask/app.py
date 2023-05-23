
import json
import os
import tempfile
from flask import Flask, render_template, request, send_file, send_from_directory, session, flash
from flask_session import Session

import base64
from io import BytesIO
from matplotlib.figure import Figure
import numpy as np
from matplotlib import use
import matplotlib.pyplot as plt
from scipy.stats import norm
#TODO: the squad offset might be wrong. large squads could end up gaining rating despite losing!! TODO test.

# import requi9red module
import sys

# append the path of the
# parent directory
import logging
sys.path.append("..")
#from trueskill import Rating, rate, TrueSkill
from src.trueskillplus import Rating_plus, Trueskillplus
logging.basicConfig(level=logging.INFO)

# import method from sibling
# module

# TODO: Refactor with new data structure
# TODO: Finish swap, swapall and remove functions

use('agg')  # MATPLOTLIB IS NOT THREAD SAFE.

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'
app.config["SESSION_TYPE"] = "filesystem" 
app.config['UPLOAD_FOLDER'] = f'{os.getcwd()}/files'
Session(app)


@app.route('/', methods=['GET','POST'])
def index():

    
    session.update({
        'teams': {
            'Team 1': {},
            'Team 2': {}
        },
        'env':{
            'mu' : 25,
            'sigma' : round(25/3,4),
            'beta' : round(25/6,4),
            'tau' : round(25/300,4),
            'draw_probability' : 0.1,
            'stat_coefficient' : 0,
            'experience_coefficients' : {
                1:0,
                2:0,
                3:0,
                4:0,
                5:0
            },
            'squad_coefficients' : {
                1:0,
                2:0,
                3:0,
                4:0,
                5:0
            }

        },
        'data': {
            'played_matches_count' : 0

        }
        

    })
    session.pop('img', '')

    # print(session['teams'])
    return render_template('main.html')


@app.route('/main', methods=['GET','POST'])
def index_main():
    
    print("\nCurrent session: \n", dict(session.items()))
    return render_template('main.html')


@app.route('/add_player', methods=['POST'])
def add_player():
    #print(request.form)
    if request.form['action'] == 'add':

        s = dict(session['teams'].items())
        
        team = request.form['team']
        
        playerName = str(request.form['playerName'])


        s[team][playerName] = {'mu': '', 'sigma': '', 'stats': '', 'pred_stats': '', 'experience': '', 'squad': ''}
        
        s[team][playerName]['mu'] = float(request.form['mu'])
        s[team][playerName]['sigma'] = float(request.form['sigma'])
        s[team][playerName]['stats'] = float(request.form['stats'])
        s[team][playerName]['pred_stats'] = float(request.form['pred_stats'])
        s[team][playerName]['experience'] = int(request.form['experience'])

        if 'squad' in request.form:
            s[team][playerName]['squad'] = 'on'
        else:
            s[team][playerName]['squad'] = 'off'

    elif request.form['action'] == 'load':
        try:
            s = dict(session['teams'].items())
            file = request.files['file']
            team = request.form['team']
            playerName = file.filename.removesuffix('.json')
            playerdata = json.loads(file.stream.read())

            s[team][playerName] = {'mu': '', 'sigma': '', 'stats': '', 'pred_stats': '', 'experience': '', 'squad': ''}
            s[team][playerName]['mu'] = float(playerdata['mu'])
            s[team][playerName]['sigma'] = float(playerdata['sigma'])
            s[team][playerName]['stats'] = float(playerdata['stats'])
            s[team][playerName]['pred_stats'] = float(playerdata['pred_stats'])
            s[team][playerName]['experience'] = int(playerdata['experience'])
        except:
            flash("Error reading this file", category="error")
    
    return render_template('main.html')




@app.route('/update_player', methods=['POST'])
def update_player():
    
    
    if request.form['action'] == 'remove':

        s = dict(session['teams'])
        team = request.form['team']
        playerName = request.form['playerName']
        s[team].pop(playerName, '')

        
    elif request.form['action'] == 'update':
        #print(request.form)
        s = dict(session['teams'].items())
        
        team = request.form['team']
    
        playerName = request.form['playerName']
        
        s[team][playerName]['stats'] = request.form['stats']
        s[team][playerName]['pred_stats'] = request.form['pred_stats']
        s[team][playerName]['experience'] = request.form['experience']

        if 'squad' in request.form:
            s[team][playerName]['squad'] = 'on'
        else:
            s[team][playerName]['squad'] = 'off'
        
        flash('Player updated successfully', category='info')

    elif request.form['action'] == 'move_down':
        s = dict(session['teams'].items())
        
        team = request.form['team']
        print(s)
        playerName = request.form['playerName']

        temp = list(s)
        try:
            res = temp[temp.index(team) + 1]
            s[res][playerName] = s[team].pop(playerName)
        except (ValueError, IndexError):
            flash("Cannot move this player down!", category='warning')
        
    elif request.form['action'] == 'save':
        s = dict(session['teams'].items())
        
        team = request.form['team']
     
        playerName = request.form['playerName']

        data = dict(s[team][playerName])
        print(data)
    
   
        with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=f'{os.getcwd()}/files') as temp_file:
            # Write the dictionary data to the temporary file
            json.dump(data, temp_file)

            # Send the temporary file to the user for download
            print(temp_file.name)
            temp_file.seek(0)
            return send_file(path_or_file=temp_file.name, as_attachment=True, download_name=f'{ playerName.replace(" ", "_") }.json')
        
    elif request.form['action'] == 'move_up':
        s = dict(session['teams'].items())
        
        team = request.form['team']
        print(s)
        playerName = request.form['playerName']

        temp = list(s)
        try:
            res = temp[temp.index(team) -1]
            s[res][playerName] = s[team].pop(playerName)
        except (ValueError, IndexError):
            flash("Cannot move this player up!", category='warning')
        
        

        print(s)
       

        
    
    return render_template('main.html')




@app.route('/add_team', methods=['POST'])
def add_team():

    session['teams'][request.form['teamName']] = {}

    return render_template('main.html')


@app.route('/remove_team', methods=['POST'])
def remove_team():

    session['teams'].pop(request.form['team'])

    return render_template('main.html')

@app.route('/quality', methods=['POST'])
def quality():

    if 'env' in session:
        s = session['env']
        #TODO add mu and sigma
        env = Trueskillplus(mu=float(s['mu']),
                            sigma=float(s['sigma']),
                            beta=float(s['beta']), 
                            tau=float(s['tau']), 
                            draw_probability=float(s['draw_probability']), 
                            experience_coeffs=dict(s['experience_coefficients']), 
                            squad_coeffs=dict(s['squad_coefficients']),
                            stat_coeff=float(s['stat_coefficient']))
    else:
        env = Trueskillplus()

    s = dict(session['teams'].items())
   
    ratings = []
    stats = []
    expected_stats = []
    squads=[]
    for teamName, teamMembers in s.items():
        player_rating = []
        player_stat = []
        player_expected_stat = []
        squad_count = 0
        for member, rating in teamMembers.items():

            player_rating.append(
                Rating_plus(mu=float(rating['mu']), sigma=float(rating['sigma']), experience=float(rating['experience'])))
            
            player_stat.append(float(s[teamName][member]['stats']))
            player_expected_stat.append(float(s[teamName][member]['pred_stats']))
            if s[teamName][member]['squad'] == 'on':
                squad_count+=1

        ratings.append(tuple(player_rating))
        stats.append(tuple(player_stat))
        expected_stats.append(tuple(player_expected_stat))
        squads.append(squad_count)
    try:
        quality = env.quality(rating_groups=ratings)
        flash(message=f'This match has a {round(quality * 100,1)}% draw probability.')
        if quality > 0.5:
            flash('This is a great pairing!')
        if quality < 0.2:
            flash('This match is unfair.', category="warning")
    except Exception as e:
        flash("Error calculating quality!", category='error')
        flash(str(e), category='error')

    return render_template('main.html')
    
@app.route('/calculate', methods=['POST'])
def calculate():
    print(request.form)
    print(session)
    
    if 'env' in session:
        s = session['env']
        #TODO add mu and sigma
        env = Trueskillplus(mu=float(s['mu']),
                            sigma=float(s['sigma']),
                            beta=float(s['beta']), 
                            tau=float(s['tau']), 
                            draw_probability=float(s['draw_probability']), 
                            experience_coeffs=dict(s['experience_coefficients']), 
                            squad_coeffs=dict(s['squad_coefficients']),
                            stat_coeff=float(s['stat_coefficient']))
    else:
        env = Trueskillplus()
    print(env)
    s = dict(session['teams'].items())

    ratings = []
    stats = []
    expected_stats = []
    squads=[]
    for teamName, teamMembers in s.items():
        player_rating = []
        player_stat = []
        player_expected_stat = []
        squad_count = 0
        for member, rating in teamMembers.items():

            player_rating.append(
                Rating_plus(mu=float(rating['mu']), sigma=float(rating['sigma']), experience=float(rating['experience'])))
            
            player_stat.append(float(s[teamName][member]['stats']))
            player_expected_stat.append(float(s[teamName][member]['pred_stats']))
            if s[teamName][member]['squad'] == 'on':
                squad_count+=1

        ratings.append(tuple(player_rating))
        stats.append(tuple(player_stat))
        expected_stats.append(tuple(player_expected_stat))
        squads.append(squad_count)

    print("Rating the following:\n", ratings)
    
    
    
    try:
        if env.quality(rating_groups=ratings) < 0.2:
 
            flash(f'This match did not seem to be too fair...',category='info')

        
        rated = env.rate(rating_groups=ratings, 
                     ranks=[int(x) for x in request.form['ranks'].split(',')], 
                     stats=stats, 
                     expected_stats=expected_stats, 
                     squads=squads )
        
    except Exception as e:
        flash("Error determining ratings!", category='error')
        flash(str(e), category='error')
       
        return render_template('main.html')

    

    rated_flat = [item for sublist in rated for item in sublist]  # flatten

    # dict items are ordered since python 3.6!
    
    i = 0
    for teams, teamMembers in s.items():
        for member, rating in teamMembers.items():

            rating['mu'] = round(rated_flat[i].mu,4)
            rating['sigma'] = round(rated_flat[i].sigma,4)
            i += 1

    
    # make figure
    # MAY BE UNSAFE
    plt.clf()
    labels = []
    x_axis = np.arange(0, float(session['env']['mu']) * 2, 0.01)
    for teamName, teamMember in s.items():
        for teamMember, values in teamMember.items():
            # TODO invent some clever colors here
            plt.plot(x_axis, 100 * norm.pdf(
                x_axis, values['mu'], values['sigma']), scalex=1.5, animated=True)
            labels.append(teamMember)

    plt.legend(labels)
    plt.xlabel('Rating')
    plt.ylabel('Probability of rating %')
    # Save it to a temporary buffer.
    buf = BytesIO()
    plt.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    session['img'] = data

    plt.clf()
    session['data']['played_matches_count']+=1
    played_matches_count = session['data']['played_matches_count']
    """
    session['data'][played_matches_count] = [x.mu for x in rated_flat] 
    x_axis = np.arange(0, played_matches_count, 1)
    
    for i in range(played_matches_count):
        print(session['data'][played_matches_count])
        plt.plot(x_axis, session['data'][played_matches_count])

    plt.legend(labels)
    buf = BytesIO()
    plt.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    session['img2'] = data
    """
    return render_template('main.html')




@app.route('/manage', methods=['GET','POST'])
def manage():
    logging.info(request.form)
    if request.method == 'POST':
        
            
        session['env'] = {}
        session['env']['mu'] = request.form['mu']
        session['env']['sigma'] = request.form['sigma']
        session['env']['beta'] = request.form['beta']
        session['env']['tau'] = request.form['tau']
        session['env']['draw_probability'] = request.form['draw_probability']
        session['env']['stat_coefficient'] = request.form['stat_coefficient']
        session['env']['squad_coefficients'] = {}
        session['env']['experience_coefficients'] = {}
        for i in range(5):
            session['env']['squad_coefficients'][i+1] = request.form[f'squad_coefficient_{i+1}']
            session['env']['experience_coefficients'][i+1] = request.form[f'experience_{i+1}']
        
        print(session)
        flash('The Trueskill-plus settings were updated', category='info')
        return render_template('main.html')
    elif request.method == 'GET':
        
        return render_template('manage.html')
    
@app.route('/graph', methods=['GET'])
def graph():
    return render_template('graph.html')

@app.route('/help', methods=['GET'])
def help():
    return render_template('help.html')

if __name__ == '__main__':
    app.run()


"""
session:
{
    "teams" : {
        "team1" : {
            "playerName" : 
                {
                "sigma" : "",
                "mu" : "",
                "stat" : "",
                "pred"
                "experience" : "",
                
                etc.
            },

        },

        "team2" : {},
        etc.
    },
    "env" : {
        "mu" : 25,
        ...
    }

}
"""
