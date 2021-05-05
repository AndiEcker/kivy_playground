# Example of sharing from an app
#
# a) Share text using ShareSheet
# b) Share html file using ShareSheet
# c) Share text file directly to Google Drive
#
# The setup instructions are critical, and non-trivial
# This example does not depend on androidx

from textwrap import fill
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from android import mActivity, autoclass, cast
from android.storage import app_storage_path

JString = autoclass('java.lang.String')
File    = autoclass('java.io.File')
Intent  = autoclass('android.content.Intent')
FileProvider = autoclass('android.support.v4.content.FileProvider')

'''
README, perhaps enlightenment follows in these 4 steps, so README

If you want to understand what is happening here you will need to read about
Android's  : Intent , Activity, content url, and MIME types

One day there will be a p4a option that automates steps 1) and 2)
https://github.com/kivy/python-for-android/pull/2200
One day there will be a p4a option that automates some of step 4)
https://github.com/kivy/python-for-android/issues/2020

1) Make a local copy of p4a
---------------------------
Create a (or use existing) directory <some_path> BUT NOT the App directory
Go to https://github.com/kivy/python-for-android/tree/master
From the "Code" button select download a zip file
Unzip and place in the directory <some_path> 
In buildozer.spec set, for your value of <some_path>:

p4a.source_dir = <some_path>/python-for-android-master

2) Edit the AndroidManifest file.
---------------------------------
Edit:
<some_path>/python-for-android-master/pythonforandroid/bootstraps/sdl2/build/templates/AndroidManifest.tmpl.xml

Add the following lines at the end of the file, before "</application>" 

    <provider
        android:name="android.support.v4.content.FileProvider"
        android:authorities="{{ args.package }}.fileprovider"
        android:grantUriPermissions="true"
        android:exported="false">
        <meta-data
            android:name="android.support.FILE_PROVIDER_PATHS"
            android:resource="@xml/provider_paths" />
    </provider>

3) Specify the folders that can be shared.
------------------------------------------
Create a file 'provider_paths.xml' containing:

<?xml version="1.0" encoding="utf-8"?>
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <files-path name="app storage" path="."/>
</paths>

Save the file in both of the following directories:
<App directory>/src/debug/res/xml/provider_paths.xml
<App directory>/src/main/res/xml/provider_paths.xml

This example of provider_paths.xml enables sharing of the App local storage.

If you want to share some other location don't ask me, read the docs:
https://developer.android.com/reference/android/support/v4/content/FileProvider.html#SpecifyFiles

4) Include the Java package containing FileProvider in buildozer.spec
---------------------------------------------------------------------

android.gradle_dependencies = "com.android.support:support-core-utils:27.0.0"

NOTE: This approach is depreciated by Android.  :(
But I sucessfully built with  android.api =27 , also 29, and 30 
I do have a version of this app that uses androidx with additional p4a tweaking. 

As a sanity check, there were 2 changes to buildozer.spec

References:

MIMEtypes:
https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
https://developer.android.com/training/sharing/receive#handling-content
https://www.iana.org/assignments/media-types/media-types.xhtml

Android:
https://developer.android.com/courses/fundamentals-training/toc-v2
https://developer.android.com/training/sharing/send
https://developer.android.com/guide/topics/providers/content-provider-basics
https://developer.android.com/guide/topics/providers/content-provider-creating
https://developer.android.com/reference/android/support/v4/content/FileProvider.html#SpecifyFiles
'''

class ShareSend(App):
    
    def share_text_choose(self, data):
        send = Intent()
        send.setAction(Intent.ACTION_SEND)  
        send.setType("text/plain")
        send.putExtra(Intent.EXTRA_TEXT, JString(data))
        try:
            mActivity.startActivity(Intent.createChooser(send,None))
        except Exception as e:
            self.err.text = fill('Text share issue :\n'+str(e),40)

    def create_file_intent(self, filepath, MIMEtype):
        context =  mActivity.getApplicationContext()
        try:
            # matches android:authorities in AndroidManifest
            auth = str(context.getPackageName()) + '.fileprovider'
            contentUri = FileProvider.getUriForFile(context,auth,File(filepath))
        except Exception as e:
            self.err.text = fill('File Provider setup issue :\n'+str(e),40)
            return None
        parcelable = cast('android.os.Parcelable', contentUri)  
        send = Intent()
        send.setAction(Intent.ACTION_SEND)  
        send.setType(MIMEtype)
        send.putExtra(Intent.EXTRA_STREAM, parcelable)
        send.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        return send
        
    def share_file_choose(self, filepath, MIMEtype):
        send = self.create_file_intent(filepath,MIMEtype)
        try:
            if send:
                mActivity.startActivity(Intent.createChooser(send,None))
        except Exception as e:
            self.err.text = fill('File share issue :\n'+str(e),40)
            
    def share_file_direct(self, filepath, MIMEtype, app):
        send = self.create_file_intent(filepath,MIMEtype)
        try:
            if send:
                send.setPackage(app)
                mActivity.startActivity(send)
        except Exception as e:
            self.err.text = fill('File share issue with '+app+' : '+str(e),40)

    def button1_pressed(self,b):
        self.share_text_choose('Greetings Earthlings')

    def button2_pressed(self,b):
        # FYI, other apps filter what they can receive using MIMEtype 
        self.share_file_choose(self.filename1,
                               "text/html")

    def button3_pressed(self,b):
        self.share_file_direct(self.filename2,
                               "text/plain",
                               'com.google.android.apps.docs')
        '''
        # Some examples of other possibilites, but no warranty
        com.dropbox.android = Dropbox
        com.android.bluetooth = Bluetooth
        com.android.email = Email
        com.google.android.gm = Gmail
        com.microsoft.skydrive = Skydrive
        com.google.android.apps.docs = Googledrive
        com.google.android.apps.maps = Maps
        '''

    def on_start(self):
        # Create some test data
        self.filename1 = join(app_storage_path(),'from_space.html')
        with open(self.filename1, "w") as f:
            f.write("<html>\n")
            f.write(" <head>\n")
            f.write(" </head>\n")
            f.write(" <body>\n")
            f.write("  <h1>Greetings Earthlings<h1>\n")
            f.write("  <h1>We come in please?<h1>\n")
            f.write(" </body>\n")
            f.write("</html>\n")
        self.filename2 = join(app_storage_path(),'from_earth.txt')
        with open(self.filename2, "w") as f: 
            f.write("Fear Google puny Earthlings\n")

    def build(self):
        b1 = Button(text='Share TEXT via ShareSheet',
                    on_press=self.button1_pressed)
        b2 = Button(text='Share HTML FILE via ShareSheet',
                    on_press=self.button2_pressed)
        b3 = Button(text='Share TEXT FILE only with Google Drive',
                    on_press=self.button3_pressed)
        self.err = Label()
        box = BoxLayout(orientation='vertical')
        box.add_widget(b1)
        box.add_widget(b2)
        box.add_widget(b3)
        box.add_widget(self.err)
        return box

ShareSend().run()
