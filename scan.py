import urllib2
import netifaces
import time
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
  print('scan.url', url)

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
  print("Is this alive:", source_player)
  if source_player is None:
    print("No", ip)
    return False
  else:
    print("Yes", ip)
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
    if (player is None) or (player is not None and source_player_alive(player) is False):
      player = scan_range()

    if player is not None:
      yield player

    time.sleep(30); # check again after 5 minutes



'''
#########################

current_source = self.sourcePlayer
    new_source = None

    if current_source is None:
      print("Intial...")
      current_source = self.scan_source_player()
      print("Current source:", current_source)
    else:
      current_source = self.sourcePlayer
      print("verify if it is still alive though: " + current_source)

      # only check others when the current one is dead
      if self.source_player_alive(current_source, timeout=1) is False:
        print("self.sourcePlayer " + current_source + " is dead. get a new source")
        new_source = self.scan_source_player()

    # The current source is no longer available and a new source was found
    if new_source != current_source:
      Logger.info("Local IP: " + self.get_local_ip())
      Logger.info("Changing source player from " + str(current_source) + " to " + source_url)
      self.kill()
      self.run()

'''
