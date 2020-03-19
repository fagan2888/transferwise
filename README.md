# transferwise
automate to create and compare quotes periodically to get the best rate.
Website: transferwise.com

# How-To
- Open an account at transferwise.com
- Obtain the token and input the token into the transferwise_api.py bearer token.
- Execute the `run.py` every */5 minutes in the crontab.

# Concept
the script will create the quote every time the script is executed. The quote rate will be compared with that stored under record.txt, if the earlier is higher, the new quote will be added and the old quote is cancelled. Lastly, the script will check if there are expired quotes and cancel them since they will not be gauranteed rate any more.

*This script helps you monitor and the get the best rates, it is recommended to send the summary data in `run.py` to your Email or Social Media to inform you if a better rate is obtained.*
 
# Precautions
Transferwise only allow the storing of quotes up to 3 days (depends on currency), this script will compare the expiration date time with the current date time and decides to generate a new quote if the old quote expires.
