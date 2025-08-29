FROM python:3.10.slim

# RUN apt-get update && apt-get install -y \
#     wget \
#     curl \
#     gnupg \
#     unzip \
#     jq \
#     fonts-liberation \
#     libnss3 \
#     libxss1 \
#     libasound2 \
#     libatk1.0-0 \
#     libatk-bridge2.0-0 \
#     libcups2 \
#     libxrandr2 \
#     libgbm1 \
#     libgtk-3-0 \
#     libappindicator3-1 \
#     libvulkan1 \
#     xdg-utils \
#     ca-certificates \
#     --no-install-recommends && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# RUN wget https://storage.googleapis.com/chrome-for-testing-public/123.0.6312.86/linux64/chrome-linux64.zip && \
#     unzip chrome-linux64.zip && \
#     mv chrome-linux64 /opt/chrome && \
#     ln -sf /opt/chrome/chrome /usr/bin/google-chrome && \
#     rm chrome-linux64.zip

# RUN wget -O /tmp/chromedriver.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/123.0.6312.86/linux64/chromedriver-linux64.zip && \
#     unzip /tmp/chromedriver.zip -d /tmp/ && \
#     mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
#     chmod +x /usr/local/bin/chromedriver && \
#     rm -rf /tmp/chromedriver*


# RUN mkdir -p /app/webdriver && \
#     ln -s /usr/local/bin/chromedriver /app/webdriver/chromedriver


# RUN google-chrome --version && chromedriver --version


# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python3","server.py"]

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
