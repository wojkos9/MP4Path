# MP4Path
## Example usage
Access the `stss` section inside the first `mdia` container that contains video (ASCII "vide" at 8-byte offset of `hdlr`) \
`python mp4parse.py input.mp4 moov trak mdia[hdlr[8=vide]] minf stbl stss`
