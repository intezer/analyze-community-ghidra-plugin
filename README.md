# Intezer Analyze Ghidra Plugin

Run the plugin in Ghidra to save yourself time while reversing.
The plugin helps you focus on the malicious and unique functions.
For more information about the plugin visit our blog: 
https://www.intezer.com/blog/intezer-analyze/community-ghidra-plugin-is-here/

![Running the plugin](https://github.com/intezer/analyze-community-ghidra-plugin/blob/master/media/ghidra_community.gif)

## Dependencies

This plugin requires the Python requests HTTP library at version 2.27.1 or newer, but not the 2.28 branch which has dropped support for Python 2 completely. The plugin checks its environment for the type of OS and then chooses an appropriate syntax for extending the PATH environment variable to include the location where requests is installed. On Linux and macOS, requests is recommended to be installed only for the user running Ghidra since Jython can only use Python 2.7 packages and that version of Python is past its end of life. A minimal install that is maintainable is to use `get-pip.py` and then install requests:

```
wget https://bootstrap.pypa.io/pip/2.7/get-pip.py
python2 get-pip.py --user
pip2 install --user requests
```

## Ghidra Version

This plugin is tested and working on Ghidra 10.1 branch up to 10.1.4.

## Installation

1. Clone the repo.

    ```
    $ git clone https://github.com/intezer/analyze-community-ghidra-plugin.git
    ```  
    
1. Add your API key to the environment variables: create a new variable called INTEZER_API_KEY with your API key value.
2. In Ghidra, from the CodeBrowser tool: click "Window" menu > "Bundle Manager".
3. In the Bundle Manager, click the green "+" button in the upper right corner of the window. If you hover the mouse over the button the tool tip should display "Display file chooser to add bundles to list".
4. Navigate to the directory "analyze-community-ghidra-plugin" wherever it was cloned by git and click "OK".
5. The path should appear in the table. It should have the checkbox to the left of it checked, and the text should be colored green. If the text of the path is not green, click the refresh button to the left of the "+".
4. Upload the sample to https://analyze.intezer.com.
5. In Ghidra, from the CodeBrowser window: click "Window" menu > "Script Manager" > Filter: 'intezer' > double click 'intezer_analyze_gh_community.py'

## macOS

If you are using macOS, setting the INTEZER_API_KEY via Terminal only sets the variable for that particular session. The variable will not be found by Ghidra if it was started in the GUI. To automatically set this environment variable for everything including GUI applications, copy the file `com.intezer.Analyze.plist` to `~/Library/LaunchAgents` in your user's home directory. Edit the file to change the fake API key to your correct API key, then logout and login again.
