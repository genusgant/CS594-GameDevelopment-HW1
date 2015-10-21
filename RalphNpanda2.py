__author__ = 'user'
# Roaming-Ralph was modified to remove collision part.

import direct.directbase.DirectStart
from panda3d.core import Filename,AmbientLight,DirectionalLight
from panda3d.core import PandaNode,NodePath,Camera,TextNode
from panda3d.core import Vec3,Vec4,BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
import random, sys, os, math, time
from panda3d.core import Point3
from direct.interval.IntervalGlobal import Sequence

SPEED = 0.5

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                        pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)

class World(DirectObject):

    def __init__(self):

        self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0}
        base.win.setClearColor(Vec4(0,0,0,1))

        # Post the instructions

        self.title = addTitle("Panda3D Tutorial: Roaming Ralph (Walking on the Moon)")
        self.inst1 = addInstructions(0.95, "[ESC]: Quit")
        self.inst2 = addInstructions(0.90, "[Left Arrow]: Rotate Ralph Left")
        self.inst3 = addInstructions(0.85, "[Right Arrow]: Rotate Ralph Right")
        self.inst4 = addInstructions(0.80, "[Up Arrow]: Run Ralph Forward")
        self.inst6 = addInstructions(0.70, "[A]: Rotate Camera Left")
        self.inst7 = addInstructions(0.65, "[S]: Rotate Camera Right")

        # Set up the environment
        #
        self.environ = loader.loadModel("models/square")
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)
        self.environ.setScale(100,100,1)
        self.moon_tex = loader.loadTexture("models/moon_1k_tex.jpg")
    	self.environ.setTexture(self.moon_tex, 1)

        # Create the main character, Ralph

        self.ralph = Actor("models/ralph",
                                 {"run":"models/ralph-run",
                                  "walk":"models/ralph-walk"})
        self.ralph.reparentTo(render)
        self.ralph.setScale(.2)
        self.ralph.setPos(10,10,0)

        # Create 2 panda
        # Actors at 000 and 10,0,0 position

        self.pandaActor1 = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})

        self.pandaActor1.setScale(0.004)
        self.pandaActor1.reparentTo(render)
        self.pandaActor1.setPos(30,30,0)

        self.pandaActor2 = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        self.pandaActor2.setScale(0.005, 0.005, 0.005)
        self.pandaActor2.reparentTo(render)
        self.pandaActor2.setPos(15,-15,0)

        self.car = loader.loadModel("models/RaceCar")
        self.car_tex = loader.loadTexture("models/tex/Mesh_3_TX.jpg")
        self.car_tex = loader.loadTexture("models/tex/Cylinder_TX.jpg")
        self.car_tex = loader.loadTexture("models/tex/Cylinder_2_TX.jpg")
        self.car_tex = loader.loadTexture("models/tex/Mesh_3_TX_2.jpg")
        self.car_tex = loader.loadTexture("models/tex/Mesh_3_TX_3.jpg")
        # self.car.setScale(2.5)
        self.car.reparentTo(render)
        self.car.setPos(20,30,0)
        self.x=0
        # self.pandaActor1.loop("walk")

        # self.pandaActor2.loop("walk")
        self.panda1AnimControl=self.pandaActor1.getAnimControl("walk")
        self.panda2AnimControl=self.pandaActor2.getAnimControl("walk")

        # Create a floater object.  We use the "floater" as a temporary
        # variable in a variety of calculations.


        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

        # Accept the control keys for movement and rotation

        self.accept("escape", sys.exit)
        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_up", self.setKey, ["forward",1])
        self.accept("a", self.setKey, ["cam-left",1])
        self.accept("s", self.setKey, ["cam-right",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])
        self.accept("arrow_right-up", self.setKey, ["right",0])
        self.accept("arrow_up-up", self.setKey, ["forward",0])
        self.accept("a-up", self.setKey, ["cam-left",0])
        self.accept("s-up", self.setKey, ["cam-right",0])

        taskMgr.add(self.move,"moveTask")
        taskMgr.add(self.jump1, "jumpPanda1")
        taskMgr.add(self.jump2, "jumpPanda2")

        # Game state variables
        self.isMoving = False
        self.pandaisMoving = False
        self.hasMoved = False
        self.hasMoved1 = False

        # Set up the camera

        base.disableMouse()
        base.camera.setPos(self.ralph.getX(),self.ralph.getY()+10,2)


        # Create some lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(Vec4(.3, .3, .3, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(Vec3(-5, -5, -5))
        directionalLight.setColor(Vec4(1, 1, 1, 1))
        directionalLight.setSpecularColor(Vec4(1, 1, 1, 1))
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))




    #Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value


    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def move(self, task):

        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.

        base.camera.lookAt(self.ralph)
        if (self.keyMap["cam-left"]!=0):
            base.camera.setX(base.camera, -20 * globalClock.getDt())
        if (self.keyMap["cam-right"]!=0):
            base.camera.setX(base.camera, +20 * globalClock.getDt())

        # save ralph's initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        startpos = self.ralph.getPos()

        # If a move-key is pressed, move ralph in the specified direction.

        if (self.keyMap["left"]!=0):
            self.ralph.setH(self.ralph.getH() + 300 * globalClock.getDt())
        if (self.keyMap["right"]!=0):
            self.ralph.setH(self.ralph.getH() - 300 * globalClock.getDt())
        if (self.keyMap["forward"]!=0):
            self.ralph.setY(self.ralph, -25 * globalClock.getDt())

        # If ralph is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if (self.keyMap["forward"]!=0) or (self.keyMap["left"]!=0) or (self.keyMap["right"]!=0):
            if self.isMoving is False:
                self.ralph.loop("run")
                self.isMoving = True
        else:
            if self.isMoving:
                self.ralph.stop()
                self.ralph.pose("walk",5)
                self.isMoving = False

        # If the camera is too far from ralph, move it closer.
        # If the camera is too close to ralph, move it farther.

        camvec = self.ralph.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if (camdist > 10.0):
            base.camera.setPos(base.camera.getPos() + camvec*(camdist-10))
            camdist = 10.0
        if (camdist < 5.0):
            base.camera.setPos(base.camera.getPos() - camvec*(5-camdist))
            camdist = 5.0
        self.ralphPanda1Dist = self.distance(self.pandaActor1)
        self.ralphCarDist = self.distance(self.car)
        self.ralphPanda2Dist = self.distance(self.pandaActor2)
        if(self.ralphPanda1Dist <10.0and self.ralphPanda1Dist>3.0 ):
            # self.pandaActor1.stop()
            self.hasMoved1 = True
            taskMgr.remove("jumpPanda1")
            self.pandaActor1.setZ(0)

            if(not(self.panda1AnimControl.isPlaying())):
                self.pandaActor1.loop("walk")
            self.pandaActor1.lookAt(self.ralph)
            self.pandaActor1.setH(180+self.pandaActor1.getH())
            self.pandaActor1.setY(self.pandaActor1,-4)
        if(self.ralphPanda1Dist<=3.0):
            self.pandaActor1.stop()

            taskMgr.add(self.jump1,"jumpPanda1")
        if( self.ralphPanda1Dist >10.0 and self.hasMoved1):
             self.pandaActor1.stop()
             self.hasMoved1 = False
             taskMgr.add(self.jump1,"jumpPanda1")

        if(self.ralphPanda2Dist <10.0and self.ralphPanda2Dist>3.0 ):
            # self.pandaActor1.stop()
            self.hasMoved = True
            taskMgr.remove("jumpPanda2")
            self.pandaActor2.setZ(0)
            if(not(self.panda2AnimControl.isPlaying())):
                self.pandaActor2.loop("walk")
            self.pandaActor2.lookAt(self.ralph)
            self.pandaActor2.setH(180+self.pandaActor2.getH())
            self.pandaActor2.setY(self.pandaActor2,-4)
        if(self.ralphPanda2Dist<=3.0 and self.panda2AnimControl.isPlaying()):
            self.pandaActor2.stop()

            taskMgr.add(self.jump2,"jumpPanda2")

        if( self.ralphPanda2Dist >10.0 and self.hasMoved):
             self.pandaActor2.stop()
             self.hasMoved = False
             taskMgr.add(self.jump2,"jumpPanda2")


        if(self.ralphCarDist <5.0 and self.ralphCarDist>3.0):

            self.car.setPos(self.ralph.getX()+ self.ralphCarDist*math.cos(self.x),
                            self.ralph.getY()+ self.ralphCarDist*math.sin(self.x),
                            0)
            self.car.lookAt(self.ralph)
            self.car.setH(self.car.getH()+180+45)
            self.x = self.x+math.pi/100
            if(self.x>4*math.pi):

                self.car.setPos(self.car.getX(),self.car.getY()+20,0)
                self.x = 0



        self.floater.setPos(self.ralph.getPos())
        self.floater.setZ(self.ralph.getZ() + 2.0)
        base.camera.lookAt(self.floater)
        return task.cont

    def distance(self,pandaActor):
        ralphPandaDistVec = self.ralph.getPos()- pandaActor.getPos()
        ralphPandaDist = ralphPandaDistVec.length()
        return ralphPandaDist

    def jump1(self,task):
         # flag=1
        secondsTime = int(task.time)
        #print "secondsTime2", secondsTime
        #print "time", secondsTime%60
        if  secondsTime<20 :
            return task.cont
        else:
            pandaHprInterval1 = self.pandaActor1.hprInterval(3,
                                                        Point3(360, 0, 0),
                                                        startHpr=Point3(0, 0, 0))
            pandaHprInterval1.start()
                # time.sleep(1)
                # self.pandaActor2.setZ(0)
            print "out"
        return task.again
    def jump2(self, task):
        # flag=1
        secondsTime = int(task.time)
        #print "secondsTime2", secondsTime
        #print "time", secondsTime%60
        if  secondsTime<20 :
            return task.cont
        else:
                # self.pandaActor2.setHpr(60,0,0)
            pandaHprInterval1 = self.pandaActor2.hprInterval(3,
                                                        Point3(360, 0, 0),
                                                        startHpr=Point3(0, 0, 0))
            pandaHprInterval1.start()
                # time.sleep(1)
                # self.pandaActor2.setZ(0)
            print "out"
        return task.again



w = World()
run()

