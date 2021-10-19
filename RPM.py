import gather_keys_oauth2 as Oauth2
import fitbit
import pandas as pd 
import datetime
import matplotlib.pyplot as plt
import json
import numpy as np

CLIENT_ID='23BKW8'
CLIENT_SECRET='bf2cc5685c5012279cfa9753228c0d7c'

'''

final_df.tail()
filename = 'all_intradata'
final_df.to_csv(filename + '.csv', index = False)

'''

class RPM(object):
    def __init__(self):
            server=Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
            server.browser_authorize()
            ACCESS_TOKEN=str(server.fitbit.client.session.token['access_token'])
            REFRESH_TOKEN=str(server.fitbit.client.session.token['refresh_token'])
            self.auth2_client=fitbit.Fitbit(CLIENT_ID,CLIENT_SECRET,oauth2=True,access_token=ACCESS_TOKEN,refresh_token=REFRESH_TOKEN)
    
    ## Returns heart rate per second as a dataframe
    def get_hrate(self, s_date, e_date):

        date_list = []
        df_list = []
        allDates = pd.date_range(start=s_date, end = e_date)

        for oneDate in allDates:
            oneDate = oneDate.date().strftime("%Y-%m-%d")
            oneDayData = self.auth2_client.intraday_time_series('activities/heart', base_date=oneDate, detail_level='1sec')
            df = pd.DataFrame(oneDayData['activities-heart-intraday']['dataset'])
            date_list.append(oneDate)
            df_list.append(df)
            
        final_df_list = []

        for date, df in zip(date_list, df_list):
            if len(df) == 0:
                continue
            df.loc[:, 'date'] = pd.to_datetime(date)
            final_df_list.append(df)

        final_df = pd.concat(final_df_list, axis = 0)

        ## Optional Making of the data have more detailed timestamp (day and hour instead of day)
        hoursDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.hour.apply(lambda x: datetime.timedelta(hours = x))
        minutesDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.minute.apply(lambda x: datetime.timedelta(minutes = x))
        secondsDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.second.apply(lambda x: datetime.timedelta(seconds = x))

        # Getting the date to also have the time of the day
        final_df['date'] = final_df['date'] + hoursDelta + minutesDelta + secondsDelta

        return final_df.drop(columns=['time'])
    

    ## returns spent calories per minute
    def get_calories(self, s_date, e_date):

        date_list = []
        df_list = []
        allDates = pd.date_range(start=s_date, end = e_date)

        for oneDate in allDates:
            oneDate = oneDate.date().strftime("%Y-%m-%d")
            oneDayData = self.auth2_client.intraday_time_series('activities/calories', base_date=oneDate, detail_level='1min')
            df = pd.DataFrame(oneDayData['activities-calories-intraday']['dataset'])
            date_list.append(oneDate)
            df_list.append(df)

        final_df_list = []

        for date, df in zip(date_list, df_list):
            if len(df) == 0:
                continue
            df.loc[:, 'date'] = pd.to_datetime(date)
            final_df_list.append(df)

        final_df = pd.concat(final_df_list, axis = 0)

        hoursDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.hour.apply(lambda x: datetime.timedelta(hours = x))
        minutesDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.minute.apply(lambda x: datetime.timedelta(minutes = x))
        secondsDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.second.apply(lambda x: datetime.timedelta(seconds = x))

        final_df['date'] = final_df['date'] + hoursDelta + minutesDelta + secondsDelta
        return final_df.drop(columns=['time', 'mets', 'level'])

    ## returns steps per minute
    def get_steps(self, s_date, e_date):
        date_list = []
        df_list = []
        allDates = pd.date_range(start=s_date, end = e_date)

        for oneDate in allDates:
            oneDate = oneDate.date().strftime("%Y-%m-%d")
            oneDayData = self.auth2_client.intraday_time_series('activities/steps', base_date=oneDate, detail_level='1min')
            df = pd.DataFrame(oneDayData['activities-steps-intraday']['dataset'])
            date_list.append(oneDate)
            df_list.append(df)

        final_df_list = []

        for date, df in zip(date_list, df_list):
            if len(df) == 0:
                continue
            df.loc[:, 'date'] = pd.to_datetime(date)
            final_df_list.append(df)

        final_df = pd.concat(final_df_list, axis = 0)

        hoursDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.hour.apply(lambda x: datetime.timedelta(hours = x))
        minutesDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.minute.apply(lambda x: datetime.timedelta(minutes = x))
        secondsDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.second.apply(lambda x: datetime.timedelta(seconds = x))

        final_df['date'] = final_df['date'] + hoursDelta + minutesDelta + secondsDelta
        return final_df.drop(columns=['time'])
    
    ## Returns tuple of dataframes, first containing data about time spent in different sleep modes (rem, awake, light...)
    ## As a second dataframe it returns sleepmode at exact minute
    def get_sleep(self, s_date, e_date):

        allDates = pd.date_range(start=s_date, end = e_date)
        date_list = []
        df_list = []
        stages_df_list = []

        allDates = pd.date_range(start=s_date, end = e_date)

        for oneDate in allDates:
            
            oneDate = oneDate.date().strftime("%Y-%m-%d")
            
            oneDayData = self.auth2_client.sleep(date=oneDate)
            
            # get number of minutes for each stage of sleep and such. 
            #stages_df = pd.DataFrame(oneDayData['summary'])
            #The above didn't work.
            oneDayData = json.loads(json.dumps(oneDayData))
            stages_df = pd.json_normalize(oneDayData['summary'])

            #This "if" handles the case, if there is no sleepdata (sleepdata is empty)
            if (not oneDayData['sleep']):
                nodata = {'dateTime':[np.nan], 'value':[np.nan], 'date':[oneDate] }
                df = pd.DataFrame(nodata)
            else:
                df = pd.DataFrame(oneDayData['sleep'][0]['minuteData'])

            date_list.append(oneDate)
            df_list.append(df)
            stages_df_list.append(stages_df)
            
        final_df_list = []

        final_stages_df_list = []

        for date, df, stages_df in zip(date_list, df_list, stages_df_list):

            if len(df) == 0:
                continue
            
            df.loc[:, 'date'] = pd.to_datetime(date)
            
            stages_df.loc[:, 'date'] = pd.to_datetime(date)
            
            final_df_list.append(df)
            final_stages_df_list.append(stages_df)

        final_df = pd.concat(final_df_list, axis = 0)

        final_stages_df = pd.concat(final_stages_df_list, axis = 0)
        columns = final_stages_df.columns[~final_stages_df.columns.isin(['date'])].values
        pd.concat([final_stages_df[columns] + 2, final_stages_df[['date']]], axis = 1)
        return (final_df, final_stages_df)
    
    ## Returns activity level per minute.
    ## Level field reflects calculated activity level for that time period ( 0 - sedentary; 1 - lightly active; 2 - fairly active; 3 - very active.)
    def get_activity(self, s_date, e_date):
        date_list = []
        df_list = []
        allDates = pd.date_range(start=s_date, end = e_date)

        for oneDate in allDates:
            oneDate = oneDate.date().strftime("%Y-%m-%d")
            oneDayData = self.auth2_client.intraday_time_series('activities/calories', base_date=oneDate, detail_level='1min')
            df = pd.DataFrame(oneDayData['activities-calories-intraday']['dataset'])
            date_list.append(oneDate)
            df_list.append(df)

        final_df_list = []

        for date, df in zip(date_list, df_list):
            if len(df) == 0:
                continue
            df.loc[:, 'date'] = pd.to_datetime(date)
            final_df_list.append(df)

        final_df = pd.concat(final_df_list, axis = 0)
        hoursDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.hour.apply(lambda x: datetime.timedelta(hours = x))
        minutesDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.minute.apply(lambda x: datetime.timedelta(minutes = x))
        secondsDelta = pd.to_datetime(final_df.loc[:, 'time']).dt.second.apply(lambda x: datetime.timedelta(seconds = x))

        final_df['date'] = final_df['date'] + hoursDelta + minutesDelta + secondsDelta
        return final_df.drop(columns=['time', 'mets', 'value'])
'''
    Other stuff that can be pulled with intraday-time-series:
    activities/calories
    activities/steps
    activities/distance
    activities/floors
    activities/elevation


    Instead of using that precise intraday-time-series we can extract data using
    the "normal" time-series method, which gives us this less time-dense data:

    activities/calories
    activities/caloriesBMR
    activities/steps
    activities/distance
    activities/floors
    activities/elevation
    activities/minutesSedentary
    activities/minutesLightlyActive
    activities/minutesFairlyActive
    activities/minutesVeryActive
    activities/activityCalories

    Especially these "minutes Lightly / Fairly / Very - active" looks interesting,
    but FitBit does notexplain anywhere what is considered E.g. "very active", 

    https://dev.fitbit.com/build/reference/web-api/activity/#activity-types
'''


if __name__ == "__main__":
    rpm = RPM()

    # Get data betveen dates "s" and "e"
    s = pd.datetime(year = 2021, month = 10, day = 11)
    e = pd.datetime.today().date() - datetime.timedelta(days=1)

    #steps = rpm.get_steps(s, e)
    #print(rpm.get_hrate(s, e))
    #print(rpm.get_calories(s, e))
    #sleepdata = rpm.get_sleep(s, e)
    #print(sleepdata[0])
    #print(sleepdata[1])

    activity = rpm.get_activity(s,e)
    # A way of exporting dataframe to csv file:
    filename = 'activity_data'
    activity.to_csv(filename + '.csv', index = False)
    
