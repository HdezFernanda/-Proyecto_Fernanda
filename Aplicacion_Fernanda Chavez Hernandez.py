from netmiko import ConnectHandler #netmiko para haver conexion de los dispositivos 
import re#importamos la libreria de las expreciones regulares
ippatron = r"\d{1,4}\.\d{1,4}\.\d{1,4}\.\d{1,4}"# PATRON DE UNA IP ejemplo :192.168.0.1
# r=exprecion regular  {}=rangos de dijitos o letras \d=dijitos
macpatron = r"[a-f0-9]{2}.[a-f0-9]{2}.[a-f0-9]{2}.[a-f0-9]{2}.[a-f0-9]{2}.[a-f0-9]{2}"#Patron de la mac add   cuadno vienen separados de 2 en 2 
# .(solo)=lo que sea
macpatron2 = r"[a-f0-9]+.[a-f0-9]+.[a-f0-9]+.[a-f0-9]+"#Patron cisco, es para la mac add (cuadno viene de 4 en 4)
interfLocal=r"Interface:\s*(.),(.):\s*(.*)"#Sacar interfaz local por donde la ve el switch core
groups_macT=r"\s*?(\d)\s+([a-f0-9]+\.[a-f0-9]+\.[a-f0-9]+)\s+(\w+)\s+((Fa|Gi)\d{1,2}\/\d{1,2}\/?(\d{1,2})?)"#checar que este ben la mac y el format
#\s=espacio  LEER TODA LA LINEA QUE NOS MANDA EL COMANDO SH MAC ADD TABLE | MAC \W=cualquier letra que puede tener uno o mas dijitos, numeros 
                         #COMPRUEBA EL FORMATO DE IP Core 
def ComFormat(variable,patron):       #esta entra cuando ponemos la ip del core
    forma = re.compile(patron)        #La compara con la exprecion regular ippatron
    comprobar = forma.search(variable)#busca el formato correcto en la variable con forme al patron 
    if comprobar == None:
        print("!!............Error, Intenta de nuevo............!!")
        return comprobar
    else:
        print(".-.-.-.-..-¡¡C O I N C I D E !!.-.-.-.-.")# coincide la ip
        return comprobar.group()
   #COMANDOS 
shmac = "show mac address-table | in "             #comando para ver la tabla de MAC add
shcdpn = "show cdp neighbors detail"               #Ver los detalles de los vecinos, como la IP
shhostN = "show running-config | include hostname"  #Sacar el nombre del dispositivo donde se encuentra la Mac    

#encontrar mac 
def encontrar_Mac(mac,connect): #Esta funcion es la encargada de buscar y encontrar la MAC
    MACtabla = connect.send_command(shmac + mac)   #Sabemos por donde es que se encuentra esta mac 
   
    forma=re.compile(groups_macT)      # Se encarga de comparar la mac con la que estamos buscando de gurpo 4 de arriba
    comprobar = forma.search(MACtabla) #Traer la mac si es que es la correcta
    if comprobar != None:
        port = comprobar.group(4)      #solo lo compara en el grupo 4 por que solo le interesas el puerto
        print("----La mac es visible por el puerto------: ",port)# En que puerto se encuentra la mac
        print("")
    else:
        print("!!............ La MAC que tecleaste No existe en la red..............!!")#Si no se encuentra el puerto imprime
        #CDPneighborsDetail= Sacar la ip de los vecinos
    CDPneig= connect.send_command(shcdpn) #No sdice que dispositivos estan conectados a los vecinos
    #CDPneig_list = CDPneig.split('\n')         #Crea la lista de los vecinos que estan conectafdos(Todos los switches)

#Comprobacion de las ip de los vecinos 
    Todaip = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",CDPneig) #Encuentra todas lsa ip por medio de una exprecion regular y 
          #las guarda en formato de lista 

    IPs = []#Guarda las IPs  a las que se conecto para llegar a la MAC
    print("1.",IPs)
    [IPs.append(i) for i in Todaip if i not in IPs]#Eliminamos las ip que estan repetidas 

    print(IPs, "aqui no hay ips duplicadas")#las imprime

#Guuarde las interfaces locales de los dispositivos que estan conectados al core
    INterfaz =re.findall(r"Interface:\s+[a-zA-Z]*\d+\/\d+\/?\d+",CDPneig)#Encuentra todas la interf. locales y las guarda en formato de lista
    i=0
    #Verificasar el frmato correcto de las interfaces 
    for element in INterfaz: #Por cada elemento de la interfas     
        forma=re.compile(r"(Fa|Gi)[a-zA-Z]*([0-9]+\/[0-9]+\/?[0-9?]+)")#Comprueba con la exprecion si es Fa|Gi 
         #= 0 o mas de 0   ()=grupos  +=1 o mas de 1  
        comprobar=forma.search(element)#Compreueba si el formato esta en el elemento 
        INterfaz[i]=comprobar.group(1)+comprobar.group(2)# Si esta, compara con grupo 1 y 2 
        i+=1#Acomulalas

#Verificar si el puerto essta en la lista de interfas saca la ip para conetcarnos al siguiente dospositivo
    if port in INterfaz:      # Si el puerto en la interfaz
        posicion=INterfaz.index(port)#Que muestra la posicion del puerto
        ip=IPs[posicion]
        Device={
            "host":ip,#Ip que saca de los vecinos
            "username":"cisco",#usuario
            "device_type":"cisco_ios",#tipo de dispositivo
            "secret":"cisco", #contraseña
            "password":"cisco",#contraseña
            }
        
        try:
            connection = ConnectHandler(**Device)# Podernos conectar al dispositivo
            connection.enable() #Lo permte
        except:
            print("!!..............C O N E X I ó N    N U L A  .................!!")#Si no se puede conectar

        encontrar_Mac(mac, connection)#Se manda llamar la funcion "Encontrar mac"
         
    else:
        Hostname = connect.send_command(shhostN)#Saber nombre del dispositivo donde se encuentra la MAC
        forma=re.compile(r"hostname (.*)")# Verifica el forato con la exprecion "hostname " 
        comprobar=forma.search(Hostname)#LO comprueba buscandolo
        print("")
        print("-.-.-.-..-..-..-LA MAC ESTA CONECTADA EN EL ",comprobar.group(1), "Y SU PERTO ES:",port,"-.-.-.-.-.-.-.-.-.-.")#Lo imprime

        return None
while True:
    print("")
    print("____________________________________________")
    print("1. Seguir ejecutando el programa")
    print("2.Salir")
    print("____________________________________________")
    op=input("Elije una de las opciones:")
    if op=="1":
        while True:
            print("--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.-")
            ip = input("IP CORE:") #192.168.0.1
            print("--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.--.-")
            print("")
            if ComFormat(ip,ippatron) != None:#manda llamar la funcion "comprobar formato"
                # comprueba la ip si es correcta pide usuario y contraseña
                user = input("--Usuario--:")
                passw = input("--Contraseña--:")
              #Pero si no
            else:
                print("!!..............IP INGRESADA ES ERRONEA.................!!")
                break

                #DICCIONARIO PARA CONECTARNOS AL SWITCH  C O R E #
            Device={
                    "host":ip, #192.168.0.1
                    "username":user,#cisco
                    "device_type":"cisco_ios", #TIP DE DISPOSITIVO (Sistema operativo Cisco)
                 "secret":passw, #cisco
                        "password":passw,#cisco
                }
            try:
                net_connect = ConnectHandler(**Device)# hace su coneccion
                net_connect.enable()#compreta la conexion
            except:#pero si no
                print("!!............NO SE LOGRO LA CONEXIÓN.................!!")
                break
                #Si se logra la conexion
          
            print("-.-.-.-.-.-.-.-.¡¡¡¡¡¡-SE LOGRO LA CONEXIÓN-!!!!.-.-.-.-.-.-.-.-")
    
            mac_buscada = input("Teclea la MAC a encontrar:").lower()
            mac_buscada = ComFormat(mac_buscada,macpatron)#Comprobar el formato de la MAC

            if mac_buscada != None:
                #Si la mac biene con "-", ".", ":" , se los quita y les pone un punto en la posicion 4y 9
             mac_buscada = mac_buscada.replace("-","") 
             mac_buscada= mac_buscada.replace(".","")
             mac_buscada= mac_buscada.replace(":","")
             mac_buscada = list(mac_buscada)
             mac_buscada.insert(4,".")
             mac_buscada.insert(9,".")
             mac_buscada = "".join(mac_buscada) #Junta toda la mac 
             print(mac_buscada)#Imprime la mac 
             fin = encontrar_Mac(mac_buscada, net_connect)#Manda llamar la funcion encontrar MAC junto con la mac buscada y los compara y conecta
            if fin == None:#Si no coincide 
             break
            else:
                print("!!.......... M A C    I N C O R R E C T A ............!!")#imprime
            pass
    elif op=="2":
        print("Saliendo....")
        exit() 