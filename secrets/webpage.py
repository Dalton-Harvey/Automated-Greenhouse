import umail
import network
import socket
from time import sleep
from machine import Pin

sender = 'rosshardybot@gmail.com'
password = 'dujr vrcg zabq cqys'

SSID = 'hardy1'
PASSWORD = 'hardyrje'

def send_email(subject, body, recipients, sender=sender, password=password):
    smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True)
    
    try:
        smtp.login(sender, password)
        smtp.to(recipients)
        smtp.write(f'From:{sender}\n')
        smtp.write(f'Subject:{subject}\n')
        smtp.write(body)
        smtp.send()
    except Exception as e:
        print('Failed to send email:', e)
    finally:
        smtp.quit()
        print('Successfully sent email')


def get_page(ip):
    return f"""
<!DOCTYPE html>
<html>
    <head/>
    <body>
        <h1>Hello world!</h1>
        <button onclick="buttonPress()">send email</a>
    </body>
</html>
<script>
function buttonPress() {{
    var request = new XMLHttpRequest();
    request.open("GET", "http://{ip}/email", false);
    request.send(null);
}}
</script>
"""

led = Pin('LED', Pin.OUT)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    print('Connecting')
    
    while not wlan.isconnected():
        led.toggle()
        sleep(0.5)
    
    led.on()
    
    print('Connected')
    
    ip = wlan.ifconfig()[0]
    
    print(f'Address: {ip}')
    return ip

def start_server():
    ip = connect_wifi()
    addr = socket.getaddrinfo(ip, 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen()
    print(f'Server running on http://{ip}:80')
    
    while True:
        cl, c_addr = s.accept()
        print(f'Client connected from {c_addr}')
        request = cl.recv(1024).decode('utf-8')
        print(f'Request: {request}')
        
        if 'GET /email' in request:
            send_email('Email from Pi Pico', 'Hello world!', 'hardyrje@gmail.com')
        
        response = get_page(ip)
        
        cl.send('HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()

start_server()