This is a fairly easy Python program based on Selenium. It is meant to automate the download of bills from AziendaOnWeb, since the service doesn't have an API. I also included a Dockerfile to build an image that automatically runs the script periodically, using a Selenium Grid Chrome container.

Github: https://github.com/kodai2199/bill-downloader<br/>
Let me know if you have any issues!

## <div align="center">Getting started</div>
Simply clone the repository and install the requirements:
`pip install -r requirements.txt`
Then set the following environment variables:
- webdriverHost, pointing to the Selenium Grid Chrome instance, like `http://selenium_chrome:4444`
- username, used to login to AziendaOnWeb
- password, for the same login

Then run `main.py`. Note that the folder will be downloaded to the remote Selenium Grid instance!