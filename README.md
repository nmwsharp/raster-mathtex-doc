# raster-mathtex-doc
Parse a document with embedded LaTeX equations and replace them with images.

Uses the simple [tex2im](http://www.nought.de/tex2im.php) to generate math rasters. Assumes `pdflatex` and ImageMagick's `convert` are both on your path.

Example usage:
```
python render-doc.py document.md document_processed.md --output-image-dir generated_images
```

For now, this is specified to generate PNGs and embed them in the github wiki style, because that's what I specifically needed. However, the code is written to be easy to extend to other variations.

Warning: This program passes the equations around as command line arguments; it is very likely vulnerable to malicous "equations" executing code. Don't run on untrusted input!