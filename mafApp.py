import requests
import json
from bs4 import BeautifulSoup
import math

print("Welcome!")
ticket = input("Enter Symbol Ticket for your first Stock! ")


def become_an_investor(stock_symbols):

    while True:
        portfolio = stock_symbols.upper()
        print("Awesome! Your Portfolio: " + portfolio)

        # using API WorldTradingData to pull current prices and number of shares for each security:

        key_api = 'xxxxxxx'
        #  8k0Gv31NhPZLr4wHesQtcJSAVS1L4FmOfk7jQNb8QXjzHQChE7wvnlM4Qq7y

        url_base_api = 'https://api.worldtradingdata.com/api/v1/stock'
        query = '?symbol='
        try:
            trading_data = url_base_api + query + portfolio + '&api_token=' + key_api
            my_request = requests.get(trading_data)
            my_json = my_request.json()
            # Uncomment if you want to see all the info for each security:
            # print(my_json['data'])

            # to_find_current_prices:

            g_number = 1             # "Graham Number" to be calculated using the formula invented by Benjamin Graham to
            # find fundamental value that investor should max pay for the stock (very conservative valuation approach).

            price = {}               # dictionary to accumulate all financial information for the stock
            numbers_list = []        # list to collect all data for each stock
            for item in my_json['data']:
                numbers_list.append(float(item['price']))       # adding current price of the stock
                numbers_list.append(float(item['shares']))      # adding number of shares
                price.setdefault(item['symbol'], numbers_list)  # adding the list to the dictionary
                g_number = 1/(float(item['shares']))            # adding calculated items to the formula

            # to_find_shareholders_equity:

            equity = {}
            for item in my_json['data']:
                balance_sheet = requests.get(
                    'https://money.cnn.com/quote/financials/financials.html?symb=' + item['symbol'] + '&dataSet=BS')

                balance_sheet.raise_for_status()             # getting equity data from the Balance Sheet tables online
                soup_bs = BeautifulSoup(balance_sheet.content, 'html.parser')

                # to get total shareholder equity:
                equity_list = soup_bs.select('div .totalRow')[9].findAll('td', class_='periodData')[3].contents

                # converting data to a float number
                try:
                    if str(equity_list[0]).endswith("M"):
                        equity_list_string = str(equity_list[0]).replace("M", "")
                        equity_number = float(equity_list_string)
                        equity_number = equity_number * 1000000
                    elif str(equity_list[0]).endswith("B"):
                        equity_list_string = str(equity_list[0]).replace("B", "")
                        equity_number = float(equity_list_string)
                        equity_number = equity_number * 1000000000
                    else:
                        equity_number = float(equity_list)

                    numbers_list.append(equity_number)  # adding new item to the list
                    g_number = g_number*equity_number  # adding calculated items to the formula

                    equity.setdefault(item['symbol'], numbers_list) # updating the dictionary with new data
                    price.update(equity)
                except:
                    print("Seems no data for SHE found...:(")
                continue

            #  Using web scraping to look up main financial statements

            # to_find_earnings_per_share():
            eps = {}
            for item in my_json['data']:
                income_statement = requests.get('https://money.cnn.com/quote/financials/financials.html?symb=' +
                                                item['symbol'] + '&dataSet=IS')

                income_statement.raise_for_status()
                #print(income_statement.status_code)
                soup_is = BeautifulSoup(income_statement.text, "html.parser")

                # to find Earnings per Share (EPS)using Income Statement reports online
                earnings_list = soup_is.select('div .periodData')[71].contents

                # converting data to a float number
                try:
                    e_list_string = str(earnings_list[0]).replace("$", "")
                    if e_list_string.endswith("M"):
                        e_string = str(e_list_string[0]).replace("M", "")
                        e_number = float(e_string)
                        e_number = e_number * 1000000
                    elif e_list_string.endswith("B"):
                        e_string = str(e_list_string[0]).replace("B", "")
                        e_number = float(e_string)
                        e_number = e_number * 1000000000
                    else:
                        e_number = float(e_list_string)

                    numbers_list.append(e_number)   # updating the list and the dictionary
                    eps.setdefault(item['symbol'], numbers_list)
                    price.update(eps)

                    g_number = g_number*e_number    # accumulating the number value
                    g_number = math.sqrt(22.5*g_number)    # final formula for Graham Number
                except:
                    print("Seems no data for EPS found...:(")
                continue
            # Printing final report

            for item in my_json['data']:
                print(item['name'] + ": Current Price, number of shares, Shareholders' Equity and Earnings per Share:")
                print(price)
                print("'Graham Number' to compare the Current Price of the stock.")
                print(str(g_number) + " vs " + str(item['price']))
                if g_number <= float(item['price']):
                    print("Stock is overvalued :/")
                else:
                    print("Stock is undervalued! :)")
                print("Data might be inaccurate due to the possible distortion of the source data. This information "
                      "is only for information purpose. Please use other valuation approaches! Thank you!")
        except:
            print("Please input correct Ticket Symbols ;)")
        finally:
            reply = input("Do you want to analyse another stock? (y/n)")
            if reply == "y":
                print("Enter Symbol Ticket for your Stock ")
                new_ticket = input()
                become_an_investor(new_ticket)
            if reply == "n":
                print("Thanks bye!")
            break


become_an_investor(ticket)

