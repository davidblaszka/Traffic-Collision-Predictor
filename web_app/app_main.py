from flask import Flask, request, render_template
from pymongo import MongoClient
import pandas as pd
from find_recommendations import recommender


app = Flask(__name__)
PORT = 8080
# Connect to the database
client = MongoClient()
db = client.redpointer


def recommender_page_setup():
	'''Returns routes, grade_list, route_type, and users for recommender page'''
	routes = db.routes.find({})
	users = db.users.find({})
	with open('../data/grades.txt') as f:
		grade_data = f.read()
	grade_list = grade_data.replace('\n', '').replace(' ', '').split(',')
	# make list of route types
	route_type = ['Select', 'Aid', 'TR', 'Trad', 'Sport', 'Alpine']
	return routes, grade_list, route_type, users


@app.route('/')
def root():
	# find top routes in washington
	df = pd.DataFrame(list(db.routes.find()))
	df_sorted = df.sort_values('page_views', ascending=False).head(20)
	recs = df_sorted.sort_values('average_rating', ascending=False).head(6)
	return render_template('index.html', routes=recs)


@app.route('/returning-user', methods=['GET', 'POST'])
def getReturnRatings():
	routes, grade_list, route_type, users = recommender_page_setup()
	return render_template('recommender.html', 
							routes=routes, 
							grades=grade_list, 
							route_type=route_type,
							users=users)


@app.route('/new-user', methods=['GET', 'POST'])
def getNewRatings():
	routes, grade_list, route_type, users = recommender_page_setup()
	return render_template('recommender.html', 
							routes=routes, 
							grades=grade_list, 
							route_type=route_type,
							users=users)


@app.route('/my-recommendations', methods=['POST', 'GET'])
def getRecs():
	route_name = request.args.get('route-name')
	route_type = request.args.get('route-type')
	route_grade_gr = request.args.get('route-grade_gr')
	route_grade_ls = request.args.get('route-grade_ls')
	username = request.args.get('username')
	recs = recommender(username, route_name, route_grade_gr, 
								route_grade_ls, route_type)
	return render_template('my-recommendations.html', recs=recs)


if __name__ == '__main__':
	# Start Flask app
	app.run(host='0.0.0.0', port=PORT, threaded=True, debug=True)
