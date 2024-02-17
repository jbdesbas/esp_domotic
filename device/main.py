"""
V240217
"""
import network
from machine import RTC, I2C
import config
from lib.umqttsimple import MQTTClient
import ubinascii
import utime
import ntptime
from machine import Pin, unique_id, reset, WDT

CONFIG={}

RTC_SYNC_EVERY_MS = 60*60*1000 # Sync NTP every hour

def do_connect(ssid,pwd):
    import network
    ap = network.WLAN(network.AP_IF) # create access-point interface
    ap.active(False)  
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, pwd)
        while not sta_if.isconnected():
            safe_wdt_feed()
            utime.sleep_ms(250)
    print('network config:', sta_if.ifconfig())

if config.ENABLE_WDT :
    utime.sleep(config.TIME_SLEEP_BEFORE_WDT)
    print("/!\ Who let the watchdogs out ?")
    wdt=WDT()
else :
    print("/!\ WDT is disable. Please enable after debug")


def safe_wdt_feed():
    if config.ENABLE_WDT : 
        wdt.feed()

rtc = RTC()
i2c = I2C(scl=Pin(config.I2C_SCL_PIN), sda=Pin(config.I2C_SDA_PIN))

mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode() #client id ?
client_id = mac
print('MAC :', mac)

client = MQTTClient(client_id,config.MQTT_HOST, user = config.MQTT_USER, password = config.MQTT_PASSWORD)

i2c_devices = i2c.scan() # TODO config autoscan

print('i2c scan :', [hex(x) for x in i2c_devices])

if(0x3C in i2c_devices):
    print('Found display device (0x3C)')
    CONFIG['OLED']=True
    from ssd1306 import SSD1306_I2C
    display = SSD1306_I2C(128, 64, i2c)

if(0x40 in i2c_devices):
    print('Found si7021 device (0x40)')
    CONFIG['SI7021']=True
    from lib.si7021 import Si7021
    sensor = Si7021(i2c)

if(0x77 in i2c_devices):
    print('Found bmp180 device (0x77)')
    CONFIG['BMP180']=True
    from lib.bmp180 import BMP180
    bmp180 = BMP180(i2c)

if(0x5a in i2c_devices):
    print('Found CMJCU-811 (0x5a)')
    CONFIG['CMJCU-811']=True
    from lib.CCS811 import CCS811
    ccs811 = CCS811(i2c=i2c, addr=0x5a)

time_flag = 0
time_flag_rtc = 0

while True :
    safe_wdt_feed()
    if time_flag != 0 and utime.ticks_diff(utime.ticks_ms(), time_flag ) < 60*1000 :
        continue
    
    time_flag = utime.ticks_ms()
    do_connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    
    if time_flag_rtc == 0 or utime.ticks_diff(utime.ticks_ms(), time_flag_rtc ) > config.RTC_SYNC_EVERY_MS :
        try :
            ntptime.host=config.NTP_HOST
            ntptime.settime() # set the rtc datetime from the remote server
            time_flag_rtc = utime.ticks_ms()
            print('Sync time with {}'.format(ntptime.host))
        except OSError as e:
            pass
            
    try : 
        client.connect() # MQTT connect
        safe_wdt_feed()
    except OSError as e:
        reset()
    
    if CONFIG.get('SI7021') is True :
        h,t, = sensor.relative_humidity, sensor.temperature, 
        h,t = sensor.relative_humidity, sensor.temperature,
        topic = '{}/temperature'.format(mac)
        client.publish(topic, str(t))
        topic = '{}/humidity'.format(mac)
        client.publish(topic, str(h))
        safe_wdt_feed()

    if CONFIG.get('BMP180') is True :
        p,t = bmp180.pressure, bmp180.temperature 
        topic = '{}/pressure'.format(mac)
        client.publish(topic, str(p))
        if CONFIG.get('SI7021') is not True : #publish temp only if no SI7021
            topic = '{}/temperature'.format(mac)
            client.publish(topic, str(t))
        safe_wdt_feed()

    if CONFIG.get('CMJCU-811') is True :
        #ccs811.put_envdata(humidity=h, temp=t) # s assurer que h et t sont relevé avec le si7021
        if ccs811.data_ready():
            co2, voc = ccs811.eCO2, ccs811.tVOC
            topic = '{}/co2'.format(mac)
            client.publish(topic, str(co2))
            topic = '{}/cov'.format(mac)
            client.publish(topic, str(voc))
        safe_wdt_feed()
    
    if CONFIG.get('OLED') is True :
        display.fill(0)
        display.text('{}°C'.format(round(t,1)),20,0)
        display.text('{} %'.format(int(h)),20,15)
        display.text('{}:{}'.format(*rtc.datetime()[4:6]),20,50)
        display.show()
        safe_wdt_feed()
    
    safe_wdt_feed()
    utime.sleep_ms(250)


