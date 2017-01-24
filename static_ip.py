#!flask/bin/python
from flask import Flask, jsonify, request, abort
import pexpect

app = Flask(__name__)

#---------------------------------------------------------------------------------#
def restart_dhcp():
    child = pexpect.spawn('sudo /etc/init.d/isc-dhcp-server restart')
    t = child.expect(['Restarting', pexpect.EOF, pexpect.TIMEOUT])
    if t == 0 :
       child.sendline('supermen23')
       t = child.expect(['[ok]', pexpect.EOF, pexpect.TIMEOUT])
       if t == 0:
          return True
       else:
          return False
#--------------------------------------------------------------------------------#    
    
    
@app.route('/add/<login>/<MAC>/<IP>')
def add(login,MAC,IP):
    f=open('static_ip.conf','r')
    l = [line.strip() for line in f]
    f.close()
    if 'fixed-address '+IP+';' in l and l.index('fixed-address '+IP+';') != l.index('host '+login+' {')+2 :
	return jsonify({'Error': 'IP is already used'})
    if 'hardware ethernet '+MAC+';' in l and l.index('hardware ethernet '+MAC+';') != l.index('host '+login+' {')+1 :
	return jsonify({'Error': 'MAC is already used'})
    if "host "+login+" {" in l :
       del l[l.index("host "+login+" {"):l.index("host "+login+" {")+4]
       f=open('static_ip.conf','w')
       for index in l:
           f.write(index+'\n')
       f.close()	

    config=open('static_ip.conf','a')
    config.write("host "+login+" {\n hardware ethernet "+MAC+";\n fixed-address "+IP+";\n}\n")
    config.close()

    if restart_dhcp():
      return jsonify({'Added':'ok'}),201
    else:
      return jsonify({'error':"can't restart dhcp"}),500

@app.route('/delete/<login>')
def delete(login):
    f=open('static_ip.conf','r')
    l = [line.strip() for line in f]
    f.close()
    
    if "host "+login+" {" in l:
       del l[l.index("host "+login+" {"):l.index("host "+login+" {")+4]
       f=open('static_ip.conf','w')
       for index in l:
           f.write(index+'\n')
       f.close()
    else:
       return jsonify({"error":"Not found"}),404
    if restart_dhcp():
       return jsonify({"status":"deleted"}),200
    else:
       return jsonify({"error":"can't restart dhcp"}),500
   

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1992, debug=True)
