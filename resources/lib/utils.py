import xbmc
import xbmcvfs
import xbmcaddon
import os
import time
import sys
import buggalo
import re
import random
    
__addon_id__= u'service.watchedlist'
__Addon = xbmcaddon.Addon(__addon_id__)

# XBMC-JSON
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson


def data_dir():
    # get user data directory of this addon. 
    # according to http://wiki.xbmc.org/index.php?title=Add-on_Rules#Requirements_for_scripts_and_plugins
    __datapath__ = xbmc.translatePath( __Addon.getAddonInfo('profile') ).decode('utf-8')
    if not xbmcvfs.exists(__datapath__):
        xbmcvfs.mkdir(__datapath__)
    return __datapath__

def addon_dir():
    # get source directory of this addon.
    # according to http://wiki.xbmc.org/index.php?title=Add-on_Rules#Requirements_for_scripts_and_plugins
    return __Addon.getAddonInfo('path').decode('utf-8')

def log(message,loglevel=xbmc.LOGNOTICE):
    # save message to xbmc.log. `message` has to be unicode
    # loglevels: xbmc.LOGDEBUG, xbmc.LOGINFO, xbmc.LOGNOTICE, xbmc.LOGWARNING, xbmc.LOGERROR, xbmc.LOGFATAL
    
    # message should be unicode object. Encoding according to http://wiki.xbmc.org/index.php?title=Add-on_unicode_paths#Logging
    xbmc.log(encode(__addon_id__ + u": " + message), level=loglevel)


def showNotification(title,message, time=4000):
    # Show Notification with given `title` and `message`.
    # `title` and `message` have to be unicode
    __addoniconpath__ = os.path.join(addon_dir(),"icon.png")
    log(u'Notification. %s: %s' % (title, message) )
    if xbmc.Player().isPlaying() == False:
        xbmc.executebuiltin(encode('Notification("' + title + '","' + message + '",'+(str(time)).decode('utf-8')+',"' + __addoniconpath__ + '")'))
    if getSetting('debug') == 'true':
        xbmc.sleep(250) # time to read the message
        

def setSetting(name,value):
    __Addon.setSetting(name,value)

def getSetting(name):
    return __Addon.getSetting(name)
    
def getString(string_id):
    # return a localized string from resources/language/*.po
    # The returned string is unicode
    return __Addon.getLocalizedString(string_id)

def encode(string):
    return string.encode('UTF-8','replace')

def decode(string):
    return string.decode('UTF-8') 


def footprint():
    log(u'data_dir() = %s' % data_dir(), xbmc.LOGDEBUG)
    log(u'addon_dir() = %s' % addon_dir(), xbmc.LOGDEBUG)
    log(u'debug = %s' % getSetting('debug'), xbmc.LOGDEBUG)
    log(u'w_movies = %s' % getSetting('w_movies'), xbmc.LOGDEBUG)
    log(u'w_episodes = %s' % getSetting('w_episodes'), xbmc.LOGDEBUG)
    log(u'autostart = %s' % getSetting('autostart'), xbmc.LOGDEBUG)
    log(u'periodic = %s' % getSetting('periodic'), xbmc.LOGDEBUG)
    log(u'interval = %s' % getSetting('interval'), xbmc.LOGDEBUG)
    log(u'delay = %s' % getSetting('delay'), xbmc.LOGDEBUG)
    log(u'progressdialog = %s' % getSetting('progressdialog'), xbmc.LOGDEBUG)
    log(u'extdb = %s' % getSetting('extdb'), xbmc.LOGDEBUG)
    log(u'dbpath = %s' % getSetting('dbpath'), xbmc.LOGDEBUG)
    log(u'dbfilename = %s' % getSetting('dbfilename'), xbmc.LOGDEBUG)
    log(u'dbbackup = %s' % getSetting('dbbackup'), xbmc.LOGDEBUG)
    
# "2013-05-10 21:23:24"  --->  1368213804
def sqlDateTimeToTimeStamp(sqlDateTime):
    if sqlDateTime == '':
        return 0 # NULL timestamp
    else:
        # the usage of strptime produces the error "Failed to import _strptime because the import lock is held by another thread."
        # to solve this, in case of error try again after random time
        try:
            for i in range(5):
                try:
                    return int(time.mktime(time.strptime(sqlDateTime,"%Y-%m-%d %H:%M:%S")))
                except:
                    xbmc.wait( random.randint(200, 500) )
        except:
            return 0 # error, but timestamp=0 works in the addon
                    
                

#  1368213804  --->  "2013-05-10 21:23:24"
def TimeStamptosqlDateTime(TimeStamp):
    if TimeStamp == 0:
        return ""
    else:
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(TimeStamp))    
    
def executeJSON(request):
    rpccmd = simplejson.dumps(request) # create string from dict
    json_query = xbmc.executeJSONRPC(rpccmd)
    json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_response = simplejson.loads(json_query)  
    # in case of exception this will be sent
    buggalo.addExtraData('len(json_query)',len(json_query));
    buggalo.addExtraData('len(json_response)', len(json_response));
    return json_response

def buggalo_extradata_settings():
    # add extradata to buggalo
    buggalo.addExtraData('data_dir', data_dir());
    buggalo.addExtraData('addon_dir', addon_dir());
    buggalo.addExtraData('setting_debug', getSetting("debug"));
    buggalo.addExtraData('setting_w_movies', getSetting("w_movies"));
    buggalo.addExtraData('setting_w_episodes', getSetting("w_episodes"));
    buggalo.addExtraData('setting_autostart', getSetting("autostart"));
    buggalo.addExtraData('setting_delay', getSetting("delay"));
    buggalo.addExtraData('setting_starttype', getSetting("starttype"));
    buggalo.addExtraData('setting_interval', getSetting("interval"));
    buggalo.addExtraData('setting_progressdialog', getSetting("progressdialog"));
    buggalo.addExtraData('setting_watch_user', getSetting("watch_user"));
    buggalo.addExtraData('setting_extdb', getSetting("extdb"));
    buggalo.addExtraData('setting_dbpath', getSetting("dbpath"));
    buggalo.addExtraData('setting_dbfilename', getSetting("dbfilename"));
    buggalo.addExtraData('setting_dbbackup', getSetting("dbbackup"));
    buggalo.addExtraData('setting_db_format', getSetting("db_format"));
    buggalo.addExtraData('setting_mysql_server', getSetting("mysql_server"));
    buggalo.addExtraData('setting_mysql_port', getSetting("mysql_port"));
    buggalo.addExtraData('setting_mysql_db', getSetting("mysql_db"));

    
def translateSMB(path):
    # translate "smb://..." to "\\..." in windows. Don't change other paths
    if os.sep == '\\': # windows os
        res_smb = re.compile('smb://(\w+)/(.+)').findall(path)
        if len(res_smb) == 0:
            # path is not smb://...
            return path
        else:
            # create smb path
            return '\\\\'+res_smb[0][0]+'\\'+res_smb[0][1].replace('/', '\\')
    else:
        # linux os. Path with smb:// is correct, but can not be accessed with normal python file access
        return path
    
def fileaccessmode(path):
    # determine file access mode in case of smb share no direct access possible
    res_smb = re.compile('smb://(\w+)/(.+)').findall(path)
    res_nw = re.compile('(\w+)://(.*?)').findall(path)
    if os.sep == '\\': # windows os
        if len(res_smb) != 0:
            # smb accessable in windows
            return 'normal'
        elif len(res_nw) != 0:
            # path is ftp or nfs network
            return 'copy'
        else:
            # path is not smb://...
            return 'normal'
    else:
        # linux os. 
        if len(res_nw) != 0:
            # Path with smb:// or ftp:// is correct, but can not be accessed with normal python file access
            # use virtual file system
            return 'copy'
        else:
            # "normal" path
            return 'normal'

def sleepsafe(waittime):
    # sleep waittime [seconds] and return if a shutdown is requested
    starttime = time.time()
    while not xbmc.abortRequested:
        if time.time() > starttime + waittime:
            return 0
        xbmc.sleep(1000) # wait 1 second until next check if xbmc terminates
    return 1 # shutdown requested
