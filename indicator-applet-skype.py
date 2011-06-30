#!/usr/bin/env python
#
#Copyright 2010 Andreas Happe
#
#Authors:
#    Andreas Happe <andreashappe@snikt.net>
#
#This program is free software: you can redistribute it and/or modify it 
#under the terms of either or both of the following licenses:
#
#1) the GNU Lesser General Public License version 3, as published by the 
#Free Software Foundation; and/or
#2) the GNU Lesser General Public License version 2.1, as published by 
#the Free Software Foundation.
#
#This program is distributed in the hope that it will be useful, but 
#WITHOUT ANY WARRANTY; without even the implied warranties of 
#MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR 
#PURPOSE.  See the applicable version of the GNU Lesser General Public 
#License for more details.
#
#You should have received a copy of both the GNU Lesser General Public 
#License version 3 and version 2.1 along with this program.  If not, see 
#<http://www.gnu.org/licenses/>
#


# Documentation:
# just start it

import indicate
import gobject
import gtk
import Skype4Py

import os
import sys
import commands
import time

import threading

def do_nothing(indicator):
    True

# this is the high-level notification functionality
class NotificationServer:
  def __init__(self):
    self.server = indicate.indicate_server_ref_default()
    self.server.set_type("message.im")
#   this is kinda ugly, or?
    self.server.set_desktop_file("/usr/share/applications/skype-wrapper.desktop")
    self.server.show()
    pass

  def connect(self, skype):
    self.skype = skype
    self.server.connect("server-display", self.on_click)

  def on_click(self, server,data=None):
    self.skype.skype.Client.Focus()

  def show_conversation(self, indicator, timestamp):
    display_name = indicator.get_property("name")

    self.skype.remove_conversation(display_name)

    # this might blow up.. don't know why, seems like an error within skype
    self.skype.show_chat_windows(display_name);

  def show_indicator(self, conversation):
    print "adding " + conversation.display_name

    #try:
      ## Ubuntu 9.10 and above
      #indicator = indicate.Indicator()
    #except:
      ## Ubuntu 9.04
      #indicator = indicate.IndicatorMessage()

    indicator = indicate.Indicator()
    indicator.set_property("name", conversation.display_name)
    indicator.set_property("subtype", "instant")
    indicator.set_property('draw-attention', 'true');

    indicator.set_property_time('time', conversation.timestamp)
   
    indicator.connect("user-display", self.show_conversation)
    indicator.show()


class UnreadConversation:
  def __init__(self, display_name, timestamp, skype_id):
    self.display_name = display_name
    self.count = 0
    self.timestamps = [timestamp]
    self.timestamp=timestamp

  def add_timestamp(self, timestamp):
    if not timestamp in self.timestamps:
      self.timestamps.append(timestamp)
      self.count += 1




class SkypeBehaviour:
  # initialize skype
  def __init__(self):
    print "entering init, defining skype"  
    self.skype = Skype4Py.Skype()
    self.skype.Client.Start(Minimized=True)


    print "attaching..."
    time.sleep(4)
    while True:
        try:
            self.skype.Attach(Wait=False)
            break
        except:
            print "."
                        
    print "attached. bam!"
    time.sleep(2)
    print "set OnMessageStatus"
    self.skype.OnMessageStatus = self.OnMessageStatus
    self.name_mappings = {}
    self.unread_conversations = {}
    self.cb_show_conversation = None
    self.cb_show_indicator = None

  def SetShowConversationCallback(self, func):
    self.cb_show_conversation = func

  def SetShowIndicatorCallback(self, func):
    self.cb_show_indicator = func

  def OnMessageStatus(self, mesg, Status):
    print 'message status'
    print mesg
    print Status
    if Status == 'SENDING':
      print(mesg.FromDisplayName + "sent a message")

      #display_name = mesg.FromDisplayName
      #if not display_name in self.unread_conversations:
        #conversation = UnreadConversation(display_name, mesg.Timestamp, mesg.Sender.Handle)
        #self.name_mappings[display_name] = mesg.Sender.Handle
        ## TODO: should we do some sort of update for this?
        #self.unread_conversations[display_name] = conversation
      #else:
        #self.unread_conversations[display_name].add_timestamp(mesg.Timestamp)
      #self.cb_show_indicator(conversation)

  def remove_conversation(self, display_name):
    skype_name = self.name_mappings[display_name]
    del self.unread_conversations[display_name]
    return skype_name

  def show_chat_windows(self, skype_name):
    self.skype.Client.OpenMessageDialog(self.name_mappings[skype_name])

  

def runCheck():
    print "in runcheck"
    print "checking if running"
    #print self.skype.Client.IsRunning
    #calling self.skype.Client.IsRunning crashes. wtf. begin hack:
    output = commands.getoutput('ps -A | grep skype' )
    print output
    if 'skype' not in output:
        print "not running"
        gtk.main_quit()
    if 'defunct' in output:
        print "ZOMBIES!!!"
        gtk.main_quit()
    print "running - restarting timer"
    threading.Timer(5, runCheck).start()

if __name__ == "__main__":

  os.chdir('/usr/share/skype-wrapper')
  
  print "1"
  skype = SkypeBehaviour();
  print "2"
  server = NotificationServer()
  print "3"
  runCheck()
  skype.SetShowConversationCallback(server.show_conversation)
  skype.SetShowIndicatorCallback(server.show_indicator)
  server.connect(skype)

  #workaround_show_skype()

  # why is this needed?
  #server.activate_timeout_check()

  # check for newly unread messages..
  #skype.check_timeout(server)
  gtk.main()

