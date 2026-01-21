import socket
from time import time,sleep
import asyncio
from collections.abc import Iterable

import socket
import re
import sys


import logging

_LOGGER = logging.getLogger(__name__)

def match_volume(data):
    """方法A：直接匹配 volume 后的数字"""
    volume_regex = r'volume["\s:]*(\d{1,3})'
    match = re.search(volume_regex, data)
    
    if match:
        return int(match.group(1))
    
    """方法B：查找独立字段的 volume（在 JSON 外的）
       假设独立 volume 字段在前，格式为 "volume"+控制字符+数字"""
    standalone_volume_regex = r'volume[\x00-\x1F](\d{1,3})'
    standalone_match = re.search(standalone_volume_regex, data)
    
    if standalone_match:
        return int(standalone_match.group(1))
    
    return None

def match_power_state(data):
    """匹配 power_state 后的单个数字"""
    power_state_regex = r'power_state["\s:]*(\d)'
    match = re.search(power_state_regex, data)
    
    if match:
        return int(match.group(1))
    
    return None




class Projector:
    # client = socket.socket()

    
    

    commands = {
        "power": [b"\x09\x12\x07\x0a\x05\x08\xc3\x05\x10\x01", b"\x09\x12\x07\x0a\x05\x08\xc3\x05\x10\x00"],
        "mongo": [b"\x09\x12\x07\x0a\x05\x08\xc2\x05\x10\x01", b"\x09\x12\x07\x0a\x05\x08\xc2\x05\x10\x00"],
        "return": [b"\x08\x12\x06\x0a\x04\x08\x04\x10\x01", b"\x08\x12\x06\x0a\x04\x08\x04\x10\x00"],
        "setting": [b"\x09\x12\x07\x0a\x05\x08\xdd\x04\x10\x01", b"\x09\x12\x07\x0a\x05\x08\xdd\x04\x10\x00"],
        "ok": [b"\x08\x12\x06\x0a\x04\x08\x17\x10\x01", b"\x08\x12\x06\x0a\x04\x08\x17\x10\x00"],
        "up": [b"\x08\x12\x06\x0a\x04\x08\x13\x10\x01", b"\x08\x12\x06\x0a\x04\x08\x13\x10\x00"],
        "down": [b"\x08\x12\x06\x0a\x04\x08\x14\x10\x01", b"\x08\x12\x06\x0a\x04\x08\x14\x10\x00"],
        "left": [b"\x08\x12\x06\x0a\x04\x08\x15\x10\x01", b"\x08\x12\x06\x0a\x04\x08\x15\x10\x00"],
        "right": [b"\x08\x12\x06\x0a\x04\x08\x16\x10\x01", b"\x08\x12\x06\x0a\x04\x08\x16\x10\x00"],
        "option": [b"\x08\x12\x06\x0a\x04\x08\x52\x10\x01", b"\x08\x12\x06\x0a\x04\x08\x52\x10\x00"],
        "volume_min": [b"\x31\x12\x2f\x22\x2d\x0a\x0a\x72\x65", b"\x71\x65\x73\x74\x69\x6e\x66\x6f\x12",
                       b"\x1f\x7b\x22\x72\x65\x71\x22\x3a\x22\x73", b"\x65\x74\x56\x6f\x6c\x75\x6d\x65",
                       b"\x22\x2c\x22\x70\x61\x72\x61\x6d\x22\x3a\x22", b"\x30", b"\x22\x7d"],
        "volume_mid": [b"\x32\x12\x30\x22\x2e\x0a\x0a\x72\x65\x71", b"\x65\x73\x74\x69\x6e\x66\x6f\x12\x20\x7b\x22",
                       b"\x72\x65\x71\x22\x3a\x22\x73\x65\x74\x56", b"\x6f\x6c\x75\x6d\x65\x22\x2c\x22\x70\x61\x72",
                       b"\x61\x6d\x22\x3a\x22", b"\x32\x30", b"\x22\x7d"],
        "volume_max": [b"\x33\x12\x31\x22\x2f\x0a\x0a\x72\x65\x71", b"\x65\x73\x74\x69\x6e\x66\x6f\x12\x21\x7b\x22",
                       b"\x72\x65\x71\x22\x3a\x22\x73\x65\x74\x56", b"\x6f\x6c\x75\x6d\x65\x22\x2c\x22\x70\x61\x72",
                       b"\x61\x6d\x22\x3a\x22\x31\x30\x30\x22\x7d"]
    }

    def __init__(self, host, port):
        # self.client.connect((host, int(port)))
        self.host=host
        self.port=port
        self._is_on = False
        self.last_on = time()
        self.last_off = time()
        self.volume=0
      


    @property
    def is_on(self) -> bool:
        """Return true if the device is on."""
        return self._is_on
    
    

    def async_fetch_data(self):
            alive = self.async_check_alive()
            self._is_on = alive

    def async_check_alive(self):
       
    
       try:
          sock=socket.socket()
          sock.connect((self.host,9005))
          sock.send('Hello Server!'.encode('utf-8'))
          data = sock.recv(32).decode('utf-8')
          data1 = sock.recv(512).decode('latin-1')
          sock.close()
          cleaned_data = re.sub(r'[^\w\s]', '', data).strip()
          self.volume = match_volume(cleaned_data)
          power_state = match_power_state(data1)
          if power_state==0:
            return True
          if power_state==3:
            return False
        
       except ConnectionRefusedError:
            return False
       except Exception:
            return False


       
 
    def is_ip_reachable(ip, port, timeout=2):
        try:
            # 创建一个socket对象
            with socket.create_connection((ip,9005), 2) as sock:
                return True
        except (socket.error, socket.timeout):
            return False
 



    

    def exec(self, cmds):
        sock=socket.socket()
        sock.connect((self.host,9005))
        for cmd in cmds:
         sock.send(cmd)
        sock.close()

    def power(self):
        cmds = self.commands["power"]
        self.exec(cmds)

    def mongo(self):
        cmds = self.commands["mongo"]
        self.exec(cmds)

    def back(self):
        cmds = self.commands["return"]
        self.exec(cmds)

    def setting(self):
        cmds = self.commands["setting"]
        self.exec(cmds)

    def ok(self):
        cmds = self.commands["ok"]
        self.exec(cmds)

    def up(self):
        cmds = self.commands["up"]
        self.exec(cmds)

    def down(self):
        cmds = self.commands["down"]
        self.exec(cmds)

    def left(self):
        cmds = self.commands["left"]
        self.exec(cmds)

    def right(self):
        cmds = self.commands["right"]
        self.exec(cmds)

    def option(self):
        cmds = self.commands["option"]
        self.exec(cmds)

        

   
        

    def set_volume(self, volume):
        volume_hex = bytes(str(volume), 'utf-8')
        cmd = b""
        if volume < 10:
            self.commands['volume_min'][5] = volume_hex
            for b in self.commands['volume_min']:
                cmd += b
        elif volume == 100:
            for b in self.commands['volume_max']:
                cmd += b
        else:
            self.commands['volume_mid'][5] = volume_hex
            for b in self.commands['volume_mid']:
                cmd += b
        sock=socket.socket()
        sock.connect((self.host,9005))
        sock.send(cmd)
        sock.close()

    def volup(self):
        self.async_check_alive()
        if self.volume<100:
          self.volume+=1
          self.set_volume(self.volume)

    def voldown(self):
        self.async_check_alive()
        if self.volume>0:
          self.volume-=1
          self.set_volume(self.volume)

    def mute(self):
        self.set_volume(0)



    


    def async_send_command(self, command, **kwargs) -> None:
        """Send a command to one of the devices."""
        if command=='volup':
            self.volup()
        if command=='voldown':
            self.voldown()
        if command=='mute':
            self.mute()
        if command in self.commands:
           cmds = self.commands[command]
           self.exec(cmds)




