import RPi.GPIO as GPIO
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
from firebase import firebase

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 
GPIO.setup(12,GPIO.OUT)
GPIO.setup(16,GPIO.OUT)

TRIG = 23
ECHO = 24

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

firebase = firebase.FirebaseApplication('https://mytamuofficial.firebaseio.com/', None)

#Led upon boot
#print ("LED on")
GPIO.output(16,GPIO.HIGH)
time.sleep(5)
#print ("LED off")
GPIO.output(16,GPIO.LOW)

def led(validity):
    if validity == True:
        print("Authorized")
        for x in range(5):
            #print ("LED on")
            GPIO.output(12,GPIO.HIGH)
            time.sleep(0.2)
            #print ("LED off")
            GPIO.output(12,GPIO.LOW)
            time.sleep(0.2)
        time.sleep(2)
        cv2.destroyAllWindows()
    else:
        print("Not authorized")
        for x in range(5):
            #print ("LED on")
            GPIO.output(16,GPIO.HIGH)
            time.sleep(0.2)
            #print ("LED off")
            GPIO.output(16,GPIO.LOW)
            time.sleep(0.2)
    return;

def apibase(scanned):
    validity = False
    scan_succeed = False
    
    result = firebase.get("/Taman Teratai/VisitorLog/"+scanned+"/name", None)
    print(result)
    if str(result) !=  "None":
        validity = True
        scan_succeed = True
    else:
        pass
    led(validity)
    return scan_succeed;

def scanQr():
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
        help="path to output CSV file containing barcodes")
    args = vars(ap.parse_args())

    # initialize the video stream and allow the camera sensor to warm up
    print("[INFO] starting video stream...")
    
    #  vs = VideoStream(src=0).start()
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(0.5)
     
    # open the output CSV file for writing and initialize the set of
    # barcodes found thus far
    csv = open(args["output"], "w")
    found = set()

    # loop over the frames from the video stream
    while True:
        it_scanned = False
        # grab the frame from the threaded video stream and resize it to
        # have a maximum width of 400 pixels
        frame = vs.read()
        frame = imutils.resize(frame, width=100)
     
        # find the barcodes in the frame and decode each of the barcodes
        barcodes = pyzbar.decode(frame)
        
        # loop over the detected barcodes
        for barcode in barcodes:
            # extract the bounding box location of the barcode and draw
            # the bounding box surrounding the barcode on the image
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
     
            # the barcode data is a bytes object so if we want to draw it
            # on our output image we need to convert it to a string first
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
     
            # draw the barcode data and barcode type on the image
            text = "{} ({})".format(barcodeData, barcodeType)
            text2 = barcodeData

            # call firebase
            it_scanned = apibase(text2)
            
            cv2.putText(frame, text, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
     
            # if the barcode text is currently not in our CSV file, write
            # the timestamp + barcode to disk and update the set
            if barcodeData not in found:
                csv.write("{},{}\n".format(datetime.datetime.now(),
                    barcodeData))
                csv.flush()
                found.add(barcodeData)
                
        # show the output frame
        cv2.imshow("Barcode Scanner", frame)
        key = cv2.waitKey(1) & 0xFF

        if it_scanned:
            # close the output CSV file do a bit of cleanup
            print("Next in Line, please")
            csv.close()
            cv2.destroyAllWindows()
            vs.stop()
            time.sleep(5)
            break
            
    return;
        
while 0 == 0:
    GPIO.output(TRIG, False)
    time.sleep(0.5)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO)==0:
        pulse_start = time.time()
    
    while GPIO.input(ECHO)==1:
        pulse_end = time.time()

    duration = pulse_end - pulse_start

    distance = duration * 17150

    distance = round(distance, 2)
    
    if distance < 15:
        scanQr();
    else:
        print("Scan here")
 
