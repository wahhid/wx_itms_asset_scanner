from itms_asset_scanner import *
import itms_asset_scanner
import scanningdialog
import xmlrpclib
import wmi
import datetime
import sys

class Scanner_Frame(itms_asset_scanner.ScannerFrame):
    
    def __init__(self,parent):
        itms_asset_scanner.ScannerFrame.__init__(self, parent)        
        self.scanning_dialog = scanningdialog.Scanning_Dialog(None)
        self.user = 'admin'
        self.pwd = 'P@ssw0rd'
        self.dbname = 'itms'
        
    def btnscan_click( self, event):         
        
        self.scanning_dialog.Show()

        sock = xmlrpclib.ServerProxy('http://172.16.0.3:8069/xmlrpc/common')
        uid = sock.login(self.dbname , self.user , self.pwd)
        sock = xmlrpclib.ServerProxy('http://172.16.0.3:8069/xmlrpc/object')
        
        args = [('name','=', self.txtassetname.GetValue())]
        print "Scan Asset  : " + self.txtassetname.GetValue()
        ids = sock.execute(self.dbname, uid, self.pwd, 'asset.assets', 'search', args)
        
        if ids is None:            
            print "IDS null"
        else:
            print ids
            
        fields = []
        asset_data = sock.execute(self.dbname, uid, self.pwd, 'asset.assets', 'read', [ids[0]], fields)
        asset_value = {}
        values = {}
            
        c = wmi.WMI(asset_data[0]['name'],user=r"ta\administrator",password="berpelukanlagi")
                    
        for os in c.Win32_OperatingSystem():        
            values.update({'os':os.caption})
            print os.Caption
        
        for pro in c.Win32_Processor():    
            values.update({'processor':pro.name})
            print pro.name
                    
        print values            
        
        mems = c.Win32_PhysicalMemory()
        if len(mems) > 0:
            id = asset_data[0]['id']
            args = [('assets_id','=',id)]
            memory_ids = sock.execute(self.dbname, uid, self.pwd, 'asset.assets.memory', 'search', args)
            results = sock.execute(self.dbname, uid, self.pwd, 'asset.assets.memory', 'unlink', memory_ids)
            for mem in mems:    
                print mem
                memory_data = {}
                memory_data['assets_id'] = id
                memory_data['banklabel'] = mem.banklabel
                memory_data['capacity'] = mem.capacity
                memory_data['devicelocator'] = mem.devicelocator    
                memory_id = sock.execute(self.dbname, uid, self.pwd, 'asset.assets.memory', 'create', memory_data)            
                
        disks = c.Win32_DiskDrive()
        if len(disks) > 0:
            args = [('assets_id','=',id)]
            disk_ids = sock.execute(self.dbname, uid, self.pwd, 'asset.assets.disk', 'search', args)
            results = sock.execute(self.dbname, uid, self.pwd, 'asset.assets.disk', 'unlink', disk_ids)
            for disk in disks:    
                print disk
                disk_data = {}
                disk_data['assets_id'] = id
                disk_data['caption'] = disk.caption
                disk_data['size'] = disk.size        
                disk_id = sock.execute(self.dbname, uid, self.pwd, 'asset.assets.disk', 'create', disk_data)            
        values.update({'scan_status':'success'})                
        values.update({'last_scan': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})        
        self.txtresult.SetValue(str(values))
        self.scanning_dialog.Destroy()
        return True
    
    def btnclose_click( self, event ):
        self.Destroy()