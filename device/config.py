import secret

WIFI_SSID = secret.WIFI_SSID
WIFI_PASSWORD = secret.WIFI_PASSWORD

MQTT_HOST = secret.MQTT_HOST
MQTT_USER = secret.MQTT_USER
MQTT_PASSWORD = secret.MQTT_PASSWORD

I2C_SCL_PIN = 5
I2C_SDA_PIN = 4

TIME_SLEEP_BEFORE_WDT = 10
ENABLE_WDT = True # Disable for debug only

AUTOSCAN_I2C = True # TODO Not implemented

RTC_SYNC_EVERY_MS = 60*60*1000 # Sync NTP every hour
NTP_HOST = "1.europe.pool.ntp.org"
