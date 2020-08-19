# mayer-fields

This program retrieves historical and current prices of cryptocurrencies from Coinbase then generates Simple Moving Average (SMA) values for a set of day ranges (e.g. SMA200, SMA50). The values are then uploaded to a Google Sheet where conditional formatting is used to color the values in order to give an impression of how "hot" or "cold" the current price is in relation to a given SMA day range.

Coinbase libraries: https://developers.coinbase.com/docs/wallet/client-libraries

Google Sheets APIs: https://developers.google.com/sheets/api

Gspread: https://gspread.readthedocs.io/en/latest/

TODO: add information about how to install, configure, and use the mentioned libraries.

Note: need to add the Google service account as a shared Editor on workbooks