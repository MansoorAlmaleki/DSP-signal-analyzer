import pygame
import matplotlib.pyplot as plt
import math


pygame.init()
plt.ion
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 30)
smallfont = pygame.font.SysFont("Arial", 15)

graph = False
DFT = False

ScreenWidth = 1280
ScreenHeight = 720
IncrementValue = 1
screen = pygame.display.set_mode((ScreenWidth,ScreenHeight))
pygame.display.set_caption("DSP analyzer")

#recorded time = TotalSamples/SampleRate which in this case is a second
#nyquist sampling theorem states that higher frequency signal we can view with out aliasing is half the sample rate (512Hz) in this case at
#a sample rate of 1024Hz
SampleRate = 1024
TotalSamples = 1024
FrequencyBin = SampleRate / TotalSamples #gives the frequency incremental value, in this case its 1Hz so at a bin of 10 dividing it by the FrequencyBin we are viewing a 10Hz frequency
SamplePeriod = 1/SampleRate #1/frequency equals period
#for the DFT the viewed indexes must only be less than or equal to half the total samples to discard of the "ghost"/reflection frequencies

XcoordinateData = []
YcoordinateData = []

DFTXcoordinateData = []
DFTYcoordinateData = []

class PeriodicFunction:
    def __init__(self, frequency, amplitude, phase):
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase = phase

    def GetValue(self, time):
        #in order to get the phase angle from the time phase shift we divide time phase shift over the period of the function
        #which gives us a fraction of how many cycles it has shifted where one cycle requires 360 degrees or 2pi radians for a full revolution
        #multiplying that fraction by 2Pi results in the phase shift in degrees
        value = self.amplitude * math.sin(2*math.pi*self.frequency*(time+self.phase))
        return value

class ButtonGui:
    def __init__(self,x,y,width,height,state,text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.state = state
        self.text = text

    def DrawGui(self):
        MousePos = pygame.mouse.get_pos()
        MousePosX = MousePos[0]
        MousePosY = MousePos[1]
        #rbg values in the tuple
        Color = (190,190,190)
        ColorOutline = (130,130,130)
        #create a feel for the gui
        if(MousePosX >= self.x and MousePosX <= self.x + self.width and MousePosY >= self.y and MousePosY <= self.y + self.height):
            Color = (160, 160, 160)
        #this draws the darker rectangle
        pygame.draw.rect(screen,ColorOutline,pygame.Rect(self.x,self.y,self.width,self.height))
        #this draws the brighter rectangle and places it at the center of the dark rectangle which creates
        #the illusion of a border
        pygame.draw.rect(screen, Color, pygame.Rect(self.x+4, self.y+4, self.width-8, self.height-8))
        GraphicalText = font.render(self.text,True,(0,0,0))
        screen.blit(GraphicalText,(self.x+(self.width/2)-50,self.y+(self.height/2)-15))


    def GuiPressed(self,button):
        #here we get the mouse pos which is a tuple that contains the x and y values
        MousePos = pygame.mouse.get_pos()
        MousePosX = MousePos[0]
        MousePosY = MousePos[1]
        #collsion calculation this will check if the mouse x and y coords are intersecting with the gui box AND if the left mouse button(1) is pressed
        if(MousePosX >= self.x and MousePosX <= self.x+self.width and MousePosY >= self.y and MousePosY <= self.y+self.height and button == 1):
            return True


ButtonGuiArray = [
    ButtonGui(70,100,100,50,False,"     +"),
    ButtonGui(200,100,100,50,False,"     -"),

    ButtonGui(70, 220, 160, 80, False, "     +"),
    ButtonGui(260, 220, 160, 80, False, "     -"),

    ButtonGui(70, 370, 160, 80, False, "     +"),
    ButtonGui(260, 370, 160, 80, False, "     -"),

    ButtonGui(70,520,160,80,False,"     +"),
    ButtonGui(260,520,160,80,False,"     -"),

    ButtonGui(500,100,100,50,False,"     +"),
    ButtonGui(630,100,100,50,False,"     -"),

    ButtonGui(195,630,100,50,False,"  reset"),

    ButtonGui(535,220,160,80,False,"  graph"),

    ButtonGui(535,325,160,80,False,"  DFT"),
]


Phase = 0
Amplitude = 0
Frequency = 0
FunctionInstancesArray = []

RunProgram = True
while RunProgram:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RunProgram = False

        if(event.type == pygame.MOUSEBUTTONDOWN):
            #this if statement runs when any button of the mouse is pressed so we have to specify which
            #event.button will give the specific mouse button pressed as an int for me im using the left click so this will return a value of 1
            #you can check the collision function in the button gui class and see that i used the left click button (button == 1)
            button = event.button

            if (ButtonGuiArray[0].GuiPressed(button)):
                PeriodicFunctionObject = PeriodicFunction(Frequency, Amplitude, Phase)
                FunctionInstancesArray.append(PeriodicFunctionObject)
            if (ButtonGuiArray[1].GuiPressed(button)):
                if(len(FunctionInstancesArray) > 0):
                   FunctionInstancesArray.pop(0)

            if (ButtonGuiArray[2].GuiPressed(button)):
                Phase += IncrementValue
            if (ButtonGuiArray[3].GuiPressed(button)):
                Phase -= IncrementValue

            if (ButtonGuiArray[4].GuiPressed(button)):
                Frequency += IncrementValue
            if (ButtonGuiArray[5].GuiPressed(button)):
                Frequency -= IncrementValue

            if (ButtonGuiArray[6].GuiPressed(button)):
                Amplitude += IncrementValue
            if (ButtonGuiArray[7].GuiPressed(button)):
                Amplitude -= IncrementValue

            if (ButtonGuiArray[8].GuiPressed(button)):
                IncrementValue += .25
            if (ButtonGuiArray[9].GuiPressed(button)):
                IncrementValue -= .25

            if (ButtonGuiArray[10].GuiPressed(button)):
                IncrementValue = 1
                Phase = 0
                Frequency = 0
                Amplitude = 0
                FunctionInstancesArray.clear()

            if (ButtonGuiArray[11].GuiPressed(button)):
                graph = True

            if (ButtonGuiArray[12].GuiPressed(button)):
                DFT = True

            if (Frequency < 0):
                Frequency = 0


    if(graph == True and len(FunctionInstancesArray) > 0):
        plt.close("all")
        XcoordinateData.clear()
        YcoordinateData.clear()
        Index = 0
        for i in range(TotalSamples):
            SummedValue = 0
            Index += SamplePeriod
            for function in FunctionInstancesArray:
                SummedValue += function.GetValue(Index)
            YcoordinateData.append(SummedValue)
            XcoordinateData.append(Index)


        plt.plot(XcoordinateData, YcoordinateData)
        plt.title("Time domain")
        plt.xlabel("time")
        plt.ylabel("amplitude")
        plt.show()
        graph = False

    if(DFT == True and len(YcoordinateData) > 1):
        plt.close("all")
        DFTYcoordinateData.clear()
        DFTXcoordinateData.clear()
        RealPart = 0#cos component
        ImaginaryPart = 0#sin component
        for i in range(TotalSamples//2):
            for j in range(TotalSamples):
                RealPart += YcoordinateData[j] * math.cos((2 * math.pi * i * j) / TotalSamples)
                ImaginaryPart += YcoordinateData[j] * math.sin((2 * math.pi * i * j) / TotalSamples)

            Magnitude = math.sqrt((RealPart) ** 2 + (ImaginaryPart) ** 2) # the distance formula is used to find the the total magnitude of the two orthogonal vectors
            #the magnitude is used for the intensity, we can also get the phase component by applying an inverse tangent function on the vertical component over the horizontal component tan^-1(y/x)
            RealPart = 0
            ImaginaryPart = 0
            DFTYcoordinateData.append(Magnitude)
            DFTXcoordinateData.append(i)
        plt.plot(DFTXcoordinateData, DFTYcoordinateData)
        plt.title("frequency domain")
        plt.xlabel("frequency bin")
        plt.ylabel("amplitude")
        plt.show()
        DFT = False


    #the screen.fill function requires a tuple that contains a red green and blue value this sets the bg color
    screen.fill((255,255,255))

    #draw here
    for button in ButtonGuiArray:
        button.DrawGui()
    screen.blit(smallfont.render("Instances:" + str(len(FunctionInstancesArray)), True, (0,0,0)), (70,70))
    screen.blit(smallfont.render("Increment value:" + str(IncrementValue), True, (0, 0, 0)), (500, 70))
    screen.blit(font.render("phase:" + str(Phase), True, (0, 0, 0)), (70, 170))
    screen.blit(font.render("frequency:" + str(Frequency), True, (0, 0, 0)), (70, 320))
    screen.blit(font.render("amplitude:" + str(Amplitude), True, (0, 0, 0)), (70, 470))
    screen.blit(smallfont.render("Graph before the DFT", True, (0, 0, 0)), (542, 420))

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
