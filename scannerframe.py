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
        
        try:
            self.txtresult.Clear()
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
               
            if self.rd_hardware.GetValue() == True:
                                                        
                for os in c.Win32_OperatingSystem():        
                    values.update({'os':os.caption})
                    self.txtresult.AppendText('Operating System : ' + os.caption + '\n')
                
                for pro in c.Win32_Processor():    
                    values.update({'processor':pro.name})
                    self.txtresult.AppendText('Processor : ' + pro.name + '\n')                
                            
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
                        self.txtresult.AppendText('Memory : ' + str(memory_data) + '\n')
                        
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
                        self.txtresult.AppendText('Disk : ' + str(disk_data) + '\n')
                    
                values.update({'scan_status':'success'})                
                values.update({'last_scan': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                results = sock.execute(self.dbname, uid, self.pwd, 'asset.assets', 'write', [id], values)
                    
            if self.rd_software.GetValue() == True: 
                print "Starting Query Product"
                softs = c.query("SELECT * FROM Win32_Product")
                print "Finished Query Product"
                if len(softs) > 1:
                    id = asset_data[0]['id']
                    args = [('assets_id','=',id)]
                    soft_ids = sock.execute(self.dbname, uid, self.pwd, 'asset.assets.software', 'search', args)
                    results = sock.execute(self.dbname, uid, self.pwd, 'asset.assets.software', 'unlink', soft_ids)
                    for soft in softs:
                        try:
                            soft_id = None
                            self.txtresult.AppendText('Software : ' + soft.description + '\n')
                            args = [('name','=',soft.description)]
                            ids = sock.execute(self.dbname, uid, self.pwd, 'asset.software', 'search', args)    
                            if len(ids) == 0:
                                soft_data = {}
                                soft_data['name'] = soft.description
                                soft_id = sock.execute(self.dbname, uid, self.pwd, 'asset.software', 'create', soft_data)            
                            else:
                                soft_id = ids[0]
                                print "Software ID : " , soft_id
                                assets_software_data = {}
                                assets_software_data['assets_id'] = id
                                assets_software_data['sofware_id'] = soft_id                
                                assets_software_id = soft_id = sock.execute(self.dbname, uid, self.pwd, 'asset.assets.software', 'create', assets_software_data)
                                    
                        except:
                            print "Error : " , sys.exc_info()[0]
                            self.txtresult.AppendText("Error : " + sys.exc_info()[0] + '\n')
                            
                    values.update({'scan_status':'success'})                
                    values.update({'last_scan': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                    results = sock.execute(self.dbname, uid, self.pwd, 'asset.assets', 'write', [id], values)
                                                                                                  
        except Exception, e:
            print e        
            self.txtresult.AppendText('Error : ' + e + '\n')
        finally:
            self.scanning_dialog.Hide()
            return True
    
    def btnclose_click( self, event ):
        self.Destroy()