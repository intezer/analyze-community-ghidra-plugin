//Parse XML file which contains genes, and print the output in a table. Implemented in Java.
//@author Nicole
//@category
//@keybinding
//@menupath
//@toolbar

import java.io.File;

import ghidra.app.script.GhidraScript;
import ghidra.app.tablechooser.AddressableRowObject;
import ghidra.app.tablechooser.StringColumnDisplay;
import ghidra.app.tablechooser.TableChooserDialog;
import ghidra.app.tablechooser.TableChooserExecutor;
import ghidra.program.model.address.Address;

import java.util.ArrayList;
import java.util.List;

import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

import java.io.IOException;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;
import java.nio.file.Paths;

public class XMLParser extends GhidraScript {

    @Override
    protected void run() throws Exception {
        String file_directory = System.getenv("intezer_analyze_ghidra_export_file_path");
        if (file_directory == null) {
            file_directory = System.getProperty("user.dir");
        }

        String filePath = Paths.get(file_directory, "items.xml").toString();
        parse(filePath);
    }

    TableChooserDialog tableDialog;

    private void parse(String path) {
        SAXParserFactory saxParserFactory = SAXParserFactory.newInstance();

        try {
            SAXParser saxParser = saxParserFactory.newSAXParser();
            IntezerAnalyzeHandler handler = new IntezerAnalyzeHandler();
            saxParser.parse(new File(path), handler);
            List<Row> rowList = handler.getRowList();
            fillTable(rowList);
        } catch (ParserConfigurationException | SAXException | IOException e) {
            println("An exception has ocurred while getting the genes");
            println(e.toString());
            e.printStackTrace();
        }
    }

    private void fillTable(List<Row> rowList) {
        TableChooserExecutor executor = null;
        tableDialog = createTableChooserDialog("Intezer Analyze Genes", executor);
        configureTableColumns(tableDialog);

        try {
            for (Row row : rowList) {
                tableDialog.add(row);
            }
        } catch (Exception e) {
            println("An exception has ocurred while trying to display the gene table");
        }

        tableDialog.show();
    }

    public class IntezerAnalyzeHandler extends DefaultHandler {

        private List<Row> rowList = new ArrayList<>();
        private Row row = new Row();
        private StringBuilder data = null;

        public List<Row> getRowList() {
            return rowList;
        }

        private boolean isAddr = false;
        private boolean isName = false;
        private boolean isSoftType = false;
        private boolean isCodeReuse = false;

        @Override
        public void startElement(String uri, String localName, String qName, Attributes attributes) throws SAXException {

            switch (qName) {
                case "gene":
                    break;
                case "function_address":
                    isAddr = true;
                    break;
                case "function_name":
                    isName = true;
                    break;
                case "software_type":
                    isSoftType = true;
                    break;
                case "code_reuse":
                    isCodeReuse = true;
                    break;
            }
            data = new StringBuilder();

        }

        @Override
        public void endElement(String uri, String localName, String qName) throws SAXException {

            switch (qName) {
                case "gene":
                    row = new Row();
                    break;
                case "function_address":
                    row.setFunctionAddr(data.toString());
                    isAddr = false;
                    break;
                case "function_name":
                    row.setFunctionName(data.toString());
                    isName = false;
                    break;
                case "software_type":
                    row.setSoftwareType(data.toString());
                    isSoftType = false;
                    break;
                case "code_reuse":
                    row.setCodeReuse(data.toString());
                    isCodeReuse = false;
                    break;
            }

            if (qName.equalsIgnoreCase("gene")) {
                rowList.add(row);
            }
        }

        @Override
        public void characters(char ch[], int start, int length) throws SAXException {
            data.append(new String(ch, start, length));
        }
    }

    class Row implements AddressableRowObject {
        private Address functionAddressAddr;
        private String functionAddressHex;
        private String functionName;
        private String softwareType;
        private String codeReuse;

        @Override
        public Address getAddress() {
            return functionAddressAddr;
        }

        public String getFunctionAddr() {
            return functionAddressHex;
        }

        public String getFunctionName() {
            return functionName;
        }

        public String getSoftwareType() {
            return softwareType;
        }

        public String getCodeReuse() {
            return codeReuse;
        }


        public void setFunctionAddr(String functionAddressHex) {
            this.functionAddressHex = functionAddressHex;

            Address addr = currentProgram.getAddressFactory().getAddress(functionAddressHex);
            this.functionAddressAddr = addr;
        }

        public void setFunctionName(String functionName) {
            this.functionName = functionName;
        }

        public void setSoftwareType(String softwareType) {
            this.softwareType = softwareType;
        }

        public void setCodeReuse(String codeReuse) {
            this.codeReuse = codeReuse;
        }

        @Override
        public String toString() {
            return "Gene:: function_address=" + this.functionAddressHex + " Name=" + this.functionName + " sof. type=" + this.softwareType +
                    " code reuse=" + this.codeReuse;
        }

    }

    private TableChooserExecutor createTableExecutor() {
        TableChooserExecutor executor = new TableChooserExecutor() {
            @Override
            public String getButtonName() {
                return "Hit Me";
            }

            @Override
            public boolean execute(AddressableRowObject rowObject) {
                return true;
            }
        };
        return executor;
    }

    private void configureTableColumns(TableChooserDialog tableDialog) {
        StringColumnDisplay functionAddress = new StringColumnDisplay() {
            @Override
            public String getColumnValue(AddressableRowObject rowObject) {
                Row table = (Row) rowObject;
                try {
                    return (table.getAddress()).toString();
                } catch (NullPointerException e) {
                    return "";
                }
            }

            @Override
            public String getColumnName() {
                return "Function Address";
            }

        };

        StringColumnDisplay functionName = new StringColumnDisplay() {
            @Override
            public String getColumnValue(AddressableRowObject rowObject) {
                Row table = (Row) rowObject;

                try {
                    return table.getFunctionName();
                } catch (NullPointerException e) {
                    return "";
                }
            }

            @Override
            public String getColumnName() {
                return "Function Name";
            }

        };

        StringColumnDisplay softwareType = new StringColumnDisplay() {
            @Override
            public String getColumnValue(AddressableRowObject rowObject) {
                Row table = (Row) rowObject;

                try {
                    return table.getSoftwareType();
                } catch (NullPointerException e) {
                    return "";
                }
            }

            @Override
            public String getColumnName() {
                return "Software Type";
            }
        };

        StringColumnDisplay codeReuse = new StringColumnDisplay() {
            @Override
            public String getColumnValue(AddressableRowObject rowObject) {
                Row table = (Row) rowObject;

                try {
                    return table.getCodeReuse();
                } catch (NullPointerException e) {
                    return "";
                }
            }

            @Override
            public String getColumnName() {
                return "Code Reuse";
            }
        };

        tableDialog.addCustomColumn(functionAddress);
        tableDialog.addCustomColumn(functionName);
        tableDialog.addCustomColumn(softwareType);
        tableDialog.addCustomColumn(codeReuse);
    }

}
