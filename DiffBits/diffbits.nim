import os, strutils, sequtils, posix

# ANSI color codes
const 
  RESET = "\e[0m"
  BOLD = "\e[1m"
  GREEN = "\e[32m"
  YELLOW = "\e[33m"
  BLUE = "\e[34m"
  MAGENTA = "\e[35m"
  CYAN = "\e[36m"
  RED = "\e[31m"

proc printUsage() =
  echo "usage: ", paramStr(0), " [-v] [-n] [-h] <file>"
  quit(1)

proc hexToBinary(hex: string): string =
  var bin = ""
  for c in hex:
    if c in {'0'..'9', 'a'..'f', 'A'..'F'}:
      let val = parseHexInt($c)
      bin &= toBin(val, 4)
  return bin

proc main() =
  var
    verbose = false
    noconv = false
    hex = false
    argOffset = 0

  # Parse flags
  for i in 1..paramCount():
    let arg = paramStr(i)
    if arg in ["-v", "-n", "-h"]:
      case arg
      of "-v": verbose = true
      of "-n": noconv = true
      of "-h": hex = true
      argOffset = i
    else:
      break

  let hasFile = paramCount() > argOffset
  let filePath = if hasFile: paramStr(argOffset + 1) else: ""
  if not hasFile and posix.isatty(stdin.getFileHandle()) == 1 and not (verbose or noconv or hex):
    printUsage()

  # binary set a and b
  var
    a: seq[seq[char]]
    b: seq[seq[char]]
    orig: seq[string]
    comments: seq[string]
    next = false
    ind = 0

  proc readLines(): seq[string] =
    if hasFile:
      try:
        return readFile(filePath).splitLines()
      except IOError:
        quit(0) # Silent exit on file read error
    else:
      var lines: seq[string]
      for line in stdin.lines:
        lines.add(line)
      return lines

  let inputLines = readLines()
  if inputLines.len == 0:
    quit(0)

  for line in inputLines:
    var cleanedLine = line.strip()
    var comment = ""
    
    let commentPos = cleanedLine.find('#')
    if commentPos != -1:
      comment = cleanedLine[commentPos..^1]
      cleanedLine = cleanedLine[0..<commentPos].strip()

    if cleanedLine == "":
      next = true
      continue
    else:
      orig.add(cleanedLine)
      comments.add(comment)

    var bits: seq[char]
    if not noconv:
      if cleanedLine.allIt(it in {'0', '1', ' ', '_'}):
        bits = cleanedLine.toSeq()
      elif cleanedLine.allIt(it in {'0'..'9', 'a'..'f', 'A'..'F', ' ', '_'}):
        if not hex:
          bits = hexToBinary(cleanedLine).toSeq()
        else:
          bits = cleanedLine.toSeq()
      else:
        bits = newSeq[char]()
        for c in cleanedLine:
          bits.add(toBin(ord(c), 8).toSeq())
    else:
      bits = cleanedLine.toSeq()

    if next:
      b.add(bits)
    else:
      a.add(bits)

  if a.len == 0:
    quit(0)

  let bitlen = a[0].len

  var
    valid_a: seq[seq[char]]
    valid_b: seq[seq[char]]
    valid_orig: seq[string]
    valid_comments: seq[string]
    valid_ind = 0

  for i in 0..<a.len:
    if a[i].len == bitlen:
      valid_a.add(a[i])
      valid_orig.add(orig[valid_ind])
      valid_comments.add(comments[valid_ind])
    valid_ind += 1

  for i in 0..<b.len:
    if b[i].len == bitlen:
      valid_b.add(b[i])
      valid_orig.add(orig[valid_ind])
      valid_comments.add(comments[valid_ind])
    valid_ind += 1

  if valid_a.len == 0 and valid_b.len == 0:
    quit(0)

  a = valid_a
  b = valid_b
  orig = valid_orig
  comments = valid_comments

  proc findCommon(data: varargs[seq[seq[char]]]): seq[int] =
    result = newSeq[int](bitlen)
    for i in 0..<bitlen:
      result[i] = 1
    var lastbit = newSeq[int](bitlen)
    for i in 0..<bitlen:
      lastbit[i] = -1
    
    for bitsArray in data:
      for bits in bitsArray:
        for i in 0..<bits.len:
          let bit = if bits[i] in {'0', '1'}: parseInt($bits[i]) else: -1
          if lastbit[i] != -1 and bit != -1:
            if lastbit[i] != bit:
              result[i] = 0
          lastbit[i] = bit

  let common = findCommon(a, b)
  let common_a = findCommon(a)
  let common_b = findCommon(b)

  var diff = newSeq[int](bitlen)
  for i in 0..<bitlen:
    diff[i] = if not (common[i] != 0) and (common_a[i] != 0) and (common_b[i] != 0): 1 else: 0

  proc printBits() =
    var maxVal = (bitlen - 1) mod 8
    if verbose:
      stdout.write " ".repeat(orig[0].len + 1)
    for i in 1..bitlen:
      let color = if maxVal == 0: BOLD
                 elif maxVal == 4: YELLOW
                 else: RESET
      stdout.write color & $maxVal & RESET
      maxVal = (maxVal - 1 + 8) mod 8 # Ensure non-negative modulo
    echo ""

  proc midRow() =
    if verbose:
      stdout.write " ".repeat(orig[0].len + 1)
    for i in 0..<bitlen:
      let color = if diff[i] != 0: BOLD & BLUE
                 elif common[i] != 0: BOLD & GREEN
                 elif common_a[i] != 0 or common_b[i] != 0: CYAN
                 else: RESET
      let letter = if diff[i] != 0: 'X'
                  elif common[i] != 0: '='
                  elif common_a[i] != 0: '^'
                  elif common_b[i] != 0: 'v'
                  else: '-'
      stdout.write color & letter & RESET
    echo ""

  proc cmpr(rows: seq[seq[char]], common: seq[int]) =
    var commentIndex = ind
    for bits in rows:
      if verbose:
        stdout.write orig[ind] & " "
        inc ind
      for i in 0..<bitlen:
        let bit = bits[i]
        let color = if bit notin {'0', '1'}: RESET
                   elif common[i] != 0: GREEN
                   elif diff[i] != 0: (if bit == '1': MAGENTA else: RED)
                   else: RESET
        stdout.write color & bit & RESET
      if commentIndex < comments.len:
        echo comments[commentIndex]
        inc commentIndex
      else:
        echo ""

  cmpr(a, common_a)
  midRow()
  cmpr(b, common_b)
  printBits()

main()
