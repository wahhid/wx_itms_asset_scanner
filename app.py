import wx
import scannerframe


class Asset_ScannerMain(wx.App):
    
    def OnInit(self):
        self.scanner_frame = scannerframe.Scanner_Frame(None)
        self.scanner_frame.Show()   
        return True

app = Asset_ScannerMain(0)
app.MainLoop()