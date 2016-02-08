import urllib2
import netifaces
import time
import datetime
import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read('config.ini')

try:
  MP_HQ = int(Config.get('DEFAULT', 'MP_HQ'))
  MP_RANGE_MIN = int(Config.get('DEFAULT', 'MP_RANGE_MIN'))
  MP_RANGE_MAX = int(Config.get('DEFAULT', 'MP_RANGE_MAX'))
except:
  MP_HQ = 100
  MP_RANGE_MIN = 225
  MP_RANGE_MAX = 254

def get_local_ip():
  local_ip = None
  for ifname in netifaces.interfaces():
    try:
      for i in netifaces.ifaddresses(ifname)[netifaces.AF_INET]:
        a = i['addr']
        first = a.split('.')[0]

        if first != '127' and first != '169':
          local_ip = a
    except:
      pass

  if local_ip is None:
    print("Error: Cannot get local IP")

  return local_ip

def build_source_player_ip(lastNumber):
  local_ip = get_local_ip().split('.')[:3]
  return '.'.join(local_ip) + '.' + lastNumber

def get_source_player(ip):
  source_player = None

  url = 'http://' + ip + '/system/dev/packageStamp'

  req = urllib2.Request(url)
  try:
    res = urllib2.urlopen(req, timeout=0.3)
    code = res.getcode()
    if code == 200:
      source_player = ip

  except:
    pass

  return source_player

def source_player_alive(ip):
  source_player = get_source_player(ip)
  if source_player is None:
    return False
  else:
    return True

def scan_range():
  player = None
  for i in range(MP_RANGE_MIN, MP_RANGE_MAX):
    ip = build_source_player_ip(str(i))
    player = get_source_player(ip)
    if player is not None:
      break
  return player

def scan_source_player():
  player = None

  while True:
    if player is not None and source_player_alive(player) is False:
      player = None

    if player is None:
      player = scan_range()

    yield player
