import scipy.stats
import plotly.express as px
import plotly.graph_objects as go
import requests
import pandas 
import time

API_KEY = "***INSERT TD AMERITRADE API KEY HERE***"

UNDERLYING = "QQQ"
YEAR = "2021"
MONTH = "10"
DAY = "01" 
DAYS_TO_EXP = "0"

OPTION_START,OPTION_END = 345,365
UNDERLYING_START,UNDERLYING_END = 342,378

#fill in all the dates that you would like to collect and should apply to all options
API_DATE_INPUT = "{}-{}-{}:{}".format(YEAR,MONTH,DAY,DAYS_TO_EXP)

def collect_option_data(symbol,strike,contractType="CALL"):
    #Collect all relevant information about an option that will be analyzed
    try:
      parameters = {"apikey":API_KEY,
                   "includeQuotes":True,
                   "strike":str(strike),
                   "symbol":symbol,
                   "contractType":contractType}
          
      url = "https://api.tdameritrade.com/v1/marketdata/chains"
      response = requests.get(url,params=parameters).json()
      pointer = response['{}ExpDateMap'.format(contractType.lower())][API_DATE_INPUT][str(parameters['strike'])][0]
      
      return pointer["ask"]
    except:
      #the option does not trade
      return -1

def collect_underlying_data(symbol):
  try:
      parameters = {"apikey":API_KEY}
          
      url = "https://api.tdameritrade.com/v1/marketdata/{}/quotes".format(symbol)
      response = requests.get(url,params=parameters).json()
      return response[symbol]["askPrice"]
  except:
    print ("Unable to collect underlying price: {}".format(symbol))
    return -1


UNDERLYING_PRICE = collect_underlying_data(UNDERLYING)
    
def create_option_strikes(starting_strike,ending_strike,step=1):
  #create the desired list of strike prices for the option heatmap
  list_of_strikes = []
  for current_strike in range(starting_strike,ending_strike+step,step):
    list_of_strikes.append(current_strike)
  return list_of_strikes

def create_underlying_prices(starting_price,ending_price,step=1):
  #create the desired list of prices for the heatmap
  list_of_prices = []
  for current_price in range(starting_price,ending_price+step,step):
    list_of_prices.append(current_price)
    list_of_prices.append(current_price+0.2)
    list_of_prices.append(current_price+0.4)
    list_of_prices.append(current_price+0.6)
    list_of_prices.append(current_price+0.8)
  return list_of_prices

PROFITABILITY = {}

OPTION_STRIKES = create_option_strikes(OPTION_START,OPTION_END)
UNDERLYING_PRICES = create_underlying_prices(UNDERLYING_START,UNDERLYING_END)

#COLLECT CALL OPTION PREMIUMS
OPTION_PREMIUM_CALLS = {}
for current_option_strike in OPTION_STRIKES:
  option_price = collect_option_data(UNDERLYING,float(current_option_strike),"CALL")
  OPTION_PREMIUM_CALLS[current_option_strike] = option_price
  print ("Call Option Premium for ${} strike --> ${}".format(float(current_option_strike),option_price))
  time.sleep(0.3)

print ("\n=============================================\n")
#COLLECT PUT OPTION PREMIUMS
OPTION_PREMIUM_PUTS = {}
for current_option_strike in OPTION_STRIKES:
  option_price = collect_option_data(UNDERLYING,float(current_option_strike),"PUT")
  OPTION_PREMIUM_PUTS[current_option_strike] = option_price
  print ("Put Option Premium for ${} strike --> ${}".format(float(current_option_strike),option_price))
  time.sleep(0.3)

#read the data from prepared file
file_data = [line.split(",") for line in open("QQQ_return_data.csv")]
file_data = file_data[1:]

RETURN_DATA = {}
for current_line in file_data:
  days_to_exp = str(current_line[0])
  mean_return = float(current_line[1])
  standard_dev = float(current_line[2])
  RETURN_DATA[days_to_exp] = {"mean":mean_return,"standard_dev":standard_dev}

def _required_return_(original_price,target_price):
  #calculates the return you would need to reach your target
  difference = target_price - original_price
  return float(difference/original_price)

def calculate_probability(current_live_price,underlying_calc_price,contractType="CALL"):
  #calculates probablity of achiveing desired return based on pas performance
  data = RETURN_DATA[DAYS_TO_EXP]
  distribution = scipy.stats.norm(data["mean"],data["standard_dev"])
  required_return = _required_return_(current_live_price,underlying_calc_price)
  if contractType == "CALL":
    return  1 - distribution.cdf(required_return)
  else:
    return distribution.cdf(required_return)

call_data,put_data = {},{}
for current_option_strike in OPTION_STRIKES:
    call_option_profits,put_option_profits = [],[]

    for current_underlying_price in UNDERLYING_PRICES:
        if current_option_strike > current_underlying_price:
            current_call_profit = -OPTION_PREMIUM_CALLS[current_option_strike]
            current_put_profit = current_option_strike - current_underlying_price - OPTION_PREMIUM_PUTS[current_option_strike]
        elif current_option_strike < current_underlying_price:
            current_call_profit = current_underlying_price - current_option_strike - OPTION_PREMIUM_CALLS[current_option_strike]
            current_put_profit = -OPTION_PREMIUM_PUTS[current_option_strike]
        else:
          #deal with at the money situation meaning there is a loss on both the call and put options
          current_call_profit = -OPTION_PREMIUM_CALLS[current_option_strike]
          current_put_profit = -OPTION_PREMIUM_PUTS[current_option_strike]

        call_profit_percent = 100 * float(current_call_profit/OPTION_PREMIUM_CALLS[current_option_strike])
        put_profit_percent = 100 * float(current_put_profit/OPTION_PREMIUM_PUTS[current_option_strike])
        #profit_percent = max(min(500,profit_percent),-100)
        call_profit_percent *= calculate_probability(UNDERLYING_PRICE,current_underlying_price,"CALL")
        put_profit_percent *= calculate_probability(UNDERLYING_PRICE,current_underlying_price,"PUT")

        call_option_profits.append(min(150,call_profit_percent))
        put_option_profits.append(min(150,put_profit_percent))
    #make sure the contract is being traded
    if OPTION_PREMIUM_CALLS[current_option_strike] != -1:
      call_data[current_option_strike] = call_option_profits
    if OPTION_PREMIUM_PUTS[current_option_strike] != -1:
      put_data[current_option_strike] = put_option_profits

CALL_GRAPH_DATA = pandas.DataFrame.from_dict(call_data,orient = "index",columns = UNDERLYING_PRICES)
PUT_GRAPH_DATA = pandas.DataFrame.from_dict(put_data,orient = "index",columns = UNDERLYING_PRICES)

call_fig = px.imshow(CALL_GRAPH_DATA,color_continuous_scale="RdYlGn",title="Expected value of Call Option returns for {}".format(UNDERLYING))
put_fig = px.imshow(PUT_GRAPH_DATA,color_continuous_scale="RdYlGn",title="Expected value of Put Option returns for {}".format(UNDERLYING))

call_fig.update_layout(title_x=0.5)
put_fig.update_layout(title_x=0.5)

call_fig.update_xaxes(title_text='Underlying Price')
call_fig.update_yaxes(title_text='Option Strike Price')
put_fig.update_xaxes(title_text='Underlying Price')
put_fig.update_yaxes(title_text='Option Strike Price')

def add_profitabilty_lines(given_data,underlying_prices,contractType="CALL"):
  x,y=[],[]
  if contractType.lower() == "call":
    for current_strike in given_data:
      current_index = 0
      for current_profit in given_data[current_strike]:
        if current_profit > 0:
          y.append(current_strike-0.2)
          y.append(current_strike+0.2)
          x.append(underlying_prices[current_index]-0.2)
          x.append(underlying_prices[current_index]-0.2)
          break 
        else:
          current_index += 1
  else:
    for current_strike in given_data:
      current_index = 0
      for current_profit in given_data[current_strike]:
        if current_profit < 0:
          y.append(current_strike-0.2)
          y.append(current_strike+0.2)
          x.append(underlying_prices[current_index]-0.2)
          x.append(underlying_prices[current_index]-0.2)
          break 
        else:
          current_index += 1

  return [x,y]

call_line_data = add_profitabilty_lines(call_data,UNDERLYING_PRICES,"CALL")
put_line_data = add_profitabilty_lines(put_data,UNDERLYING_PRICES,"PUT")

#add profitability lines to both charts
call_fig.add_trace(
    go.Scatter(
        x=call_line_data[0],
        y=call_line_data[1],
        mode="lines",
        line=go.scatter.Line(color="gray"),
        showlegend=False))

put_fig.add_trace(
    go.Scatter(
        x=put_line_data[0],
        y=put_line_data[1],
        mode="lines",
        line=go.scatter.Line(color="gray"),
        showlegend=False))

#add the current price to both charts
call_fig.add_trace(
    go.Scatter(
        x=[UNDERLYING_PRICE,UNDERLYING_PRICE],
        y=[OPTION_START-0.5,OPTION_END+0.5],
        mode="lines",
        line=go.scatter.Line(color="blue"),
        showlegend=False))

put_fig.add_trace(
    go.Scatter(
        x=[UNDERLYING_PRICE,UNDERLYING_PRICE],
        y=[OPTION_START-0.5,OPTION_END+0.5],
        mode="lines",
        line=go.scatter.Line(color="blue"),
        showlegend=False))

call_fig.show()
put_fig.show()
