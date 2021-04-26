from lirc import RawConnection

class Infrared_remote:
    def __init__(self):
        self.conn = RawConnection()
    def read(self):
        try:
            keypress = self.conn.readline(.0001)
        except:
            keypress=""
                  
        if (keypress != "" and keypress != None):
                    
            data = keypress.split()
            sequence = data[1]
            command = data[2]
            
            #ignore command repeats
            if (sequence != "00"):
               return
            
            return command
        else:
            return ''
            

