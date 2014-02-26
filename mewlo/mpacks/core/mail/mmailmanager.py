"""
mmailmanager.py
helper object for emailing
ATTN:TODO Add logging, better error reporting, fix pyzmail or switch to another higher level mail lib
"""


# mewlo imports
from ..manager import manager
from ..setting.msettings import MewloSettings
from ..eventlog.mevent import EFailure, EException
from ..const.mconst import MewloConst as siteconst

# python library imports
import pyzmail

# python imports
import smtplib






class MewloMailManager(manager.MewloManager):
    """A helper object that handles all mail sending."""

    # class constants
    description = "Provides an API for sending and checking mail."
    typestr = "core"



    def __init__(self, mewlosite, debugmode):
        """Constructor."""
        super(MewloMailManager,self).__init__(mewlosite, debugmode)

    def startup(self, eventlist):
        super(MewloMailManager,self).startup(eventlist)
        # use site settings to configure mail settings

    def shutdown(self):
        super(MewloMailManager,self).shutdown()






    def send_email(self, maildict):
        """Just a wrapper around our mail sender function of choice."""
        return self.send_email_smtplib(maildict)




    def send_email_smtplib(self, maildict):
        """Send a mail message."""

        # mail settings
        mailsettings = self.get_setting_value(siteconst.DEF_SETTINGSEC_mail)

        # parameters
        efrom = mailsettings['mail_from']
        eto = maildict['to']
        esubject = maildict['subject']
        ebody = maildict['body']
        #
        etos = ", ".join(eto)
        eheader = 'To: {0}\nFrom: {1}\nSubject:{2}\n'.format(etos,efrom,esubject)
        efullmessage = eheader + '\n' + ebody + '\n'

        # smtp info for sending
        smtp_host = mailsettings['smtp_host']
        smtp_port = mailsettings['smtp_port']
        smtp_mode = mailsettings['smtp_mode']
        smtp_login = mailsettings['smtp_login']
        smtp_password = mailsettings['smtp_password']
        smtp_timeout = 10

        #print "MAIL SETTINGS: "+str(mailsettings)
        #print "SENDING TO: "+etos

        try:
            #print "ATTN: send_email 1"
            #server = smtplib.SMTP(host=smtp_host, port=smtp_port, local_hostname=None, timeout=smtp_timeout)
            server = smtplib.SMTP_SSL(host=smtp_host, port=smtp_port, local_hostname=None, timeout=smtp_timeout)
            #server.set_debuglevel(1)
            #print "ATTN: send_email 2"
            server.login(smtp_login, smtp_password)
            #print "ATTN: send_email 3"
            server.sendmail(efrom, eto, efullmessage)
            #print "ATTN: send_email 4"
            server.quit()
            #print "ATTN: send_email 5"
        except Exception as exp:
            return EException("Failed to send email ({0})".format(str(exp)), exp=exp)

        return None






    def send_email_pyzmail(self, maildict):
        """Send a mail message.
        pyzmail is supposed to be good but my experience with it has been terrible.  It fails mysteriously and takes minutes to time out.
        and the compose_mail function seems to return broken value from mail_from return argument.
        """

        # mail settings
        mailsettings = self.get_setting_value(siteconst.DEF_SETTINGSEC_mail)

        # parameters
        efrom = mailsettings['mail_from']
        eto = maildict['to']
        esubject = maildict['subject']
        ebody = maildict['body']
        preferred_encoding = 'iso-8859-1'
        text_encoding = preferred_encoding

        # compose email and create payload
        payload, mail_from, rcpt_to, msg_id = pyzmail.compose_mail(efrom, eto, esubject, preferred_encoding, (ebody,text_encoding))
        # ATTN: return value of mail_from is bad, and was causing failure to send email for hours before identified

        #print payload
        #msg = pyzmail.PyzMessage.factory(payload)
        #print msg.get_subject()

        #print "MAIL SETTINGS: "+str(mailsettings)
        #print "MAIL FROM: "+mail_from
        #print "MAIL TO: "+str(rcpt_to)

        # smtp info for sending
        smtp_host = mailsettings['smtp_host']
        smtp_port = mailsettings['smtp_port']
        smtp_mode = mailsettings['smtp_mode']
        smtp_login = mailsettings['smtp_login']
        smtp_password = mailsettings['smtp_password']

        # actually send the mail
        ret=pyzmail.send_mail(payload, efrom, eto, smtp_host=smtp_host, smtp_port=smtp_port, smtp_mode=smtp_mode, smtp_login=smtp_login, smtp_password=smtp_password)

        # check return value
        if isinstance(ret, dict):
            if ret:
                return EFailure('failed recipients: ' + ', '.join(ret.keys()))
            else:
                return None

        return EFailure('error:'+ ret)




