import pandas as pd

import warnings
warnings.filterwarnings('ignore')

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import matplotlib.pyplot as plt


def load_data(file_name):
    df = pd.read_csv(file_name)
    return df

def timestamp_translator(df, data_col_list = ['first_seen_at', 'last_seen_at', 'first_purchase_at', 'trial_start_at', 'trial_end_at', 
'most_recent_purchase_at', 'most_recent_renewal_at', 'latest_expiration_at', 'subscription_opt_out_at', 
'trial_opt_out_at', 'most_recent_billing_issues_at']):
    for data_col in data_col_list:
        df[data_col] = pd.to_datetime(df[data_col], unit='ms')
    return df


def lifetime_calculation(df):
    df = df.loc[df.status == 'cancelled']
    df['lifetime'] = df.total_renewals + 1
    lifetime = df.lifetime.mean()
    return lifetime

def print_lifetime_stat(df):
    df = df.loc[df.status == 'cancelled']
    df['lifetime'] = df.total_renewals + 1
    lifetime = df.lifetime.mean()
    product_type = str(df.all_purchased_product_ids.unique())
    period_type = product_type.split('.')[-1][0:-2]
    print(f'The average user lifetime for a {product_type} is {lifetime} {period_type}')
    return lifetime

def aov_calculation(df):
    df = df.fillna(0)
    df['average_cost'] = df.total_spent / (df.total_renewals + 1)
    return df


def ltv_calculation(df, lifetime_y, lifetime_w):
    df = aov_calculation(df)
    df['lifetime'] = 0
    df.loc[(df.all_purchased_product_ids == 'com.app.year'), 'lifetime'] = lifetime_y
    df.loc[(df.all_purchased_product_ids == 'com.app.week'), 'lifetime'] = lifetime_w
    df['ltv'] = df.average_cost * df.rpr * df.lifetime
    return df

def sampling_report(df):
    print('Total Data: ' + str(len(df)) + ' lines')
    df_y = df.loc[df.all_purchased_product_ids == 'com.app.year']
    df_w = df.loc[df.all_purchased_product_ids == 'com.app.week']
    percent_y = (len(df_y) * 100) / len(df)
    percent_w = (len(df_w) * 100) / len(df)
    print('Number of lines about the annual subscription: ' + str(len(df_y)) + ' lines (' + str(float('{:.2f}'.format(percent_y))) + '%)')
    print('Number of lines about the weekly subscription: ' + str(len(df_w)) + ' lines (' + str(float('{:.2f}'.format(percent_w))) + '%)')
    print()
    print("Completed user - a user who has already purchased a subscription a certain number of times and eventually canceled it \n(the user's lifetime is presumably already over)")
    print()
    df_trial = df.loc[df.status == 'free_trial']
    df_active = df.loc[df.status == 'active']
    df_cancelled = df.loc[df.status == 'cancelled']
    df_expired = df.loc[df.status == 'expired']
    df_cancelled_trial = df.loc[df.status == 'cancelled_trial']
    percent_cancelled = (len(df_cancelled) * 100) / len(df)
    percent_active = (len(df_active) * 100) / len(df)
    percent_trial = (len(df_trial) * 100) / len(df)
    percent_expired = (len(df_expired) * 100) / len(df)
    percent_cancelled_trial = (len(df_cancelled_trial) * 100) / len(df)
    print('Number of Completed users: ' + str(len(df_cancelled)) + ' (' + str(float('{:.2f}'.format(percent_cancelled))) + '%)')
    print('Number of active users: ' + str(len(df_active)) + ' (' + str(float('{:.2f}'.format(percent_active))) + '%)')
    print('Number of users who still have a free trial period: ' + str(len(df_trial)) + ' (' + str(float('{:.2f}'.format(percent_trial))) + '%)')
    print('Number of users who failed to issue a receipt: ' + str(len(df_expired)) + ' (' + str(float('{:.2f}'.format(percent_expired))) + '%)')
    print('Number of users who did not renew their subscription after the trial period: ' + str(len(df_cancelled_trial))
         + ' (' + str(float('{:.2f}'.format(percent_cancelled_trial))) + '%)')
    
    
def distribution_report(df, col_type):
    col_type_list = df[col_type].unique().tolist()
    
    #Check for None Type
    for l in col_type_list:
        try:
            l = float(l)
            col_type.remove(l)
        except:
            continue
            
    print(f'Number of {col_type}: {len(col_type_list)}')
    number_of_entries = {}
    for col in col_type_list:
        number_of_entries[col] = [len(df.loc[df[col_type] == col]), 
                                                 len(df.loc[(df[col_type] == col) & (df.status == 'cancelled')])]

    number_of_entries = dict(sorted(number_of_entries.items(), key=lambda x: x[1]))
    top = list(reversed(list(number_of_entries.keys())))
    top_10 = top[:10]
    
    print(f'\nTop 10 {col_type} by number of users: ')
    c = 1
    
    for col in top_10:
        value = number_of_entries.get(col)[0]
        numb_of_completed =  number_of_entries.get(col)[1]
        print(f'{c}. {col} - {value} users (and {numb_of_completed} of them are completed users)')
        c = c + 1
        number_of_entries.pop(col)
        
    number_of_entries_values_list = list(number_of_entries.values())
    number_of_entries_useres_numb_list = []
    for value in number_of_entries_values_list:
        number_of_entries_useres_numb_list.append(value[0])
    try:
        maximum = max(number_of_entries_useres_numb_list)
        minimum = min(number_of_entries_useres_numb_list)
        print(f'\nFor other {col_type} the number of users is from {minimum} to {maximum} people')
    except:
        print()
    return list(top)


def formation_of_array_of_top_countries(df, top_country):
    all_df_by_country = []
    for country in top_country:
        all_df_by_country.append(df.loc[df.ip_country == country])
    return all_df_by_country


def ltv_calculation_by_country(df, top_country):
    all_df_by_country = formation_of_array_of_top_countries(df, top_country)
    ltv_country_dictionary = {}
    for df_buf in all_df_by_country:
        df_buf_y = df_buf.loc[df_buf.all_purchased_product_ids == 'com.app.year']
        df_buf_w = df_buf.loc[df_buf.all_purchased_product_ids == 'com.app.week']
        df_aov_y, aov_y = aov_calculation(df_buf_y)
        df_aov_w, aov_w = aov_calculation(df_buf_w)
        rpr = 1
        lifetime_y = lifetime_calculation(df_buf_y)
        lifetime_w = lifetime_calculation(df_buf_w)
        ltv_y = ltv_calculation(aov_y, rpr, lifetime_y)
        ltv_w = ltv_calculation(aov_w, rpr, lifetime_w)
        country = df_buf.ip_country.unique()
        ltv_country_dictionary[str(country)] = ltv_y, ltv_w
    ltv_country_dictionary = dict(sorted((ltv_country_dictionary.items()), key=lambda x: x[1]))
    top_keys = reversed(ltv_country_dictionary.keys())
    for key in top_keys:
        value = ltv_country_dictionary.get(key)
        print(f'For users from {key} LTV is {value}')
    #for key, value in ltv_country_dictionary.items():
        #print(f'For users from {key} LTV is {value}')
    return ltv_country_dictionary

def plotting(metric, number_of_users, name, xaxis_name, yaxis_name):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
            go.Scatter(x=metric, y=number_of_users, marker_color="red"),
            secondary_y=False,
        )
    fig.update_layout(title=name,
                      xaxis_title=xaxis_name,
                      yaxis_title=yaxis_name)
    fig.show()

def plotting_for_html(metric, number_of_users, name, xaxis_name, yaxis_name):
    plt.subplots()
    plt.plot(metric, number_of_users)
    plt.title(name)
    plt.xlabel(xaxis_name)
    plt.ylabel(yaxis_name)
    plt.show()


    
def describe_ltv(df):
    df = df.groupby('ltv').describe()
    number_of_users = df['rpr']['count']
    ltv = df['rpr']['count'].index
    return df, ltv, number_of_users
    
    
def top_chart_vis(df, col_name, top):
    for col in top:
        df_buf = df.loc[df[col_name] == col]
        numb_of_zero = len(df_buf.loc[df_buf.ltv == 0])
        percent = (numb_of_zero * 100) / len(df_buf)
        df_buf = df.loc[(df[col_name] == col) & (df.ltv != 0)]
        name = str(col)
        df_describe, ltv, number_of_users = describe_ltv(df_buf)
        xaxis_name = 'ltv'
        yaxis_name = 'number of users'
        plotting(ltv, number_of_users, name, xaxis_name, yaxis_name)
        print(f'Numb of zero: {numb_of_zero} ({percent}%)')
        ltv_mean = sum(ltv) / len(ltv)
        ltv_min = min(ltv)
        ltv_max = max(ltv)
        print(f'LTV statistics: mean {ltv_mean}, min {ltv_min}, max {ltv_max}')
    
    
    
    
    