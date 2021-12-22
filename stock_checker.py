import os
import pandas as pd
from bs4 import BeautifulSoup
import time
import requests
import time
import schedule
import requests
from dotenv import load_dotenv

load_dotenv()


def checkForStockCP(page):
  soup = BeautifulSoup(page.content,features="html.parser")
  items = soup.find("ul", {"class":"lineView"})

  items.findAll("div", {"class":"emproduct"})

  rows_processed = []
  for item in items.findAll("div", {"class":"emproduct"}):
    itemTittle = item.find("a", {"class":"emproduct_right_title"})
    itemUrl = item.find("a", {"class":"emproduct_right_title"})
    itemPromo = item.find("button", {"class":"cartIcon"})
    itemPrice = item.find("label", {"class":"price"})
    row = []
    row.append(itemTittle['title'])
    row.append(itemUrl['href'])
    row.append(itemPrice.text.strip())
    row.append(itemPromo != None)
    rows_processed.append(row)

  df = pd.DataFrame.from_records(rows_processed, columns=["Item_title", "Item_url", "Item_price", "Is_Available"])
  return df


def checkForStockDDTECH(page):
  soup = BeautifulSoup(page.content,features="html.parser")
  items = soup.find("section", {"class":"list-products"})

  items.findAll("div", {"class":"item-carousel"})

  rows_processed = []
  for item in items.findAll("div", {"class":"item-carousel"}):
    itemTittle = item.find("a")['title']
    itemUrl = item.find("a")['href']
    itemPromo = item.find("span", {"class":"label-icon"})
    itemPrice = item.find("span", {"class":"price"})
    row = []
    row.append(itemTittle)
    row.append(itemUrl)
    row.append(itemPrice.text.strip())
    row.append(itemPromo.text.strip() == "CON EXISTENCIA")
    rows_processed.append(row)

  df = pd.DataFrame.from_records(rows_processed, columns=["Item_title", "Item_url", "Item_price", "Is_Available"])
  return df


def searchFromCP(pages):
  products_with_stock = []
  for url in pages:
    page = requests.get(url)

    stock_df = checkForStockCP(page)
    if True in stock_df["Is_Available"].values:
      print("Stock Available on CYBERPUERTA!")
      for item in zip(stock_df.loc[stock_df['Is_Available'] == True, ['Item_title', 'Item_url', 'Item_price']].iterrows()):
        product_name = item[0][1].iloc[0] 
        product_url = item[0][1].iloc[1]
        product_price = item[0][1].iloc[2]
        products_with_stock.append({"name": product_name, "url": product_url, "price":product_price})
        print(f"{product_name} {product_price}")
    else:
      print("Everything out of stock on CYBERPUERTA!")
    time.sleep(5)
    return products_with_stock


def searchFromDDTECH(pages):
  products_with_stock = []
  for url in pages:
    page = requests.get(url)

    stock_df = checkForStockDDTECH(page)
    if True in stock_df["Is_Available"].values:
      print("Stock Available on DDTECH!")
      for item in zip(stock_df.loc[stock_df['Is_Available'] == True, ['Item_title', 'Item_url', 'Item_price']].iterrows()):
        product_name = item[0][1].iloc[0] 
        product_url = item[0][1].iloc[1]
        product_price = item[0][1].iloc[2]
        products_with_stock.append({"name": product_name, "url": product_url, "price":product_price})
        print(f"{product_name} {product_price}")
    else:
      print("Everything out of stock on DDTECH!")
    time.sleep(5)
    return products_with_stock

def telegram_bot_sendMessgae(message):
  bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
  bot_chatId = os.getenv("TELEGRAM_BOT_CHATID")
  request = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatId + '&parse_mode=Markdown&text=' + message

  response = requests.get(request)

  return response.json()


def main():
    print("Main line start")
    products = []
    DDTECH_RTX_3070 = 'https://ddtech.mx/productos/componentes/tarjetas-de-video?geforce-rtx-serie-30[]=rtx-3070&orden=primero-existencia&precio=1:99999'
    DDTECH_RTX_3060 = 'https://ddtech.mx/productos/componentes/tarjetas-de-video?geforce-rtx-serie-30[]=rtx-3060&orden=primero-existencia&precio=1:99999'
    STOCK_DDTECH_URLS=[DDTECH_RTX_3070, DDTECH_RTX_3060]
    
    CP_RTX_3070 = "https://www.cyberpuerta.mx/Computo-Hardware/Componentes/Tarjetas-de-Video/Filtro/Procesador-grafico/NVIDIA-GeForce-RTX-3070/"
    CP_RTX_3060 = "https://www.cyberpuerta.mx/Computo-Hardware/Componentes/Tarjetas-de-Video/Filtro/Procesador-grafico/NVIDIA-GeForce-RTX-3060-Ti/"
    STOCK_CP_URLS=[CP_RTX_3070, CP_RTX_3060]
    products = products + searchFromDDTECH(STOCK_DDTECH_URLS)
    products = products + searchFromCP(STOCK_CP_URLS)

    for product in products:
      messageToSend = f'{product["name"]}\n\n{product["price"]}\n\n{product["url"]}'
      telegram_bot_sendMessgae(messageToSend)
    print("Main line end")

schedule.every(1).minutes.do(main)

while True:
  schedule.run_pending()
  time.sleep(1)

    