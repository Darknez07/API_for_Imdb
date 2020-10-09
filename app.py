from flask import Flask, g, jsonify, request
import sqlite3
import random
import string
import  subprocess

subprocess.run(['python','API_of_Imdb.py'])
from database import get_db, connect_db

cols=["Id",
     "Title",
     "Year",
     "Genre",
     "Rating",
     "Number_of_Raters",
     "Movie_Url",
     "Speciality",
     "Idea",
     "Raters Count",
     "Reccomandations"]
letters_count = 20
digits_count = 12

API = {}
def check_year(l,wanted,db):
    query = ""
    if '-' in l[1]:
        # Splitting to get the column to display
        wanted = l[1].split('-')
        if '%20' in wanted[0]:
            wanted[0] = " ".join(wanted[0].split("%20"))

        if '%20' in wanted[1]:
            wanted[1] = " ".join(wanted[1].split("%20"))
        if len(wanted) >=2 or wanted[1] == 'gt':
            if wanted[2] == 'gt':
                query = "select distinct * from movies where year > {}".format(wanted[0])
                print(query)
                result = db.execute(query)
                result = result.fetchall()
            elif wanted[1] == 'gt':
                query = "select distinct * from movies where year > {}".format(wanted[0])
                print(query)
                result = db.execute(query)
                result = result.fetchall()
                wanted = None
        else:
        # Getting out everything
            query = "select distinct * from movies where year={}".format(wanted[0])
            print(query)
            result = db.execute(query)
            result = result.fetchall()

    else:
        # If not query able do the regular regime
        if '%20' in l[1]:
            l[1] = " ".join(l[1].split('%20'))
        print("\"%"+l[1]+"%\"")
        query = "select distinct * from movies where year={}".format(l[1])
        print(query)
        result = db.execute(query)
        result = result.fetchall()
    return result, wanted

def find(result, wanted):
    arr = []
    for i in result:
        if wanted and wanted[1].lower() == cols[-1].lower():
            # If we want reccomandations
            arr = arr + i[wanted[1]].split(',')
        elif wanted and wanted[1].lower() in list(map(str.lower,cols)):
            # anything else wanted here
            arr.append({wanted[1]:i[wanted[1]],
                        "Title":i["Title"][:-1]})
        else:
            # only titles if simple query
            arr.append({"result":i["Title"]})
    return arr

def check(l,wanted,db,col):
    query = ""
    if '-' in l[1]:
        # Splitting to get the column to display
        wanted = l[1].split('-')
        if '%20' in wanted[0]:
            wanted[0] = " ".join(wanted[0].split("%20"))

        if '%20' in wanted[1]:
            wanted[1] = " ".join(wanted[1].split("%20"))
        # Getting out everything
        query = "select distinct * from movies where {} like {}".format(col,"\"%"+wanted[0]+"%\"")
        print(query)
        result = db.execute(query)
        result = result.fetchall()

    else:
        # If not query able do the regular regime
        if '%20' in l[1]:
            l[1] = " ".join(l[1].split('%20'))
            print("\"%"+l[1]+"%\"")
        query = "select distinct * from movies where {} like {}".format(col,"\"%"+l[1]+"%\"")
        print(query)
        result = db.execute(query)
        result = result.fetchall()
    return result, wanted
app = Flask(__name__)

@app.teardown_appcontext
def close_db(err):
    if hasattr(g,'sqlite3_db'):
        g.sqlite3_db.close()

@app.route("/token",methods=['GET'])
def get_api_token():

    sample_str = ''.join((random.choice(string.ascii_letters) for i in range(letters_count)))
    sample_str += ''.join((random.choice(string.digits) for i in range(digits_count)))

    # Convert string to list and shuffle it to mix letters and digits
    sample_list = list(sample_str)
    random.shuffle(sample_list)
    final_string = ''.join(sample_list)

    # API_TOKEN
    API["API_KEY] = final_string
    final_list = list(final_string)
    random.shuffle(final_list)

    #API_PASSWORD

    API["API_VALUE"] = ''.join(final_list)
    return jsonify([{"API_KEYPAIR":API,
                    "Message":"Use this API Key to GET data"}])

@app.route("/movies/",methods=['GET'])
def movie():
    wanted = None
    # Columns in the table
    # Decoding the incoming query string
    # finding the amount of queries
    string = request.query_string.decode('utf-8').split('?')
    # looping over the string
    try:
        if request.headers[API["API_KEY"]] == API["API_VALUE"]:
            for i in string:
                l = i.split('=')
                # defining each query:
                db = get_db()
                print(list(map(str.lower,cols[3:])))
                if len(l) == 2:
                    # Checking if l has enough elements
                    if l[0].lower() in cols[0]:
                        # getting everything if Id is present
                        result = db.execute('select * from movies where id=?',[l[1]])
                        result = result.fetchone()
                        # litreally returning every thing
                        return jsonify({"Id": result["Id"],
                                "Title": result["Title"],
                                "Year":result["Year"],
                                "Genre": result["Genre"],
                                "Rating": result["Rating"],
                                "Number_of_Raters": result["Raters Count"],
                                "Movie_Url":result["Movie_Url"],
                                "Achievements":result["Speciality"],
                                "The_Line":result["Idea"]})
                    # This is for query is about the title of the movie
                    elif l[0].lower() in cols[1].lower():
                        # within title offering a feature of returing certain outputs
                        result, wanted = check(l,wanted,db,cols[1].lower())
                        arr = find(result,wanted)
                        # What can wanted do
                        if wanted and wanted[1] == cols[-1]:
                            # Return reccomendations if requested
                            return jsonify({"Reccomends": list(set(arr))})
                        return jsonify(arr)
                    elif l[0].lower() in cols[2].lower():
                        result, wanted = check_year(l,wanted,db)
                    elif l[0].lower() in list(map(str.lower,cols[3:])):
                        result, wanted = check(l, wanted, db, l[0].lower())
                        arr = find(result,wanted)
                        print(wanted,arr)
                        return jsonify(arr)
        else:
            return jsonify({"message":"Get or Enter API token"}), 403
    except Exception:
        return jsonify({"message":"Get or Enter API token"}), 403

@app.route("/movies/<int:num>",methods=['GET'])
def movies(num):
    # API authentication
    # This gets the n random movies from database
    try:
        if request.headers[API["API_KEY"]] == API["API_VALUE"]:
            db =get_db()
            results = db.execute('select * from Movies order by random() limit ?',[num])
            results = results.fetchall()
            rows = []
            print(request.authorization)
            for result in results:
                rows.append({"Id": result["Id"],
                            "Title": result["Title"],
                            "Year":result["Year"],
                            "Genre": result["Genre"],
                            "Rating": result["Rating"],
                            "Number_of_Raters": result["Raters Count"],
                            "Movie_Url":result["Movie_Url"],
                            "Achievements":result["Speciality"],
                            "Reccomandations": result["Recommandations"],
                            "The_Line":result["Idea"]})
            return jsonify(rows)
        else:
            return jsonify({"message":"Get or Enter API token"}), 403
    except Exception:
        return jsonify({"message":"Get or Enter API token"}), 403

if __name__ == '__main__':
    app.run(debug=True)
