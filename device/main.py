import network
from machine import RTC, I2C
from config import *
from lib.umqttsimple import MQTTClient
import ubinascii
import utime
import ntptime
from machine import Pin, unique_id, reset

CONFIG={}

def do_connect(ssid,pwd):
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, pwd)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

rtc = RTC()
i2c = I2C(scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))




mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode() #client id ?
client_id = mac
print('MAC :', mac)

client = MQTTClient(client_id,MQTT_HOST)


i2c_devices = i2c.scan()

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

while True :
    do_connect(WIFI_SSID, WIFI_PASSWORD)

    try :
        ntptime.settime() # set the rtc datetime from the remote server
    except OSError as e:
        pass
    try : 
        client.connect()
    except OSError as e:
        reset()
    
    if CONFIG.get('SI7021') is True :
        h,t, = sensor.relative_humidity, sensor.temperature, 
        h,t = sensor.relative_humidity, sensor.temperature,
        topic = '{}/temperature'.format(mac)
        client.publish(topic, str(t))
        topic = '{}/humidity'.format(mac)
        client.publish(topic, str(h))

    if CONFIG.get('BMP180') is True :
        p,t = bmp180.pressure, bmp180.temperature 
        topic = '{}/pressure'.format(mac)
        client.publish(topic, str(p))
        if CONFIG.get('SI7021') is not True : #publish temp only if no SI7021
            topic = '{}/temperature'.format(mac)
            client.publish(topic, str(t))

    if CONFIG.get('CMJCU-811') is True :
        #ccs811.put_envdata(humidity=h, temp=t) # s assurer que h et t sont relev?? avec le si7021
        if ccs811.data_ready():
            co2, voc = ccs811.eCO2, ccs811.tVOC
            topic = '{}/co2'.format(mac)
            client.publish(topic, str(co2))
            topic = '{}/cov'.format(mac)
            client.publish(topic, str(voc))
    
    if CONFIG.get('OLED') is True :
        display.fill(0)
        display.text('{}??C'.format(round(t,1)),20,0)
        display.text('{} %'.format(int(h)),20,15)
        display.text('{}:{}'.format(*rtc.datetime()[4:6]),20,50)
        display.show()

        

    utime.sleep(60)
