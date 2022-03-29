# -*- encoding=utf8 -*-
import OlivOS
import OlivaDraw

class Event(object):
    def init(plugin_event, Proc):
        pass

    def init_after(plugin_event, Proc):
        OlivaDraw.msgReply.unity_init(plugin_event, Proc)

    def private_message(plugin_event, Proc):
        OlivaDraw.msgReply.unity_reply(plugin_event, Proc)

    def group_message(plugin_event, Proc):
        OlivaDraw.msgReply.unity_reply(plugin_event, Proc)

    def save(plugin_event, Proc):
        pass
