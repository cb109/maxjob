-- Render some random teapots.

for i = 1 to 100 do (
    local ranpos = [random -100 100, random -100 100, random -100 100]
    Teapot pos:ranpos wirecolor:(random black white)
)
print "now we will setup the render output"
rendSaveFile = true
rendOutputFileName = pathConfig.appendPath (pathConfig.removePathLeaf (getThisScriptFileName())) "output.png"
deleteFile rendOutputFileName
print "now render the image"
max quick render

print "nice, lets close max"
quitMax #noPrompt