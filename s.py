from collections import Counter
from typing import List

class Solution:
    def countWords(self, words1: List[str], words2: List[str]) -> int:
        counter1 = Counter(words1)
        print(counter1)
        counter2 = Counter(words2)
        print(counter2)
        return sum(1 for word in counter1 if counter1[word] == 1 and counter2[word] == 1)


words1 = ["bjxzvssdoq","oom","lxrrvf","aoeselhvrnw","awnornqyztqlza","bjxqkapuvaw","wibxruerngdzgjd","rezrwdzvllpbjpnikhzraz","pswmnrsepudx","nlicjldpeia","glg","nllxfcjjitmsuugmr","cl","pysmpgjakkjnusfopphb","zxlwcdjpn","xktsfnchwrdesnf","qptnoxxgrjmvr","exlfwjfsbsirbbkyqjtinrrwuhh","rqbnghajxygilgdjejopyuwyjqrx","vrjkqsicuqoalqyaxkaaogxbf","ixnlltqbpygmpjuspom","izajsxotcbhzdnkujwgdzo","b","lighabre","i","ljqqbfddipvcooh","hboedpepeeunx","bkhzhiefammwqkhvampokd","ptlozguwmyyp","loeshsjgazzwvs","kyrltbdzlymjxtvwiiq","fk","mbjpgwsahkgkehlcoqbhunqchxj","nfyuvlrmiturheb","cyqwsiysmoirurj","sciqruywy","podsrhmsozan","nlyadkrxhdbup","gdugldwghzt","wpjm","gjobdekmjisjgadkwwemnmco","dkjdtimdghvlhuetxyaklk","iwqylhdwqbwaqdouowoodhs","mn"]
words2 = ["eeormvovhzslwsqgzthlgntgzc","zfwownznh","suxrkdbjdjjtbkjucsbyk","u","y","lbjooktoctgwbbptiffytquha","dcsxrghgpultkatbecjadbespvww","vwduylshcpaiu","rtcxwctvquaiuwkgvdx","a","szearxmdqcismljmihbtkcirztdnrc","htgmuxtxdunsvfizb","hybe","nsegkgwcvopncmfpaahhhjeuqjosv","jtarnnpppxtzmopixeijqqahkd","hazcgrrnpourkyoeanodejiptne","kurhokvhixihe","ljwycewmecfqdhtxiokjn","qgjzzvpyvwetlsvcsw","aunns","nwcnfrzzvxafkfjfnczummtubikji","nipiygnvlfntgpxfedj","mgnt","xvjehufvaqouhztnmts","sjtbrfjwtqxakqktxjaljrbwfoxvz","dfeujeikfrtrpiafrgxvjlkpxtog","u","ggbcxoasodaqaazulrxjleecexey","inedrgssajhpygfvozigohis","pevxwgfzxebybfe","cgy","fnhvlx","vxfybaebkoq","xvhx","mxbqjtanctljewwjjlbpkgbtsm","mlwagamcikbcpuexhikmizp","qeiomipvsoqlsnhylulirrcwtqga","bwemqcgyusuauwlpbjjru","iimcbidtndh","lpjejlkmxtlbyvnscy","dlspriicnyykdsyvswlgktavwloq","dib","qoptbduulgqwquvhdvmwdz","xrtxghrbfrhpzduxeljnctgg","schmbsaupayqnpchn","kah","itotymryqufqpozrwmvsl","gurb","xsyocxcmwvqmnmxthfemmu","pkfdutm","hkbwxwjxyuld","ukdqszfjckdunnhpevw","kqfwytdvnvjrchiwprcqkfntqticsc","zjmsfwjddgjiypsmagdrujb","gn","ebncbjvhpbjecbrizdpv","nbfehcktwswih","sttmqcdmobdgtgkyxydyovahknjbsn","sryyufrtocf","eiicpwknxrzqylqpybhfd","pey","njimttradeoa","wcogjdfr","prva","tyxdmxgw","wluzocppg","kzm","wbyyperlkflaoxyxftzwxvmemof","snzpclbulddnmmjmpdurcybo","mowxgpmzojtmympmt","uvtnojjahrovzmlukf","sykhtgejlmbzshhneoyqr","ib","haqkkizidifykwijm","csjtexnr","yvgr","vzcxbtlthrynnawxnkxdptp","yvxrmscsckv"]

print(Solution().countWords(words1, words2))