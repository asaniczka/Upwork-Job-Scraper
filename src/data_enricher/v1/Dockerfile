# CREDITS
# https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/743#issuecomment-1420119272

FROM ultrafunk/undetected-chromedriver:3.20-chrome-lateinstall

RUN DEBIAN_FRONTEND=noninteractive 
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub > /usr/share/keyrings/chrome.pub 
RUN echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/chrome.pub] http://dl.google.com/linux/chrome/deb/ stable main' > /etc/apt/sources.list.d/google-chrome.list
RUN apt update -y 
RUN apt install -y google-chrome-stable

RUN apt install xvfb -y 
RUN export DISPLAY=:1 
RUN Xvfb $DISPLAY -screen $DISPLAY 1280x1024x16 &

WORKDIR /app
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

CMD [ "python3","./src/orchestrator/scheduled_run.py" ]