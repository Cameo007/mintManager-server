import socket, os, subprocess, json, re, time

def checkCmd(text, user, group):
    with open("./permissions.json", "r") as file:
        expressions = json.load(file)[user][group]
    for expression in expressions:
        match = re.match(expression, text)
        if match:
            match = match.group(0)
            if match in text:
                return True

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 50000)) 
s.listen(1)
        
try:
    while True: 
        komm, addr = s.accept()
        data = komm.recv(1024)
        if not data: 
            komm.close()
            break
        cmd = data.decode()
        while True:
            if not "<end>" in cmd:
                cmd += komm.recv(4096).decode()
            else:
                cmd = cmd.replace("<end>", "").rstrip()
                break

        usernamesForTokens = {}
        passwords = []

        #New version
        with open("./tokens.json", "r") as file:
            tokens = json.load(file)
            for token in tokens:
                if int(time.time()) - token["time"] > 900:
                    tokens.remove(token)
                else:
                    passwords.append(token["token"])
                    usernamesForTokens[token["token"]] = token["username"]
        with open("/var/www/mintManager/tokens.json", "w") as file:
            json.dump(tokens, file)

        user = ""
        error = True

        for password in passwords:
            cmd2 = f'./jasypt-1.9.3/bin/decrypt.sh input="{cmd}" password="{password}" algorithm="PBEwithMD5andDES" keyObtentionIterations=1000 verbose=false'
            cmd2 = subprocess.check_output(cmd2, shell=True).decode()
            if cmd2 != "":
                cmd = cmd2
                user = usernamesForTokens[password]
                error = False
                break

        if not error:
            try:
                if cmd.startswith("xmpp "):
                    cmd = cmd.replace("xmpp", "/opt/ejabberd-22.05/bin/ejabberdctl")
                    if checkCmd(cmd, user, "xmpp"):
                        result = subprocess.check_output(cmd, shell=True).decode()
                    else:
                        result = "Befehlsausführung verboten: " + cmd
                elif "bot" in cmd:
                    if "bot start" in cmd:
                        cmd = "/usr/bin/python3 /home/pasca/Bot/bot.py &"
                        if checkCmd(cmd, user, "xmpp"):
                            subprocess.Popen(cmd, shell=True)
                            result = "OK"
                        else:
                            result = "Befehlsausführung verboten: " + cmd
                    elif "bot stop" in cmd:
                        cmd = "pkill -9 -f bot.py"
                        if checkCmd(cmd, user, "xmpp"):
                            result = subprocess.check_output(cmd, shell=True).decode()
                            if not result:
                                result = "OK"
                        else:
                            result = "Befehlsausführung verboten: " + cmd
                elif "webserver" in cmd:
                    if "webserver start" in cmd:
                        cmd = "service apache2 start"
                        if checkCmd(cmd, user, "webserver"):
                            result = subprocess.check_output(cmd, shell=True).decode()
                            result = "OK"
                        else:
                            result = "Befehlsausführung verboten: " + cmd
                    elif "webserver stop" in cmd:
                        cmd = "service apache2 stop"
                        if checkCmd(cmd, user, "webserver"):
                            result = subprocess.check_output(cmd, shell=True).decode()
                            result = "OK"
                        else:
                            result = "Befehlsausführung verboten: " + cmd
                    else:
                        cmd = cmd.replace("webserver", "apachectl")
                        if checkCmd(cmd, user, "webserver"):
                            result = subprocess.check_output(cmd, shell=True).decode()
                        else:
                            result = "Befehlsausführung verboten: " + cmd
                elif cmd.startswith("adblocker "):
                    cmd = cmd.replace("adblocker", "pihole")
                    if checkCmd(cmd, user, "adblocker"):
                        result = subprocess.check_output(cmd, shell=True).decode()
                    else:
                        result = "Befehlsausführung verboten: " + cmd
                elif "system" in cmd:
                    if "system-manager start" in cmd:
                        cmd = "systemctl start ajenti"
                        if checkCmd(cmd, user, "system"):
                            result = subprocess.check_output(cmd, shell=True).decode()
                            result = "OK"
                        else:
                            result = "Befehlsausführung verboten: " + cmd
                    elif "system-manager stop" in cmd:
                        cmd = "systemctl stop ajenti"
                        if checkCmd(cmd, user, "system"):
                            result = subprocess.check_output(cmd, shell=True).decode()
                            result = "OK"
                        else:
                            result = "Befehlsausführung verboten: " + cmd
                    elif "system-manager restart" in cmd:
                        cmd = "systemctl restart ajenti"
                        if checkCmd(cmd, user, "system"):
                            result = subprocess.check_output(cmd, shell=True).decode()
                            result = "OK"
                        else:
                            result = "Befehlsausführung verboten: " + cmd
                    elif "system restart" in cmd:
                        cmd = "reboot"
                        if checkCmd(cmd, user, "system"):
                            result = subprocess.check_output(cmd, shell=True).decode()
                            result = "OK"
                        else:
                            result = "Befehlsausführung verboten: " + cmd
                    elif "system stop" in cmd:
                        cmd = "shutdown -h now"
                        if checkCmd(cmd, user, "system"):
                            result = subprocess.check_output(cmd, shell=True).decode()
                            result = "OK"
                        else:
                            result = "Befehlsausführung verboten: " + cmd
                else:
                    result = "Befehlsausführung verboten: " + cmd
            except Exception as e:
                result = str(e)
        else:
            result = "ERROR: Session"
        
        if not result:
            result = "OK"
        
        komm.send(result.replace("\n", "\\n").encode("utf-8"))
        komm.close()
finally: 
    s.close()
