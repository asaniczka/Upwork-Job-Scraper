# Make it portable

FROM ultrafunk/undetected-chromedriver

# RUN apt update && apt upgrade -y
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb

WORKDIR /usr/src


COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .