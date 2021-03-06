from scapy.all import *
import sys

def parsePCAP(pkts):
  for pkt in pkts:
    print "Source IP: " + pkt[IP].src	
    print "Destination IP: " + pkt[IP].dst	
    print "Source port: " + str(pkt[TCP].sport)	
    print "Destinations port: " + str(pkt[TCP].dport)	
    print "Packet Payload: " + str(pkt[TCP].payload)	

def findOtherIPs ( pkts ) :
 unique = []
 for pkt in pkts :
     if " 10.3.0 " in pkt [ IP ]. src :
         if pkt [ IP ]. src not in unique :
             unique . append ( pkt [ IP ]. src )
 return unique


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print "usage: python lab3.py [pcap]"
    sys.exit()	 
  pcap= rdpcap(sys.argv[1])
  pcap = [pkt for pkt in pcap if TCP in pkt]
  print findOtherIPs(pcap)

