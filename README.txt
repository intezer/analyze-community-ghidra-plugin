This is a plugin for Ghidra. It is based on the IDA plugin. This is a POC!
This plugin is build from 2 files one in python (intezer_analyze_gh.py) and the other is in JAVA (XMLPARSER.java).
The python script is responsible for getting information from the open file, sending and getting an analyzes from Analyze,
the answer is saved into a XML file.
The JAVA script is called afterwards and it parses the XML, and prints the information in a format of a table.

1. Clone the repo.
2. Add the path of the repo, into the list of directories that Ghidra uses for its scripts.
3. Before running the scripts, configure the path to the XML in both of the files. 
	In the python script the path is at "XML_PATH"
	In the java script it is in "path".
	change it to whatever you want.
4. Run the python script by double cliking on it.

