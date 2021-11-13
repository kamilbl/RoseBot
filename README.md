# RoseBot

**A simple bot for trading on the Binance exchange.**

This version is based on trading with the RSI indicator.

The bot is based on Python 3.
1. Install python3 https://www.python.org/downloads/
2. Install the add-on package from the ```requirements.txt``` file ```pip3 install -r requirements.txt```
3. Create API Keys on Binance.com (remember to set up trading without withdrawals. It's worth setting only your IP)
4. Create a bot on Telegram. https://sendpulse.com/knowledge-base/chatbot/create-telegram-chatbot
5. Add the keys to the ```key.py``` file and save.
6. Enter the data for trading in the ```RoseBot_RSI.py``` file:
   - Line 32 -> Cryptocurrency symbol np "SHIBUSDT".
   - Line 43 -> What operation should BOT SELL or BUY trade start with? np. "BUY"
   - Line 44 -> Budget expressed in USDT, e.g. 50
   - Line 45 -> Cryptocurrency balance for sale, e.g. 342123.0
   - Line 70 -> Change only the value (75) ```float (df_Main.loc [0, "RSI"]) > 75``` This is the upper limit of the RSI indicator when the cryptocurrency is to be sold.
   - Line 75 -> Change only the value (25) ```elif float (df_Main.loc [0, "RSI"]) < 25``` This is the lower limit of the RSI indicator when the cryptocurrency is to be bought.
