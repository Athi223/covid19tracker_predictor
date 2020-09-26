from flask import Flask, render_template, jsonify, request
from time import mktime
from datetime import datetime, timedelta
import requests
import prediction

data = {
	'modified': ['', ''],
	'confirmed': [],
	'active': [],
	'deceased': [],
	'recovered': [],
	'tested': 0,
	'states': [[], [], [], [], []],
	'districts': {}
}
predict = [ None ]*4
annual_dates = []
annual_prediction = [ [], [], [], [] ]

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def main(path):
	return render_template('index.html')

@app.route('/prediction', methods=['POST'])
def predictor():
	pred = [0]*4
	for i in range(4):
		pred[i] = predict[i].predictor(mktime(datetime.strptime(request.json['date'][:10], "%Y-%m-%d").timetuple()))
	return jsonify(pred)

@app.route('/api')
def get_data():
	get_api()
	return jsonify({ 'data': data, 'annual_dates': annual_dates, 'annual_prediction': annual_prediction })

def get_api():
	# API Call
	r = requests.head('https://api.covid19india.org/data.json')
	if r.headers['Last-Modified'] != data['modified'][0]:
		reset(True)
		response = requests.get('https://api.covid19india.org/data.json')
		data['modified'][0] = r.headers['Last-Modified']
		for day in response.json()['cases_time_series']:
			confirmed = int(day['totalconfirmed'])
			deceased = int(day['totaldeceased'])
			recovered = int(day['totalrecovered'])
			active = confirmed - deceased - recovered
			data['confirmed'].append({ 'date': day['date'], 'confirmed': confirmed })
			data['active'].append({ 'date': day['date'], 'active': active })
			data['deceased'].append({ 'date': day['date'], 'deceased': deceased })
			data['recovered'].append({ 'date': day['date'], 'recovered': recovered })
		data['tested'] = response.json()['tested'][-1]['totalsamplestested']
		# Prediction Training
		predict[0] = prediction.Confirmed(
			list(map(lambda x: mktime(datetime.strptime(x['date']+'2020', "%d %B %Y").timetuple()), data['confirmed'])),
			list(map(lambda x: x['confirmed'], data['confirmed']))
		)
		predict[1] = prediction.Active(
			list(map(lambda x: mktime(datetime.strptime(x['date']+'2020', "%d %B %Y").timetuple()), data['active'])),
			list(map(lambda x: x['active'], data['active']))
		)
		predict[2] = prediction.Deceased(
			list(map(lambda x: mktime(datetime.strptime(x['date']+'2020', "%d %B %Y").timetuple()), data['deceased'])),
			list(map(lambda x: x['deceased'], data['deceased']))
		)
		predict[3] = prediction.Recovered(
			list(map(lambda x: mktime(datetime.strptime(x['date']+'2020', "%d %B %Y").timetuple()), data['recovered'])),
			list(map(lambda x: x['recovered'], data['recovered']))
		)
		# Annual Prediction Logic
		current = datetime.today().strftime("%Y-%m-%d")
		for _ in range(12):
			temp = (datetime.strptime(current, "%Y-%m-%d").replace(day=1) + timedelta(days=31)).replace(day=1)
			current = temp.strftime("%Y-%m-%d")
			annual_dates.append(current)
			for i in range(4):
				annual_prediction[i].append(predict[i].predictor(mktime(temp.timetuple())))
		
	# API Call
	r = requests.head('https://api.covid19india.org/v4/data.json')
	if r.headers['Last-Modified'] != data['modified'][1]:
		reset(False)
		response = requests.get('https://api.covid19india.org/v4/data.json')
		data['modified'][1] = r.headers['Last-Modified']
		for stateid in response.json():
			total = response.json()[stateid]['total']
			types = ('confirmed', 'active', 'deceased', 'recovered', 'tested')
			current = (
				total[types[0]] or 0,
				(total[types[0]] or 0) - (total['deceased'] if 'deceased' in total else 0) - (total[types[3]] or 0) - (total['other'] if 'other' in total else 0),
				total['deceased'] if 'deceased' in total else 0,
				total[types[3]] or 0,
				total[types[4]] or 0
			)
			if stateid != 'TT':
				data['districts'][stateid] = response.json()[stateid]['districts']
				for i in range(5):
					data['states'][i].append({ 'state': stateid, types[i]: current[i] })

def reset(choice):
	if choice:
		data['confirmed'].clear()
		data['active'].clear()
		data['deceased'].clear()
		data['recovered'].clear()
	else:
		for i in range(5):
			data['states'][i].clear()
		data['districts'].clear()


if __name__ == "__main__":
	app.run(debug=True)