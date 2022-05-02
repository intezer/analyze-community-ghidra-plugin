**Intezer Analyze Ghidra Plugin**
Run the plugin in Ghidra to save yourself time while reversing.
The plugin helps you focus on the malicious and unique functions.
For more information about the plugin visit our blog: 
https://www.intezer.com/blog/intezer-analyze/community-ghidra-plugin-is-here/

![alt text](https://github.com/intezer/analyze-community-ghidra-plugin/blob/master/media/ghidra_community.gif)

**Dependencies**

This plugin requires the Python requests HTTP library. The plugin checks its environment for the type of OS and then chooses an appropriate syntax for extending the PATH environment variable to include the location where requests is installed. On Linux and macOS, requests is recommended to be installed only for the user running Ghidra since Jython can only use Python 2.7 packages and that version of Python is past its end of life. A minimal install that is maintainable is to use `get-pip.py` and then install requests:

```
wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
python2 get-pip.py --user
pip2 install --user requests
```

**Installation**
1. Clone the repo.

    ```
    $ git clone https://github.com/intezer/analyze-community-ghidra-plugin.git
    ```  
    
1. Add your API key to the environment variables: create a new variable called INTEZER_API_KEY with your API key value.
2. In Ghidra: add the path of the repo into the list of directories that Ghidra uses for its scripts. From Ghidra's first main window: click "Edit" menu > "Plugin Path..." > "Add Dir..." > Navigate to 'analyze-community-ghidra-plugin' > "Add Directory" > "OK"
4. Upload the sample to https://analyze.intezer.com.
5. In Ghidra, from the CodeBrowser window: click "Window" menu > "Script Manager" > Filter: 'intezer' > double click 'intezer_analyze_gh_community.py'

**Known Issues**

New versions of the requests module are not working with Jython. The solution is to downgrade the Python requests module to 2.7.0. 

# macOS

If you are using macOS, setting the INTEZER_API_KEY via Terminal only sets the variable for that particular session. The variable will not be found by Ghidra if it was started in the GUI. To automatically set this environment variable for everything including GUI applications, copy the file `com.intezer.Analyze.plist` to `~/Library/LaunchAgents` in your user's home directory. Edit the file to change the fake API key to your correct API key, then logout and login again.
