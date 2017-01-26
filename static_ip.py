#!flask/bin/python
from flask import Flask, jsonify
import  os
from jinja2 import Template


app = Flask(__name__)

template_conf = Template(u"""
host {{login}}
{
hardware ethernet {{MAC}};
fixed-address {{IP}};
}

""")



@app.route('/add/<login>/<MAC>/<IP>')
def add(login,MAC,IP):
    open_config()
    for i in range(0,len(parameters)) :
	if IP in parameters[i][2] and parameters[i][0] != login :
	    host_IP = parameters[i][0]
            return response("error","IP is already used by "+host_IP)
	    
        elif MAC in parameters[i][1] and parameters[i][0] != login :
            host_MAC = parameters[i][0]
            return response("error","MAC is already used by "+host_MAC)
    
    for i in range(0,len(config)) :
        if config[i]["login"] == login :
	    del config[i]
            
    config.append({"login":login,"MAC":MAC,"IP":IP})
  
    with open('static_ip.conf','w') as f:
        for i in range(0,len(config)):
            f.write(template_conf.render(config[i]))

    if restart_dhcp():
        return response("succsess","added")
        
    else :
        return response("error","can't restart dhcp")
        



@app.route('/delete/<login>')
def delete(login):
    open_config()
    for i in range(0,len(config)) :
        if config[i]["login"] == login :
	    del config[i]
            with open('static_ip.conf','w') as f:
                for i in range(0,len(config)):
                    f.write(template_conf.render(config[i]))

            if restart_dhcp():
               return response("success","deleted")
              
            else :
               return response("error","can't restart dhcp")
               
    return response("error","not found login in config")
    

@app.route('/show/<login>')
def show(login) :
    open_config()
    if login != "all" :
       for i in range(0,len(config)) :
           if config[i]["login"] == login :
               return response("success",login+" config",config[i])
               
       return response("error","not found login in config")
    else :
       return response("success","all config",config)
       
    
      

def open_config():
    global config, parameters
    parameters = []
    config = []
    with open('static_ip.conf','r') as l:
	l = [line.strip() for line in l]	
	for i in range(0,len(l),6):
            parameters.append([l[i+1].split()[1],l[i+3].split()[2].replace(";",""),l[i+4].split()[1].replace(";","")])
        for i in range(0,len(parameters)) :
            config.append({"login":parameters[i][0] , "MAC":parameters[i][1] , "IP":parameters[i][2]})


def restart_dhcp():
    returncode = os.system('/etc/init.d/isc-dhcp-server restart')
    if returncode == 0:
       return True
    else :
       return False

def response(stat,mass,dat=None) :
    if dat == None :
        response = jsonify(stastus=stat,massage=mass)
    else :
        response = jsonify(stastus=stat,massage=mass,data=dat)
    return (response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1992, debug=True)
