from mappainter import MapPainter
import random

testPaint = MapPainter()
if random.randint(0,15) > 10:
    testPaint.reset()
x,y = random.randint(0,200), random.randint(0,200)
for i in range(random.randint(1,5)):
    if random.randint(0,1):
        p = random.randint(0,1)
        if p:
            for k in range(10):
                x += 10*(random.randint(1,40))
                y -= 10*(random.randint(0,10))
                testPaint.add(x,y)
        else:
            for k in range(10):
                x -= 10*(random.randint(1,50))
                y += 10*(random.randint(0,10))
                testPaint.add(x,y)
    else:
        p = random.randint(0,1)
        if p:
            for k in range(10):
                y += 10*(random.randint(1,50))
                x += 10*(random.randint(0,10))
                testPaint.add(x,y)
        else:
           for k in range(10):
                y -= 10*(random.randint(1,50))
                x += 10*(random.randint(0,10))
                testPaint.add(x,y)

    