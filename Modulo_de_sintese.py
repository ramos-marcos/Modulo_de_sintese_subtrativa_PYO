import serial
import time
from pyo import * # Iporta o módulo PYO

#----------------Bloco responsável por estabelecer a comunicação serial--------------------------

list = ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'COM10', 'COM11', 'COM12', 'COM13', 'COM14', 'COM15', 'COM16', 'COM17', 'COM18', ]

COM1 = 'COM1'
COM2 = 'COM2'
COM3 = 'COM3'
COM4 = 'COM4'
COM5 = 'COM5'
COM6 = 'COM6'
COM7 = 'COM7'
COM8 = 'COM8'
COM9 = 'COM9'
COM10 = 'COM10'
COM11 = 'COM11'
COM12 = 'COM12'
COM13 = 'COM13'
COM14 = 'COM14'
COM15 = 'COM15'
COM16 = 'COM16'
COM17 = 'COM17'
COM18 = 'COM18'
COM19 = 'COM19'
time.sleep(1)
ser = serial.Serial()

ser.baudrate = 9600

j = 1

while True:
    time.sleep(.2)
    print(j)
    ser.port = list[j]
    try:

        ser.open()
        if ser.isOpen() == True:
            print('Conectado')
            break
        break

    except:
        print('Aguarde')
        j = j+1
        if j == 18:
            print('Remova o cabo USB e tente novamente')
            break


#--------------------Inicialização do servidor------------------------------------

s = Server(duplex=0)
s.boot()
s.start()

#---------------------LFO---------------------------------------

lfoFreq = Sig(value=0)    # Cria um sinal para receber valores dos botões da interface
lfoSharp = Sig(value=0.5) # Cria um sinal para receber valores dos botões da interface
lfoType = 0               # Define a forma de onda inicial do LFO
lfoMul = Sig(value=0)     # Cria um sinal para receber valores dos botões da interface


lfo =  LFO(freq=lfoFreq, sharp=lfoSharp, type=lfoType, mul=lfoMul) # Inicializa o LFO

#-------------------OSCILADORES---------------------------------

# Sinal que modifica a frequência dos osciladores a partir dos dados do sensor
fr = Sig(value=0)

# Portamento para suavizar as transições nas mudanças de frequência
p = Port(fr, risetime=0.035, falltime=0.035)

osc1Mul = Sig(value=0.5)  # Cria um sinal para receber valores dos botões da interface para controle de volume do oscilador 1
osc2Mul = Sig(value=0.5)  # Cria um sinal para receber valores dos botões da interface para controle de volume do oscilador 2

# Inicialização dos osciladores 1 e 2
osc1 = LFO(freq=[p], sharp=lfo, mul=osc1Mul)
osc2 = LFO(freq=[p], sharp=lfo, mul=osc2Mul)

#-----------------GERADORES DE RUÍDO----------------------------

# Inicialização dos geradores de ruído
n1 = Noise(0.3)
n2 = PinkNoise(0.3)
n3 = BrownNoise(0.3)

noiseMul = Sig(value=0)    # Cria um sinal para receber valores dos botões da interface para controle de volume do gerador de ruído (0 à 1)
noiseVoice = Sig(value=0)  # Cria um sinal para receber valores dos botões da interface para modificar o tipo de ruído (0, 1 ou 2)

#Inicialização do seletor de ruído
sel = Selector([n1, n2, n3], voice=noiseVoice, mul=noiseMul)

#----------------------FILTROS----------------------------------

filResonance = Sig(value=0) # Cria um sinal para receber valores dos botões da interface para controle do nível de ressonância (0 à 1)
filFreq = Sig(value=20000)  # Cria um sinal para receber valores dos botões da interface para ajuste da frequência de corte (0 à 20000)

fil = MoogLP([osc1,osc2,sel],freq=filFreq, res=filResonance) #Inicializa o filtro passa baixas

#---------------------PRÉ-AMPLIFICADOR---------------------------

fa = Sig(value=0) # Sinal que modifica a amplitude do sinal a partir dos dados do sensor de amplitude (0 à 1)
pa = Port(fa, risetime=0.035, falltime=0.035) # Portamento para suavizar as transições nas mudanças de amplitude
Pre_Mix = Mix([fil], voices=2, mul=pa) #Inicialização do mixer responsável por receber os sinais dos osciladores e modificar sua amplitude 

#-------------------------DELAY----------------------------------

delayTime = Sig(value=0)     # Cria um sinal para receber valores dos botões da interface para controle do tempo do efeito de delay
delayFeedback = Sig(value=0) # Cria um sinal para receber valores dos botões da interface para controle do feedback do efeito de delay
delayMul = Sig(value=0)      # Cria um sinal para receber valores dos botões da interface para controle da amplitude do efeito de delay

d = Delay([Pre_Mix,Pre_Mix], delay=[delayTime,delayTime], feedback=delayFeedback, mul=delayMul) # Inicialização do efeito de delay

#------------------------AMPLIFICADOR----------------------------


L = Mix([d,Pre_Mix], voices=2, mul=1).out(0) # Mixer responsável por enviar sinal à saída de áudio esquerda
R = Mix([d,Pre_Mix], voices=2, mul=1).out(1) # Mixer responsável por enviar sinal à saída de áudio direita

while 1:
            time.sleep(0.0001)
            b = ser.readline()     # Lê uma string de byte
            string_n = b.decode()  # Decodifica string de byte em Unicode  
            
            string = string_n.rstrip() # Remove \n e \r

            string_1 = string.split('/')[0] # Captura a primeira parte da string até encontrar a barra
            string_2 = string.split('/')[1] # Captura a segubda parte da string depois da barra

            i = float(string_1) # Converte os caracteres da string em float e atribui a variável i

            flt_2 = float(string_2) # Converte os caracteres da string em float e atribui a variável flt_2

            if i!=-1:                     # Verifica se o valor obtido pelo sensor de frequência é válido
                flt_1 = (110*(2**(i/12))) # Aplica o valor de i obtido a partir do sensor de frequência na expressão, 
                                          # calcula a frequência correspondente e atribui a variável flt_1
                flt_1 = round(flt_1,2)    # Arredonda o valor de frequência obtido para um float de duas casas decimais
                fr.value = flt_1          # Aplica a frequência obtida ao sinal fr que controla a frequência dos osciladores
            else:
                 fr.value = 0             # Se i não é um valo válido atribui-se 0 ao sinal que controla a frequencia



            if flt_2!=0:                  # Verifica se o valor obtido pelo sensor de amplitude é válido
                fa.value = flt_2*0.01     # Converte o valor lido pelo sensor de amplitude par o intervalo de 0 à 1,
                                          # e aplica o valor obtido ao sinal fa que controla a amplitude do sinal
                Pre_Mix.mul=pa            # Aplica o sinal pa, obtido a partir do portamento em que fa é aplicado ao Pre_Mix 
                                          # que controla a amplitude do sinal 
                                               
            else:                         # Se flt_2  não é um valor válido
                fa.value = 0              # Atribui-se 0 ao sinal que contraola a amplitude
                Pre_Mix.mul=pa

