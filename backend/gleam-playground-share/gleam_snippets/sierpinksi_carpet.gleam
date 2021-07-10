//cname:'Sierpinski Carpet'
//cuuid:'1ae08768-f751-4e6c-9e00-ea8f8fc28c6c'
import gleam/float
import gleam/list
import gleam/string
import gleam/int
import gleam/io

pub external type CharList

pub const symbol: String = "*"

// Generate a row (at a certain level) in a Sierpinski carpet 
pub fn aggregate(level: Int, carpet: List(String)) -> List(String) {
  list.map(carpet, fn(x: String) -> String { string.concat([x, x, x]) })
  |> list.append(list.map(
    carpet,
    fn(x: String) -> String {
      string.concat([x, string.replace(x, symbol, " "), x])
    },
  ))
  |> list.append(list.map(carpet, fn(x: String) { string.concat([x, x, x]) }))
}

// Produce an ASCII representation of a Sierpinski carpet of order n
pub fn sierpinski_carpet(n: Int) -> Nil {
  io.println(" ")
  io.println("A Sierpinski carpet:")
  io.println(" ")
  list.range(0, n)
  |> list.fold([symbol], aggregate)
  |> string.join("\n")
  |> io.println()
}

// Main escript entrypoint (function is required)
pub fn main(_args: List(CharList)) -> Nil {
  // Generate a Sierpinski carpet of order 3
  sierpinski_carpet(3)
}
