import numpy as np
import pandas
import statsmodels.api as sm
import matplotlib.pyplot as plt
import scipy
import scipy.stats as stats


def compute_r_squared(data, predictions):    
    m_y = np.mean(data)
    x_n = np.sum([pow(y-f,2) for (y,f) in zip(data, predictions)])
    x_d = np.sum([pow(y-m_y,2) for y in data])
    r_squared = 1 - x_n / x_d
    return r_squared

def linear_regression(features, values):
    """
    Perform linear regression given a data set with an arbitrary number of features.
    """
    features = sm.add_constant(features)
    model = sm.OLS(values, features)
    results = model.fit()
    params = results.params
    print results.tvalues
    #print results.t_test([1, 0, 1])
    intercept = params[0]
    params = params[1:]
  
    return intercept, params

    ################################ MODIFY THIS SECTION #####################################
    # Select features. You should modify this section to try different features!             #
    # We've selected rain, precipi, Hour, meantempi, and UNIT (as a dummy) to start you off. #
    # See this page for more info about dummy variables:                                     #
    # http://pandas.pydata.org/pandas-docs/stable/generated/pandas.get_dummies.html          #
    ##########################################################################################
turnstile_weather = pandas.read_csv('turnstile_weather_v2.csv')

# 0.48
#features = turnstile_weather[['rain', 'hour', 'meantempi', 'weekday', 'fog', 'wspdi', 'weather_lon']]
features = turnstile_weather[['wspdi']]


#dummy_units = pandas.get_dummies(turnstile_weather['UNIT'], prefix='unit')
#features = features.join(dummy_units)

#dummy_conds = pandas.get_dummies(turnstile_weather['conds'], prefix='conds')
#features = features.join(dummy_conds)

    
# Values
values = turnstile_weather['ENTRIESn_hourly']

# Perform linear regression
intercept, params = linear_regression(features, values)

predictions = intercept + np.dot(features, params)
r2 = compute_r_squared(turnstile_weather['ENTRIESn_hourly'],predictions)

print "r_squared: " + str(r2)

residuals = turnstile_weather['ENTRIESn_hourly'] - predictions
plt.figure()
plt.subplots_adjust(hspace=.4)

plt.subplot(311)
plt.hist(residuals, bins=30, range=[-15000, 15000])
plt.title(r'Residuals distribution ')
plt.xlabel('# of entries')

plt.subplot(312)
stats.probplot(residuals, dist="norm", plot=plt)

plt.subplot(313)
plt.scatter(values, residuals)



plt.show()



