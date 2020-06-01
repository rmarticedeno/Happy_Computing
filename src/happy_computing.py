import random
import math
import queue 

MAX = 960

def exponential(lmda):
    val = random.random()
    return -1/lmda * (math.log(val))

def normal01():
    y = 0
    while True:
        y1 = exponential(1)
        y2 = exponential(2)
        y = y2 - (y1 - 1)**2/2
        if y > 0:
            break
    u = random.random()
    return y if u <= 1/2 else -1 * y 

def normal(miu, ro):
    return normal01() * math.sqrt(ro) + miu

def generate_client_type():
    u = random.random()
    if u <= 0.45:
        return 1
    elif 0.45 < u <= 0.7:
        return 2
    elif 0.7 < u <= 0.9:
        return 4
    return 3

attender_type = {1:'tec', 2:'tec', 3:'stec', 4:'none'}

def generate_client(t, lmda=1/20):
    return t - 1/lmda*(math.log(random.random()))   

def generate_vendor_time(miu=10, ro=5):
    return abs(normal(miu,ro))

def generate_tec_time(lmbda=1/20):
    return exponential(lmbda)


class Client:
    def __init__(self, number = -1, arrival = MAX):
        self.arrival = arrival
        self.id = number
        self.vendor_waiting_time = 0
        self.stec_waiting_time = 0
        self.tec_waiting_time = 0
        self.vendor_end_time = 0
        self.tec_end_time = 0
        self.finish_time = 0
        self.vendor_id = 0
        self.tec_id = 0
        self.type = generate_client_type()
        self.expenses = 0

    def __eq__(self, other):
        return max(self.arrival,self.vendor_end_time,self.tec_end_time) == max(other.arrival, other.vendor_end_time, other.tec_end_time)
    def __ne__(self, other):
        return not self.__eq__(other)
    def __lt__(self, other):
        return max(self.arrival,self.vendor_end_time,self.tec_end_time) < max(other.arrival, other.vendor_end_time, other.tec_end_time)
    def __ge__(self, other):
        return not self.__lt__(other)
    def __gt__(self, other):
        return max(self.arrival,self.vendor_end_time,self.tec_end_time) > max(other.arrival, other.vendor_end_time, other.tec_end_time)
    def __le__(self, other):
        return not self.__gt__(other)



class HappyComputing:
    def __init__(self, uptime=480, vendors=2, tec=3, stec=1, arrival_lambda = 1/20 ,vendor_lambda = (5,2), tec_lambda = 1/20, stec_lambda = 1/15, infinite=None):
        self.arrival_list = []
        self.vendor_list = []
        self.tec_list = []
        self.stec_list = []
        self.visitors_list = []
        self.vendor_number = vendors
        self.tec_number = tec
        self.stec_number = stec
        self.system_time = 0

        self.T = uptime
        self.MAX = 2*self.T if infinite is None else infinite

        self.SS = []
        

    def simulate(self):
        self.SS = [Client()]*(self.vendor_number + self.tec_number + self.stec_number + 1)

        t = 0
        i = 1
        while(t < self.T):
            t = generate_client(t)
            self.arrival_list.append(Client(i, t))
            i+=1
        
        self.SS[0].append(self.arrival_list.pop(0))

        self._simulate()

    def _simulate(self):
        while(len(self.arrival_list) + len(self.tec_list) + len(self.stec_list)):
            arriv = self.SS[0]
            m_vendors = min(self.SS[1:self.vendor_number + 1])
            m_tec = min(self.SS[self.vendor_number + 1: self.vendor_number + self.tec_number + 1])
            m_stec = min(self.SS[self.vendor_number + self.tec_number + 1:])

            m_min = min(self.SS)

            if arriv == m_min:
                self.system_time = arriv.arrival
                choice = self.find_free_attender('vendor')
                arriv.vendor_id = choice
                arriv.vendor_end_time = self.system_time + generate_vendor_time()
                self.SS[choice] = arriv

                self.SS[0] = self.arrival_list.pop(0)

            elif m_vendors == m_min:
                self.system_time = m_vendors.vendor_end_time

                if m_vendors.type == 4:
                    m_vendors.finish_time = self.system_time
                    #compra de equipo
                    self.visitors_list.append(m_vendors)
                else:
                    choice = self.find_free_attender(attender_type[m_vendors.type])

                    if choice:
                        m_vendors.tec_id = choice
                        m_vendors.tec_end_time = self.system_time + generate_tec_time()
                        self.SS[m_vendors] = m_vendors
                    else:
                        if attender_type[m_vendors.type] == 'tec':
                            # reparacion tipo 1 o 2
                            self.tec_list.append(m_vendors)
                        else:
                            # cambio de equipo
                            self.stec_list.append(m_vendors)

                freeone = m_vendors.vendor_id

                if len(self.vendor_list):
                    newone = self.vendor_list.pop(0)
                    newone.vendor_waiting_time = self.system_time - newone.arrival
                    self.SS[freeone] = newone
                
                
            elif m_tec == m_min:
                self.system_time = m_tec.tec_end_time
                m_tec.finish_time = self.system_time

                freeone = m_tec.tec_id

                self.visitors_list.append(m_tec)

                if len(self.tec_list):
                    nextone = self.tec_list.pop(0)
                    nextone.tec_id = freeone
                    nextone.tec_waiting_time = self.system_time - nextone.vendor_end_time
                    self.SS[freeone] = nextone


            elif m_stec == m_min:
                self.system_time = m_stec.tec_end_time
                m_stec.finish_time = self.system_time

                freeone = m_stec.tec_id

                self.visitors_list.append(m_stec)

                if len(self.stec_list) or len(self.tec_list):
                    nextone = self.stec_list.pop(0) if len(self.stec_list) else self.tec_list.pop(0)
                    nextone.tec_id = freeone
                    nextone.tec_waiting_time = self.system_time - nextone.vendor_end_time
                    self.SS[freeone] = nextone

            else:
                print("anomalous exit")
                break
    
    def find_free_attender(self, a_type):
        choices = []
        if a_type == 'vendor':
            choices = self.SS[1:self.vendor_number+1]
        # todo aquel que requiera el servicio de un tecnico puede ser atendido por el especializado o no
        elif a_type == 'tec':
            choices = self.SS[self.vendor_number+1:]
        elif a_type == 'stec':
            choices = self.SS[self.vendor_number + self.tec_number + 1:]
        else:
            print('bad call')
            return 0
        
        candidates = []
        for i in range(0,len(choices)):
            if choices[i] == Client():
                if a_type == 'vendor':
                    candidates.append(i + 1)
                elif a_type == 'tec':
                    candidates.append(i + self.vendor_number + 1)
                else:
                    candidates.append(i + self.vendor_number + self.tec_number + 1)
        
        if len(candidates):
            return random.choice(candidates)
        return 0