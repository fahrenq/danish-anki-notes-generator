q=$1

alias gc="/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"

gc "https://ordnet.dk/ddo/ordbog?query=$q"
gc "https://www.ordbogen.com/en/search#/auto/ordbogen-daen/$q" 

# "open" command doesn't work with letters like ø å æ
# open "https://ordnet.dk/ddo/ordbog?query=$q"
# open "https://www.ordbogen.com/en/search#/auto/ordbogen-daen/$q"

