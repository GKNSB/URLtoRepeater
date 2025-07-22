from burp import IBurpExtender, ITab
from javax.swing import JPanel, JLabel, JTextField, JButton, JOptionPane, SwingConstants, Box, BoxLayout
from java.awt import BorderLayout, Dimension, FlowLayout
from java.net import URL

class BurpExtender(IBurpExtender, ITab):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("URL to Repeater")
        
        # Create main panel with border layout
        self._panel = JPanel(BorderLayout())
        
        # Create input panel with flow layout
        input_panel = JPanel(FlowLayout(FlowLayout.CENTER, 10, 50))
        
        # Create UI components
        self._urlField = JTextField(40)  # Wider text field
        go_button = JButton("Create Request", actionPerformed=self.createRequest)
        
        # Add components to input panel
        input_panel.add(JLabel("Target URL:"))
        input_panel.add(self._urlField)
        input_panel.add(go_button)
        
        # Add input panel to main panel
        self._panel.add(input_panel, BorderLayout.NORTH)
        
        # Add some padding at the bottom
        self._panel.add(Box.createVerticalStrut(20), BorderLayout.SOUTH)
        
        # Add custom tab to Burp UI
        callbacks.addSuiteTab(self)
    
    def getTabCaption(self):
        return "URL to Repeater"
    
    def getUiComponent(self):
        return self._panel
    
    def createRequest(self, event):
        raw_url = self._urlField.getText().strip()
        if not raw_url:
            JOptionPane.showMessageDialog(
                None,
                "Please enter a URL",
                "Error",
                JOptionPane.ERROR_MESSAGE
            )
            return
        
        try:
            # Parse URL components
            target_url = URL(raw_url)
            protocol = target_url.getProtocol()
            host = target_url.getHost()
            port = target_url.getPort()
            path = target_url.getPath() if target_url.getPath() else "/"
            query = target_url.getQuery()
            
            # Include query string if present
            full_path = path
            if query:
                full_path += "?" + query
            
            # Set default ports if needed
            if port == -1:
                port = 443 if protocol == "https" else 80
            
            # Create basic GET request
            request = "GET {} HTTP/1.1\r\n".format(full_path)
            request = request + "Host: {}\r\n".format(host)
            request = request + "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0\r\n"
            request = request + "Accept-Encoding: gzip, deflate, br\r\n"
            request = request + "Accept: */*\r\n\r\n"

            # Send to Repeater
            self._callbacks.sendToRepeater(
                host,
                port,
                protocol == "https",
                request,
                "URL: " + host
            )

        except Exception as e:
            JOptionPane.showMessageDialog(
                None,
                "Invalid URL: " + str(e),
                "Error",
                JOptionPane.ERROR_MESSAGE
            )