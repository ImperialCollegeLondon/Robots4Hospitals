import qi
import time
import sys
import argparse
import movement
import takePicture
from datetime import datetime
import subprocess
import os

class HumanGreeter(object):
    """
    A simple class to react to face detection events.
    """

    def __init__(self, app):
        """0
        Initialisation of qi framework and event detection.
        """
        super(HumanGreeter, self).__init__()
        app.start()
        session = app.session
        # Get the service ALMemory.
        self.memory = session.service("ALMemory")
        # Connect the event callback.
       
        self.subscriber = self.memory.subscriber("WordRecognized")
        self.subscriber.signal.connect(self.on_human_tracked)
        # Get the services ALTextToSpeech and ALFaceDetection.
        self.tts = session.service("ALTextToSpeech")
        self.face_detection = session.service("ALSpeechRecognition")
        
        self.face_detection.pause(True)
       
        self.face_detection.setVocabulary(["please scan me"], False)
        
        self.face_detection.pause(False)
        self.face_detection.subscribe("HumanGreeter")
        self.got_face = False
        self.session = app.session

    def on_human_tracked(self, value):
        """
        Callback for event FaceDetected.
        """
        if value == []:  # empty value when the face disappears
            self.got_face = False
        elif not self.got_face:  # only speak the first time a face appears
            self.got_face = True
            print value
            
            if value[0] == 'please scan me' and value[1] > 0.4:
                self.tts.say('Commencing scan in 3')
                time.sleep(0.5)
                self.tts.say('2')
                time.sleep(0.5)
                self.tts.say('1')
                time.sleep(0.5)

                t1 = datetime.now()
                movement.main(self.session)
                takePicture.main(self.session)
                t2 = datetime.now()

                print( 'analyzing visor')
                os.system('python3 visor2.py')
                os.system('python3 face_mask_detection.py')
                
                mask = open('MaskText', 'r')
                visor = open('VisorText', 'r')

                self.tts.say(visor.read())
                self.tts.say(mask.read())
                print(mask.read())

                if visor.read() == 'Error':
                    self.tts.say('Sorry, there was an error, please ask me to scan you again')
                    

            

            self.got_face = False
        
       
        


    def run(self):
        """
        Loop on, wait for events until manual interruption.
        """
        print "Starting HumanGreeter"
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print "Interrupted by user, stopping HumanGreeter"
            self.face_detection.unsubscribe("HumanGreeter")
            #stop
            sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="10.0.0.83",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application(["HumanGreeter", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    human_greeter = HumanGreeter(app)
    human_greeter.run()