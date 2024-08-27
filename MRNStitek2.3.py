import wx
import socket
import ctypes
import sys
import json
import os

class SettingsDialog(wx.Dialog):
    def __init__(self, parent, title, initial_ip, initial_port, initial_remap):
        super(SettingsDialog, self).__init__(parent, title=title, size=(300, 200))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        hbox_ip = wx.BoxSizer(wx.HORIZONTAL)
        lbl_ip = wx.StaticText(panel, label="IP tiskárny:")
        hbox_ip.Add(lbl_ip, flag=wx.RIGHT, border=8)
        self.txt_ip = wx.TextCtrl(panel, value=initial_ip)
        hbox_ip.Add(self.txt_ip, proportion=1)
        vbox.Add(hbox_ip, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        hbox_port = wx.BoxSizer(wx.HORIZONTAL)
        lbl_port = wx.StaticText(panel, label="Port:")
        hbox_port.Add(lbl_port, flag=wx.RIGHT, border=8)
        self.txt_port = wx.TextCtrl(panel, value=str(initial_port))
        hbox_port.Add(self.txt_port, proportion=1)
        vbox.Add(hbox_port, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        self.chk_remap = wx.CheckBox(panel, label="Remapování kláves QWERTZ")
        self.chk_remap.SetValue(initial_remap)
        vbox.Add(self.chk_remap, flag=wx.LEFT|wx.TOP, border=10)

        pnl_buttons = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(panel, wx.ID_OK)
        btn_cancel = wx.Button(panel, wx.ID_CANCEL)
        pnl_buttons.AddButton(btn_ok)
        pnl_buttons.AddButton(btn_cancel)
        pnl_buttons.Realize()
        vbox.Add(pnl_buttons, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        panel.SetSizer(vbox)

class LabelPrinterFrame(wx.Frame):
    def __init__(self, parent, title):
        super(LabelPrinterFrame, self).__init__(parent, title=title, size=(400, 250))
        icon = wx.IconLocation(sys.executable, 0)
        self.SetIcon(wx.Icon(icon))

        self.settings_file_path = os.path.join(os.path.expanduser('~'), 'Documents', 'mrnstitek.json')
        self.load_settings()

        self.InitUI()
    
    def InitUI(self):
        panel = wx.Panel(self)
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        label_width = 80
        
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        mrn_label = wx.StaticText(panel, label='MRN:')
        mrn_label_font = mrn_label.GetFont()  # Získání aktuálního fontu
        mrn_label_font.SetWeight(wx.FONTWEIGHT_BOLD)  # Nastavení fontu na tučné
        mrn_label.SetFont(mrn_label_font)  # Aplikace nového fontu na popisek
        mrn_label.SetMinSize((label_width, -1))  # Nastaví pevnou šířku pro popisek
        hbox1.Add(mrn_label, flag=wx.RIGHT, border=10)
        self.mrn_textctrl = wx.TextCtrl(panel, size=(250, -1), style=wx.TE_PROCESS_ENTER)
        self.mrn_textctrl.Bind(wx.EVT_TEXT_ENTER, self.OnPrint)
        hbox1.Add(self.mrn_textctrl, proportion=1)
        clear_mrn_btn = wx.Button(panel, label='X', size=(30, 30))
        clear_mrn_btn.Bind(wx.EVT_BUTTON, lambda evt, temp=self.mrn_textctrl: self.ClearText(evt, temp))
        hbox1.Add(clear_mrn_btn, flag=wx.LEFT, border=5)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.ALL, border=10)

        
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        item_label = wx.StaticText(panel, label='Položka:')
        item_label.SetMinSize((label_width, -1))  # Nastaví pevnou šířku pro popisek
        hbox2.Add(item_label, flag=wx.RIGHT, border=10)
        self.item_textctrl = wx.TextCtrl(panel, size=(250, -1), style=wx.TE_PROCESS_ENTER)
        self.item_textctrl.Bind(wx.EVT_TEXT_ENTER, self.OnPrint)
        hbox2.Add(self.item_textctrl, proportion=1)
        clear_item_btn = wx.Button(panel, label='X', size=(30, 30))
        clear_item_btn.Bind(wx.EVT_BUTTON, lambda evt, temp=self.item_textctrl: self.ClearText(evt, temp))
        hbox2.Add(clear_item_btn, flag=wx.LEFT, border=5)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.ALL, border=10)

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        ptype_label = wx.StaticText(panel, label='P type:')
        ptype_label.SetMinSize((label_width, -1))  # Nastaví pevnou šířku pro popisek
        hbox3.Add(ptype_label, flag=wx.RIGHT, border=10)
        self.ptype_textctrl = wx.TextCtrl(panel, size=(250, -1), style=wx.TE_PROCESS_ENTER)
        self.ptype_textctrl.Bind(wx.EVT_TEXT_ENTER, self.OnPrint)
        
        hbox3.Add(self.ptype_textctrl, proportion=1)
        clear_ptype_btn = wx.Button(panel, label='X', size=(30, 30))
        clear_ptype_btn.Bind(wx.EVT_BUTTON, lambda evt, temp=self.ptype_textctrl: self.ClearText(evt, temp))
        hbox3.Add(clear_ptype_btn, flag=wx.LEFT, border=5)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.ALL, border=10)
        
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        print_button = wx.Button(panel, label='Tisknout štítek')
        print_button.Bind(wx.EVT_BUTTON, self.OnPrint)
        hbox4.Add(print_button, flag=wx.RIGHT, border=10)

        self.btn_settings = wx.Button(panel, label='Nastavení')
        self.btn_settings.Bind(wx.EVT_BUTTON, self.OnSettings)
        hbox4.Add(self.btn_settings)

        clear_all_button = wx.Button(panel, label='Smazat vše')
        clear_all_button.Bind(wx.EVT_BUTTON, self.ClearAllFields)
        hbox4.Add(clear_all_button)

        vbox.Add(hbox4, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)
        
        panel.SetSizer(vbox)

    def save_settings(self):
        settings = {
            'printer_ip': self.printer_ip,
            'printer_port': self.printer_port,
            'remap_keys': self.remap_keys
        }
        with open(self.settings_file_path, 'w') as file:
            json.dump(settings, file, indent=4)

    def load_settings(self):
        try:
            with open(self.settings_file_path, 'r') as file:
                settings = json.load(file)
            self.printer_ip = settings.get('printer_ip', '10.173.0.121')
            self.printer_port = settings.get('printer_port', 9100)
            self.remap_keys = settings.get('remap_keys', True)
        except (FileNotFoundError, json.JSONDecodeError):
            self.printer_ip = "10.173.0.121"
            self.printer_port = 9100
            self.remap_keys = True
    
    def OnSettings(self, event):
        dlg = SettingsDialog(self, "Nastavení", self.printer_ip, self.printer_port, self.remap_keys)
        if dlg.ShowModal() == wx.ID_OK:
            self.printer_ip = dlg.txt_ip.GetValue()
            self.printer_port = int(dlg.txt_port.GetValue())
            self.remap_keys = dlg.chk_remap.IsChecked()
            self.save_settings()
        dlg.Destroy()
    def ClearText(self, event, text_ctrl):
        text_ctrl.SetValue('')
    
    def OnKeyPress(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_RETURN:  # Kód pro klávesu Enter
            self.OnPrint(event)
        else:
            event.Skip()

    def ClearAllFields(self, event):
    # Vymazání obsahu všech textových polí
        self.mrn_textctrl.SetValue('')
        self.item_textctrl.SetValue('')
        self.ptype_textctrl.SetValue('')
        
    def OnPrint(self, event):
        mrn_code = self.mrn_textctrl.GetValue().strip()
        if self.is_qwertz_layout():
            mrn_code = self.remap_string(mrn_code)
        item_text = self.item_textctrl.GetValue().strip()
        p_type = self.ptype_textctrl.GetValue().strip()
        print(item_text,p_type)
        if not mrn_code:
            wx.MessageBox('MRN kód musí být vyplněn', 'Chyba', wx.OK | wx.ICON_ERROR)
        else:
            self.SendToPrinter(mrn_code, item_text, p_type)

    def is_qwertz_layout(self):
        if not self.remap_keys:
            return False
        
        GetKeyboardLayout = ctypes.WinDLL('User32.dll').GetKeyboardLayout
        layout_id = GetKeyboardLayout(0) & 0xffff
        qwertz_layouts = {0x0405, 0x0407, 0x0807, 0x041a, 0x041b, 0x0424, 0x1000, 0x046e, 0x040e}
        return layout_id in qwertz_layouts
    
    def remap_string(self, s):
        translation_table = str.maketrans("+ěščřžýáíéyz+ĚŠČŘŽÝÁÍÉYZqwertuiopasdfghjklxcvbnm","1234567890ZY1234567890ZYQWERTUIOPASDFGHJKLXCVBNM")
        return s.translate(translation_table)
    
    def SendToPrinter(self, mrn_code, item_text, p_type):
        if item_text:

            combined_data = "{}/{}".format(mrn_code,item_text)
        else:
            combined_data = mrn_code

        zpl_data = """
^XA
^BY1,2,50
^FO40,70^BCN,80,N,N
^FH_^FD>:{}>773>6{}>773>6{}^FS
^FO50,160^A0N,20,30^FD{}^FS
^FO300,20^A0N,40,40^FD{}^FS 
^XZ
""".format(mrn_code,item_text,p_type,combined_data,p_type).encode('utf-8')

        print(zpl_data)
        
        printer_ip = self.printer_ip  # Změňte na IP vaší tiskárny
        printer_port = self.printer_port  # Standardní port pro tiskárny Zebra
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((printer_ip, printer_port))
                sock.sendall(zpl_data)
        except Exception as e:
            wx.MessageBox(f'Chyba při odesílání na tiskárnu: {e}', 'Chyba', wx.OK | wx.ICON_ERROR)

def main():
    app = wx.App(False)
    frame = LabelPrinterFrame(None, "Tisk štítků Zebra")
    frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()
