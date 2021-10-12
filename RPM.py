import gather_keys_oauth2 as Oauth2
import fitbit
import pandas as pd 
import datetime
import matplotlib.pyplot as plt

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

        return final_df
    
    def get_calories(self, s_date, e_date):
        return self.auth2_client.intraday_time_series('activities/calories', start_time=s_date, end_time = e_date, detail_level='1min')




if __name__ == "__main__":
    print("aboba")
    rpm = RPM()
    s = pd.datetime(year = 2021, month = 10, day = 8)
    e = pd.datetime.today().date() - datetime.timedelta(days=1)
    print(rpm.get_hrate(s, e))
    print(rpm.get_calories(e))
    print("hello")