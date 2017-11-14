# Process a document with embedded equations and create images
# Author: Nicholas Sharp (nsharp@cs.cmu.edu)

import os.path, tempfile, sys, subprocess
import argparse
from PIL import Image # `pip install Pillow`. used to get dimensions of images (TODO find something more lightweight)

## Arguments
parser = argparse.ArgumentParser(description="""
Process a document with embedded equations and create images.
Written by Nicholas Sharp (nsharp@cs.cmu.edu)
        """)

## Camera and image arguments 
parser.add_argument('document', help="The text document to process.")
parser.add_argument('output', help="The filename for the processed document")
parser.add_argument('--delimiters', default=['$','$$'], help="Math delimiters (specify multiple separated by spaces). Default: [$,$$]")
parser.add_argument('--output-image-dir', default="", help="Output directory for math images")
parser.add_argument('--output-image-prefix', default="", help="Prefix for filename of output images")
parser.add_argument('--output-image-filetype', default="png", help="Filetype for output images")
parser.add_argument('--image-resolution', default="200x200", help="Resolution in DPI for ouputs")
parser.add_argument('--embedded-image-style', choices=['github-wiki'], default="github-wiki", help="Style for the embedded image tags.")

args = parser.parse_args()

## Open the input file
inDoc = open(args.document, 'r')
docString = inDoc.read()

## Create a directory in which to place the output file
if not os.path.exists(args.output_image_dir):
    os.makedirs(args.output_image_dir)

## Process all delimiters

# Sort delimiters by length. This is a simple trick that allows us to properly deal with prefix-overlapping delimiters in a greedy fashion
delims = args.delimiters
delims.sort(key=len, reverse=True)
def longestMatchedDelimiter(str, pos):
    for d in delims:
        if str.startswith(d, pos):
            return d
    return None


# Helper to render an equation
# Returns the path to the image
def renderEquation(eqStr, iEq):

    print("Generating equation {} from text: {}".format(iEq, eqStr))

    # tex2im seems to evaluate equation strings in a very bad way... let's use a temp file
    tempFilename = "temp_rasterdoc_file.tex"
    tempFile = open(tempFilename, 'w')
    tempFile.write(eqStr)
    tempFile.close()

    outFilename = os.path.join(args.output_image_dir, args.output_image_prefix + format(iEq, '04d') + '.' + args.output_image_filetype) 
    cmd = ["tex2im/tex2im", '-f', args.output_image_filetype, '-o', outFilename, '-r', args.image_resolution, tempFilename]
    subprocess.check_call(cmd)

    os.remove(tempFilename)

    return outFilename

# Helper to create an image tag
def createTag(eqPath):

    if args.embedded_image_style == 'github-wiki':

        # To output images which look nice-ish on github wiki, use 200x200 resolution but embed at half size
        if not (args.image_resolution.startswith('200') and args.image_resolution.endswith('200')):
            print("WARNING: r = 200x200 recommended for github wiki images")

        with Image.open(eqPath) as img:
            width, height = img.size

        return '[[' + eqPath + '|height=' + str(int(height/2.0)) + 'px]]'

    else:
        raise Exception("unrecognized embed style")

# Process the characters of the input string in order, stopping to render an equation whenever we encounter one
# I wrote my own parsing code, so it's almost certainly buggy. Sorry future person!
inEquation = False
inEquationDelim = ''
currEquationStr = []
outputStr = []
iLine = 0
iChar = 0
iEq = 0
while (iChar < len(docString)):

    # print("iChar = {} char = {}".format(iChar, docString[iChar]))

    # Increment line count
    if docString.startswith('\n', iChar):
        iLine += 1


    # Currently in an equation
    if inEquation:

        # Check if this is the end of the equation
        d = longestMatchedDelimiter(docString, iChar)
        
        if d is None:
            # Boring old text
            currEquationStr.append(docString[iChar])
            iChar += 1

        else:
            # End the equation
            # print("Ending equation. iChar = {}".format(iChar))

            if(d != inEquationDelim):
                raise Exception("Non-matching nested tags on line {}. Opened with {} but closed with {}.".format(iLine, inEquationDelim, d))

            inEquation = False 
            inEquationDelim = ''
            iChar += len(d)

            # Render to an image
            eqPath = renderEquation("".join(currEquationStr), iEq)
            iEq += 1
            currEquationStr = []

            # Create the tag
            tag = createTag(eqPath)
            outputStr.append(tag)


    # Not currently in an equation
    else:

        # Check if this is the start of an equation
        d = longestMatchedDelimiter(docString, iChar)

        if d is None:
            # Boring old text
            outputStr.append(docString[iChar])
            iChar += 1

        else:
            # Start a new equation
            inEquation = True
            inEquationDelim = d
            # print("Starting equation. iChar = {}".format(iChar))
            iChar += len(d)
        
if inEquation:
    raise Exception("Unclosed equation at end of file")


## Write output document
outfile = open(args.output, 'w')
outfile.write("".join(outputStr))
outfile.close()
