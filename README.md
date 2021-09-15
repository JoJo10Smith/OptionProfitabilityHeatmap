# OptionProfitabilityHeatmap
Creating Heatmaps of Option Profitabilty on an Expecteed Value Basis

Finance derivatives (specifically options) derive their value from the current value of their underlying. Options have both extrinsic and intrinsic value before expiration, the intrisic value is based on the believe that the underlying could increase/ decrease in value. Below is an example of a heatmap that was created using the program. In this readme I will explain all calculations and how I derive the option value to project the expecteed returns.

![Image of heatmap](https://github.com/JoJo10Smith/OptionProfitabilityHeatmap/blob/main/Images/heatmap.JPG)

1) The first step was to collect historical data for the underlying. The underlying that is used in this example is the Invesco QQQ Trust Series 1 (QQQ) options. This Historical data can be found on multiple websites for free. [Yahoo Finance Historical Data for QQQ](https://finance.yahoo.com/quote/QQQ/history?p=QQQ) After I had all the data I needed to calculate the returns over a range of days. For example if I wanted the 1 day return I would calculate the return based on the opening price on day 1 to the closing price on day 1. If I wanted the 2 daya return I based that on the opening price on day 1 to the closing price on day 2 and so forth. Attached in the "QQQ_return_data.csv" is the average and standard deviation of returns from 1 - 90 days.

2) Once I had the mean and the standard deviations of returnes based on the number of days between the opening and closing price I could use those to calcualte the probability of achieving a desired return using a cumulative distribution function. I had data from the last 5 years which ws sufficent for me to assume that the distribution of returns was normal under the [Central Limit Theorem](https://en.wikipedia.org/wiki/Central_limit_theorem) I used this to calculate the probabilty of the underlying reaching a cenrtain price level based on the current price. Essentially I used historical data to come up with a level of expectation of achiveing a given return.

3) The [TD Ameritrade Options Chain API](https://developer.tdameritrade.com/option-chains/apis/get/marketdata/chains) can be used to collect the current price of options for any underlying stock which has options available. I used this API to get the current premium of options which would be used to calculate my profits. My profit equation is below

![Profit equation](https://github.com/JoJo10Smith/OptionProfitabilityHeatmap/blob/main/Images/profit.JPG)

If the current strike price is below the expected underlying price then option expires out-of-the-money and the profit is just the negative of the premium since that is your maximum loss. If the strike price is above the expected underlying price then the prifit is calcualted to be the difference between the strike price and the underlying price, thwn I subtracted the option premium.

4) I finally the multipled the profit op an option at a certain price level with the probability that the underlying would get to that price level based on previuos returns over a defined period. This allowed me to create heatmaps of live data that I could update at anytime of the day. This allowed me to choose the best option to maximize my returns based on my expectations of the underlying and its movements within a range of time that I could also defined. I would either maximimze along the y-axixs (option strikes) or the x-axis (underlying price)

![Second Example Image](https://github.com/JoJo10Smith/OptionProfitabilityHeatmap/blob/main/Images/Second%20picture.JPG)

If you have any questions or suggestions please reach me at: jsmith58@bryant.edu
