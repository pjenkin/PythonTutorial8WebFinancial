from flask import Flask, render_template

app = Flask(__name__)

# route for Bokeh embedded chart
@app.route('/plot/')
def plot():
    import pandas
    from pandas_datareader import data
    import fix_yahoo_finance as fyf
    import datetime
    from bokeh.plotting import figure, show, output_file
    from bokeh.models.annotations import Title
    from bokeh.embed import components
    from bokeh.resources import CDN

    # start = datetime.datetime(2016,1,1)
    # finish = datetime.datetime(2019,3,21)
    start = datetime.datetime(2016, 3, 1)  # Y M D
    finish = datetime.datetime(2016, 9, 10)

    # # Alternative API fix B: using fix_yahoo_finance package as Yahoo API scat
    # https://www.udemy.com/the-python-mega-course/learn/v4/questions/4201842
    fyf.pdr_override()

    # stock MSI - Motorola Solutions Inc
    dfYAHOO = data.DataReader(name='MSI', data_source='yahoo', start=start, end=finish)

    # formatting the chart (20-225)

    fig = figure(x_axis_type='datetime', width=1000, height=300,
                 sizing_mode='stretch_both')  # stretch/responsive in 20-226
    fig.title.text = 'Candlestick chart - financial'
    fig.grid.grid_line_alpha = 0.3

    # 20-224 add a column to the dataframe to show price increase/decrease

    def increase_decrease(close, open):
        if close > open:
            value = 'Increase'
        elif close < open:
            value = 'Decrease'
        else:
            value = 'Equal'
        return value

    dfYAHOO['Status'] = [increase_decrease(close, open) for close, open, in zip(dfYAHOO.Close, dfYAHOO.Open)]
    # what pattern is this??

    # 20-224 add a column to the dataframe to calculate value coordinate of middle of candlestick block (for rectangle y parameter)
    dfYAHOO['BlockMiddle'] = (dfYAHOO.Open + dfYAHOO.Close) / 2
    dfYAHOO['Height'] = abs(dfYAHOO.Close - dfYAHOO.Open)

    # fig.quad() - TODO: could use quadrants
    # NB - first in code is hind-most in graph

    # 20-225
    fig.segment(pandas.to_datetime(dfYAHOO.index), dfYAHOO.High, pandas.to_datetime(dfYAHOO.index), dfYAHOO.Low,
                color='black')
    # draw lines for daily price high and low (rectangle of width=0)
    # x,y (low), x,y (high), colour - NB index field is 'Date'
    # NB had to use pandas.to_datetime again

    # blocks: open/close, lines:low/high (trading)
    hours_12 = 12 * 60 * 60 * 1000  # d H m ms - 1 half day's worth of milliseconds - (not conditional on increase/decrease)

    # fig.rect(dfYAHOO.index, (dfYAHOO.Open + dfYAHOO.Close)/2, hours_12, abs(dfYAHOO.Open-dfYAHOO.Close))

    # NB had to convert to datetime from DateTimeIndex
    # x = pandas.to_datetime(dfYAHOO.index[dfYAHOO.Close > dfYAHOO.Open])   # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html
    x = pandas.to_datetime(dfYAHOO.index[
                               dfYAHOO.Status == 'Increase'])  # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html
    # y = (dfYAHOO.Open + dfYAHOO.Close)/2
    y = dfYAHOO.BlockMiddle[dfYAHOO.Status == 'Increase']
    width = hours_12
    # height = abs(dfYAHOO.Open - dfYAHOO.Close)
    height = dfYAHOO.Height[dfYAHOO.Status == 'Increase']
    # fill color GREEN if price went down through day
    fig.rect(x=x, y=y, width=width, height=height, fill_color='#CCFFFF', line_color='black')  # x,y,width, height
    # base of rect, middle of rect, width, height (whether open>close or vice versa) https://bokeh.pydata.org/en/latest/docs/reference/plotting.html#bokeh.plotting.figure.Figure.rect

    # x = pandas.to_datetime(dfYAHOO.index[dfYAHOO.Close < dfYAHOO.Open])   # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html
    x = pandas.to_datetime(dfYAHOO.index[
                               dfYAHOO.Status == 'Decrease'])  # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html
    # y = (dfYAHOO.Open + dfYAHOO.Close)/2
    y = dfYAHOO.BlockMiddle[dfYAHOO.Status == 'Decrease']
    width = hours_12
    # height = abs(dfYAHOO.Open - dfYAHOO.Close)
    height = dfYAHOO.Height[dfYAHOO.Status == 'Decrease']
    # fill color RED if price went down through day
    fig.rect(x=x, y=y, width=width, height=height, fill_color='#FF3333', line_color='black')  # x,y,width, height

    # TODO: remove commented lines in separate cell to show final code used

    output_file('Candlestick.html')  # NB not needed for embedding Bokeh into Flask
    show(fig)  # NB not needed for embedding Bokeh into Flask

    script1, div1 = components(fig)
    cdn_javascript = CDN.js_files[0]
    cdn_css = CDN.css_files[0]
    return render_template('plot.html', script1=script1, div1=div1, cdn_css=cdn_css, cdn_javascript=cdn_javascript)


@app.route('/')
def home():
    #return 'Website content to be put here'
    return render_template('home.html')
    # return render_template('layout.html')

@app.route('/about/')
def about():
    # return 'Website \'About\' content to be put here'
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug = True)

