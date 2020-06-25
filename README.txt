This is a plugin for Ghidra. It is based on the IDA plugin. This is a POC!
This plugin is build from 2 files one in python (intezer_analyze_gh.py) and the other is in JAVA (XMLPARSER.java).
The python script is responsible for getting information from the open file, sending and getting an analyzes from Analyze, the data is saved into an XML file.
The JAVA script is called afterwards and it parses the XML, and prints the information in a format of a table.

1. Clone the repo.
2. Add the path of the repo, into the list of directories that Ghidra uses for its scripts.
3. Add your API key to the environment variables - create a new variable called INTEZER_API_KEY wit yourh API key value.
3. Run the python script by double clicking on it.
