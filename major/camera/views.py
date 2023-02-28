from django.shortcuts import render
from django.http import HttpResponse
import numpy as np
import os
from camera import DummyHandTrackingModule as Htm
import cv2
# Create your views here.

def Home(request):
    return render(request,'index.html');



def camera(request):
    global equation
    class Button:
        def __init__(self, pos, width, height, value):
            self.pos = pos
            self.width = width
            self.height = height
            self.value = value

        def draw(self, img):
            width = self.width + self.pos[0]
            height = self.height + self.pos[1]
            cv2.rectangle(img, self.pos, (width, height), (225, 225, 225), cv2.FILLED)
            cv2.rectangle(img, self.pos, (width, height), (50, 50, 50), 3)
            cv2.putText(img, self.value, (int(width * 0.95), int(height * 0.95)), cv2.FONT_HERSHEY_PLAIN, 2, (50, 50, 50),
                    2)

        def check_click(self, x, y):
            width = self.width + self.pos[0]
            height = self.height + self.pos[1]
            if self.pos[0] < x < self.pos[0] + self.width and self.pos[1] < y < self.pos[1] + self.height:
                cv2.putText(img, self.value, (int(width * 0.95), int(height * 0.95)), cv2.FONT_HERSHEY_PLAIN, 4,
                        (0, 255, 0), 6)
                return True
            return False
        

    # calculator stuff

    # for calculator hand tracking module
    button_list = []
    ypos = 200
    SQUARE_SIZE = 70
    buttons = [
        ["7", '8', '9', '*'],
        ['4', '5', '6', '-'],
        ['3', '2', '1', '+'],
        ['0', '/', 'C', '=']
    ]

    # calculator equation
    equation = ""
    for x in range(4):
        xpos = 850
        # 230
        for y in range(4):
            xpos = xpos + SQUARE_SIZE  # 320
            button1 = Button((xpos, ypos), SQUARE_SIZE, SQUARE_SIZE, buttons[x][y])
            button_list.append(button1)
        ypos += SQUARE_SIZE

    screenx = 850 + SQUARE_SIZE
    screeny = 200
    screenWidth = screenx + SQUARE_SIZE * 4
    screenHeight = 30 + SQUARE_SIZE

    one_tap = True
    operations = ["+", "-", "*", "/"]

    def perform_operation():
        # global equation
        equation_list = equation.split(" ")
        current_operation = ""
        a = 0
        #print(equation_list)
        for equ in equation_list:
            if equ != "":
                if equ in operations:
                    current_operation = equ
                elif a == 0:
                    a = int(equ)
                else:
                    b = int(equ)
                    if current_operation == "+":
                        a = a + b
                    elif current_operation == "-":
                        a = a - b
                    elif current_operation == "*":
                        a = a * b
                    elif current_operation == "/":
                        a = a / b
        return a
    #############################################
    # variables

    # Virtual Board
    sHeight = int(720 * 0.97)
    sWidth = int(1280 * 1)
    drawColor = (0, 51, 255)
    thickness = 10
    thicknessColor = (128, 255, 255)
    xp, yp = 0, 0

    # Black Board
    boardImageNum = 0
    usingBoard = False

    # Presentation Mode
    pptNum = 0
    pptShow = False
    # selectShow = True
    # presentation webcam size
    hs, ws = int(120 * 1.2), int(213 * 1.2)
    gesture_threshold = 300

    # Calculator Mode
    calShow = False
    # calculator gesture_threshold
    gesXStart = 800
    gesYStart = 180

    ############################

    # 1.board
    # 2.black board
    # 3.presentation
    operationCode = 1

    # button pressed
    gestDone = False
    gestCounter = 0
    delay = 25

    # annotations
    annotations = [[]]
    annotationStart = False
    annotationNumber = 0

    #############################################
    # cam on
    cap = cv2.VideoCapture(0)
    cap.set(3, sWidth)
    cap.set(4, sHeight)

    ############################################
    # storing Menu images with the help of os
    folderPath = "camera/Menu"
    headerImageList = os.listdir(folderPath)
    # print(headerImageList)
    overlayList = []
    for imPath in headerImageList:
        image = cv2.imread(f'{folderPath}/{imPath}')
        # print(f'{folderPath}/{imPath}')
        overlayList.append(image)
    # print(len(overlayList))
    header = overlayList[0]

    #############################################

    # storing black Board images with the help of os
    boardFolderPath = "camera/Board"
    boardImageList = sorted(os.listdir(boardFolderPath), key=len)
    # print(headerImageList)
    overLayerList = []
    for imPath in boardImageList:
        boardImage = cv2.imread(f'{boardFolderPath}/{imPath}')
        # print(f'{boardFolderPath}/{imPath}')
        overLayerList.append(boardImage)
    # print(len(overLayerList))
    boardNum = overLayerList[0]

    #############################################

    # storing Presentation Slides
    pptFolderPath = "camera/Slides"
    pptImgList = sorted(os.listdir(pptFolderPath), key=len)

    #############################################

    detector = Htm.handDetector(maxHands=1, detectionCon=0.4, trackCon=0.2)

    #############################################
    # canvas to draw
    imgCanvas = np.zeros((720, 1280, 3), np.uint8)

    while True:
        # selectShow = True
        # import image
        success, img = cap.read()
        # board image import
        pathFullImage = os.path.join(boardFolderPath, boardImageList[boardImageNum])
        blackBoard = cv2.imread(pathFullImage)
        blackBoard = cv2.resize(blackBoard, (1280, 720))

        # ppt image import
        pptPathFullImage = os.path.join(pptFolderPath, pptImgList[pptNum])
        pptCurrent = cv2.imread(pptPathFullImage)
        pptCurrent = cv2.resize(pptCurrent, (1280, 720))

        # flipping image
        img = cv2.flip(img, 1)

        # find hand landmarks
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        # calculator
        if calShow:
        # draw screen
            cv2.rectangle(img, (screenx, screeny), (screenWidth, screenHeight), (225, 225, 225), cv2.FILLED)
            cv2.rectangle(blackBoard, (screenx, screeny), (screenWidth, screenHeight), (225, 225, 225), cv2.FILLED)
            cv2.rectangle(img, (screenx, screeny), (screenWidth, screenHeight), (50, 50, 50), 2)
            cv2.rectangle(blackBoard, (screenx, screeny), (screenWidth, screenHeight), (50, 50, 50), 2)
            # draw buttons
            for button in button_list:
                button.draw(img)
                button.draw(blackBoard)
            # displying the equation
            cv2.putText(img, equation.replace(" ", ""), (screenx + 10, screenHeight + 70), cv2.FONT_HERSHEY_PLAIN, 2,
                        (50, 50, 50), 2)
            cv2.putText(blackBoard, equation.replace(" ", ""), (screenx + 10, screenHeight + 70), cv2.FONT_HERSHEY_PLAIN, 2,
                        (50, 50, 50), 2)
     
        if len(lmList) != 0 and gestDone is False:
            # check which fingers are up
            fingers = detector.fingersUp()
            print(fingers)

            # tip of index and middle finger
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]
            indexFinger = x1, y1

            # presentation
            if operationCode == 3:
                if fingers == [1, 1, 1, 1, 1]:
                    header = overlayList[0]
                    boardImageNum = 0
                    drawColor = (0, 0, 255)
                    operationCode = 1

                # middle of the hand
                _, cx, cy = lmList[10]
                x_val = cx
                y_val = cy
                # x_val = int(np.interp(lmList[8][1], [sWidth // 2, sWidth], [0, sWidth]))
                # y_val = int(np.interp(lmList[8][2], [150, sHeight - 150], [0, sHeight]))
                cv2.line(img, (0, gesture_threshold), (sWidth, gesture_threshold), (0, 255, 0), 10)
                indexFinger = x_val, y_val

                # drawing
                if fingers == [0, 1, 0, 0, 0] or fingers == [1, 1, 0, 0, 0]:
                    if annotationStart is False:
                        annotationStart = True
                        annotationNumber += 1
                        annotations.append([])
                    cv2.circle(pptCurrent, indexFinger, 4, (0, 0, 255), cv2.FILLED)
                    annotations[annotationNumber].append(indexFinger)
                else:
                    annotationStart = False

                if cy <= gesture_threshold:

                    # left Slide
                    if fingers == [1, 0, 0, 0, 0]:
                        # print("left")
                        if pptNum > 0:
                            gestDone = True
                            annotations = [[]]
                            annotationStart = False
                            annotationNumber = 0
                            pptNum -= 1
                    # right slide
                    if fingers == [0, 0, 0, 0, 1]:
                        # print("right")
                        if pptNum < len(pptImgList) - 1:
                            gestDone = True
                            annotations = [[]]
                            annotationStart = False
                            annotationNumber = 0
                            pptNum += 1

                # selection
                if fingers == [0, 1, 1, 0, 0] or fingers == [1, 1, 1, 0, 0]:
                    cv2.circle(pptCurrent, indexFinger, 4, (0, 0, 255), cv2.FILLED)

                # eraser
                if fingers == [0, 1, 0, 0, 1]:
                    if annotations:
                        if annotationNumber >= 0:
                            annotations.pop(-1)
                            annotationNumber -= 1
                            gestDone = True
                # undo
                if fingers == [0, 1, 1, 1, 0]:
                    if annotations:
                        annot_start = False
                        if annotationNumber >= 0:
                            annotations.pop(-1)
                            annotationNumber -= 1
                            gestDone = True


            # virtual board
            else:
                # if selection mode - two fingers are up
                if fingers == [0, 1, 1, 0, 0] or fingers == [1, 1, 1, 0, 0]:
                    xp, yp = 0, 0
                    # print("Selection Mode")
                    # checking for the click
                    if y1 < 72:
                        if 71 < x1 < 180:
                            header = overlayList[0]
                            boardImageNum = 0
                            drawColor = (0, 0, 255)
                            operationCode = 1
                        elif 180 < x1 < 350:
                            header = overlayList[1]
                            boardImageNum = 1
                            drawColor = (153, 77, 0)
                            operationCode = 1
                        elif 350 < x1 < 530:
                            header = overlayList[2]
                            boardImageNum = 2
                            drawColor = (0, 102, 0)
                            operationCode = 1
                        elif 500 < x1 < 680:
                            header = overlayList[3]
                            boardImageNum = 3
                            drawColor = (122, 41, 163)
                            operationCode = 1
                        elif 700 < x1 < 880:
                            header = overlayList[4]
                            boardImageNum = 4
                            drawColor = (0, 0, 0)
                            operationCode = 1
                        elif 900 < x1 < 1070:
                            header = overlayList[5]
                            boardImageNum = 5
                            drawColor = (0, 89, 179)
                            operationCode = 3

                        elif 1100 < x1 < 1280:
                            header = overlayList[6]
                            boardImageNum = 6
                            drawColor = (153, 153, 102)
                            calShow = True

                    cv2.rectangle(img, (x1, y1 - 20), (x2, y2 + 25), drawColor, cv2.FILLED)
                    cv2.rectangle(blackBoard, (x1, y1 - 20), (x2, y2 + 25), drawColor, cv2.FILLED)

                # thickness increase
                if fingers == [0, 1, 1, 0, 1]:
                    xp, yp = 0, 0
                    if thickness < 40:
                        thickness += 1
                    cv2.circle(img, (x1, y1), thickness, drawColor, cv2.FILLED)
                    cv2.circle(blackBoard, (x1, y1), thickness, drawColor, cv2.FILLED)               
                # thickness decrease
                if fingers == [0, 1, 1, 1, 0]:
                    xp, yp = 0, 0
                    if thickness > 10:
                        thickness -= 1
                    cv2.circle(img, (x1, y1), thickness, drawColor, cv2.FILLED)
                    cv2.circle(blackBoard, (x1, y1), thickness, drawColor, cv2.FILLED)

                # black Board
                if fingers == [1, 0, 0, 0, 1] :
                    xp, yp = 0, 0
                    usingBoard = not usingBoard
                    gestDone = True
                
                # all clear
                if lmList[0][2] - lmList[5][2] < 30 and fingers[1] and fingers[2] and fingers[3]:
                    xp, yp = 0, 0
                    imgCanvas = np.zeros((720, 1280, 3), np.uint8)

                # index finger to draw
                if fingers == [0, 1, 0, 0, 0] or fingers == [1, 1, 0, 0, 0]:
                    cv2.circle(img, (x1, y1), thickness, drawColor, cv2.FILLED)
                    cv2.circle(blackBoard, (x1, y1), thickness, drawColor, cv2.FILLED)
                    if xp == 0 and yp == 0:
                        xp, yp = x1, y1

                    if drawColor == (0, 0, 0):
                        cv2.line(img, (xp, yp), (x1, y1), drawColor, thickness)
                        cv2.line(blackBoard, (xp, yp), (x1, y1), drawColor, thickness)
                        cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, thickness)
                    else:
                        cv2.line(img, (xp, yp), (x1, y1), drawColor, thickness)
                        cv2.line(blackBoard, (xp, yp), (x1, y1), drawColor, thickness)
                        cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, thickness)
                    xp, yp = x1, y1


                # calculator
                if calShow:
                    if fingers == [1, 1, 1, 1, 1]:
                        header = overlayList[0]
                        boardImageNum = 0
                        drawColor = (0, 0, 255)
                        operationCode = 1
                        calShow = False  

                    borderX = lmList[8][1]
                    borderY = lmList[12][2]
                    if borderX >= gesXStart and borderY >= gesYStart:
                        length, _, img = detector.findDistance(lmList[8], lmList[12], img)
                        _, x, y = lmList[8]
                        # print(length)
                        if length < 50 and one_tap:
                            one_tap = False
                            for button in button_list:
                                if button.check_click(x, y):
                                    if button.value == "C":
                                        equation = ""
                                    elif button.value == "=":
                                        equation = str(perform_operation()) + " "
                                    else:
                                        if button.value in operations:
                                            equation += " " + button.value + " "
                                        else:
                                            equation += button.value

                        elif length > 60 and not one_tap:
                            one_tap = True  

        # Gesture Performed Iterations:
        if gestDone:
            gestCounter += 1
            if gestCounter > delay:
                gestCounter = 0
                gestDone = False

        # ppt annotations
        for i in range(len(annotations)):
            for j in range(len(annotations[i])):
                if j != 0:
                    cv2.line(pptCurrent, annotations[i][j - 1], annotations[i][j], (0, 0, 200), 12)
        
        # img and img canvas joining
        calImg = imgCanvas
        imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, imgCanvas)
        blackBoard = cv2.bitwise_and(blackBoard, imgInv)
        blackBoard = cv2.bitwise_or(blackBoard, imgCanvas)

        # setting the header image
        img[0:72, 0:1280] = header

        # attaching board on screen
        h, w, _ = img.shape
        if usingBoard:
            img[0:h, 0:w] = blackBoard

        if operationCode == 3:
            # adding the webcam image on the slides
            imgSmall = cv2.resize(img, (ws, hs))
            h, w, _ = pptCurrent.shape
            pptCurrent[0:hs, w - ws:w] = imgSmall
            img[0:h, 0:w] = pptCurrent

        # showing image
        cv2.imshow("Image", img)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return render(request,"Thank.html")

    





