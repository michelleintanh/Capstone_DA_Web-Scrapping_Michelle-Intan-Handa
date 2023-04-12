from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table', attrs = {'class':'history-rates-data'})
row = table.find_all('span', attrs={'class':'n'})

row_length = len(row)

temp = [] #initiating a list 

for i in range(0, row_length):
	#get currency data
    USD_to_IDR = table.find_all ('span', attrs={'class':'n'})[i].text
    
    #get period
    Date = table.find_all ('a', attrs={'class':'n'})[i].text
    
    #put the currency and period into the empty tuple
    temp.append((Date, USD_to_IDR))

temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns = ('Date','USD_to_IDR'))

#insert data wrangling here
df['USD_to_IDR'] = df['USD_to_IDR'].str.replace ('$',"")
df['USD_to_IDR'] = df['USD_to_IDR'].str.replace ('=', '')
df['USD_to_IDR'] = df['USD_to_IDR'].str.replace ('Rp', '')
df['USD_to_IDR'] = df['USD_to_IDR'].str.replace("1", "", 1)
df['Date'] = df['Date'].astype('datetime64')
df['USD_to_IDR'] = df['USD_to_IDR'].str.replace(",",".")
df['USD_to_IDR'] = df['USD_to_IDR'].astype('float64')
df = df.set_index('Date')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["USD_to_IDR"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)