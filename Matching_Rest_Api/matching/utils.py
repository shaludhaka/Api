from collections import OrderedDict
from fuzzy import *
from Levenshtein import *
from django.http import HttpResponse
from rest_framework.response import Response
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PatternMatch:

        def __init__(self,data):
            self.name1 = OrderedDict()
            self.name2 = OrderedDict()
            self.name1["firstname"] = str(data['FirstFirstName']).lower()
            self.name1["middlename"] = str(data['FirstMiddleName']).lower()
            self.name1["lastname"] =str(data['FirstLastName']).lower()
            self.name2["firstname"] = str(data['SecondFirstName']).lower()
            self.name2["middlename"] = str(data['SecondMiddleName']).lower()
            self.name2["lastname"] = str(data['SecondLastName']).lower()


        def extract_values(self):
            self.output=OrderedDict()
            print self.name1["firstname"]
            print self.name1["middlename"]
            print self.name1["lastname"]
            print self.name2["firstname"]
            print self.name2["middlename"]
            print self.name2["lastname"]
            logger.info("Got the names to match")



            if not (filter(lambda k: k if k != '' else None, self.name1.values()) and filter(
                    lambda k: k if k != '' else None, self.name2.values())):
                self.output["verdict"] = "NA"
                self.output["confidence_score"]="NA"
                self.output["comment"]="Start by entering both strings"
                logger.warn("Enter both the names to match")

	 
            elif not self.name1["middlename"]  and not self.name1["lastname"] and not self.name2["middlename"]  and not self.name2[
                "lastname"]  \
                    and self.name1['firstname']  and self.name2['firstname']:

                self.output = self.mix_match(self.name1["firstname"], self.name2["firstname"],self.output,nametype="firstnames")
                logger.info("only first names found")

            elif self.name1["middlename"]  and not self.name1["lastname"] and self.name2["middlename"]  and not self.name2[
                "lastname"]  \
                    and not self.name1['firstname']  and not self.name2['firstname']:
                
                self.output = self.mix_match(self.name1["middlename"], self.name2["middlename"],self.output,nametype="middlenames")
                logger.info("only middle names found")


            elif not self.name1["middlename"]  and  self.name1["lastname"] and not self.name2["middlename"]  and self.name2[
                "lastname"]  \
                    and not self.name1['firstname']  and not self.name2['firstname']:

                self.output = self.mix_match(self.name1["lastname"], self.name2["lastname"],self.output,nametype="lastnames")
                logger.info("only last names found")


            elif self.name1["firstname"]  and self.name2["firstname"]  and self.name1["lastname"] \
                and self.name2["lastname"]  and self.name1[ "middlename"]!=self.name2["middlename"]  \
                and self.sound_match(self.name1["firstname"],self.name2["firstname"]) and self.sound_match(self.name1["lastname"],self.name2["lastname"]) \
                and self.calculate_pct(self.name1["firstname"],self.name2["firstname"])>=75 and self.calculate_pct(self.name1["lastname"],self.name2["lastname"])>=75:
                print("------------------------")
                self.output["verdict"] = "approx match"
                self.output["comment"] = "Names match except middlename"
                mid_pct = self.calculate_pct(self.name1["middlename"], self.name2["middlename"])
                score = (self.calculate_pct(self.name1["firstname"],self.name2["firstname"]) + self.calculate_pct(self.name1["lastname"],self.name2["lastname"]) + mid_pct) / float(3)
                self.output["confidence_score"] = score
                logger.info("middle names match")


            else:
                print("++++++++++++++")
                self.output= self.match(self.name1, self.name2,self.output)
                logger.info("complete names found")


            return Response(self.output)

        def mix_match(self,name1, name2,output,nametype):
            first_list = name1.split()
            second_list = name2.split()
            if len(first_list) > len(second_list):
                first_list, second_list = second_list, first_list
            pct_list = []
            for name1 in first_list:
                for name2 in second_list:
                    pct = self.calculate_pct(name1, name2)
                    pct_list.append(pct)
                    logging.info("the fuzzy %% matching is %d"%(pct))

            array = np.resize(pct_list,(len(first_list),len(second_list)))

            pct_values = []
            empty_list=[]
            for i in range(len(pct_list) / len(second_list)):
                max_val=array.max()
                r = np.argwhere(array==max_val)[0][0]
                c = np.argwhere(array==max_val)[0][1]
                empty_list.append((array.max(), r, c))
                for j in range(array.shape[0]):
                    for k in range(array.shape[1]):
                        if j == r or k == c:
                            array[j][k] = 0
            for val in empty_list:
                pct_values.append(val[0])
            logger.info("the list of pct values are  "+" ".join(str(val) for val in pct_values))

            score=sum(pct_values)/float(len(pct_values))
            if (all(val >= 75 for val in pct_values)):
                if self.sound_match(first_list, second_list):
                    if (all(val == 100 for val in pct_values) and len(first_list)==len(second_list)):
                        output["verdict"]="exact match"
                    else:
                        output["verdict"]="approx match"
                    output["confidence_score"]=score
                    output["comment"]="{} match ".format(nametype)
                    return output
                else:
                    output["verdict"] = "No match"
                    output["confidence_score"] = score
                    output["comment"] = "{} don't match due to sound mismatch ".format(nametype)
                    return output

            else:
                if self.sound_match(first_list, second_list):
                    output["verdict"] = "No match"
                    output["confidence_score"] = score
                    output["comment"] = "{} matches phonetically but distance mismatch ".format(nametype)
                    return output
                output["verdict"] = "No match"
                output["confidence_score"] = score
                output["comment"]="{} don't match ".format(nametype)
                return output

        def match(self,name1, name2,output):
            complete_name1 = ' '.join(v for k, v in name1.items())
            complete_name2 = ' '.join(v for k, v in name2.items())
            print(complete_name1)
            print(complete_name2)
            if name1["firstname"] == name2["firstname"] and name1["middlename"] == name2["middlename"] and name1[
                "lastname"] == name2["lastname"]:
                output["verdict"]="exact match"
                output["confidence_score"]=100
                output["comment"]="Names are exactly equal"
                return output
            else:
                return self.mix_match(complete_name1, complete_name2,output,nametype="names")

        def sound_match(self,name1, name2):
            sound = Soundex(4)
            status_sound = []
            if not isinstance(name1,list) and not isinstance(name2,list):
                return sound(name1)==sound(name2)
            for val1 in name1:
                for val2 in name2:
                    if sound(val1) == sound(val2):
                        status_sound.append(True)
                        break
            if len(status_sound) == len(name1):
                return True
            else:
                return False

        def calculate_pct(self,name1, name2):
            dist = distance(name1, name2)
            tot_length = len(name1) + len(name2)
            pct = (1 - (dist / float(tot_length))) * 100
            print pct
            return round(pct,2)




