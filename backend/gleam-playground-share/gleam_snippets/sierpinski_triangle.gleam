//cname:'Sierpinski Triangle'
//cuuid:'49b547ca-f3e8-4cba-a48a-990f2db3e09f'
import gleam/float
import gleam/list
import gleam/string
import gleam/int
import gleam/io

pub external type CharList

pub const symbol: String = "*"

// Generate a row (at a certain level) in a Sierpinski triangle 
pub fn aggregate(level: Int, triangle: List(String)) -> List(String) {
  let n: Int = float.round(float.power(2., int.to_float(level)))
  let whitespace: String = string.repeat(" ", n)
  list.map(
    triangle,
    fn(x: String) -> String { string.concat([whitespace, x, whitespace]) },
  )
  |> list.append(list.map(
    triangle,
    fn(x: String) -> String { string.concat([x, " ", x]) },
  ))
}

// Produce an ASCII representation of a Sierpinski triangle of order n
pub fn sierpinski_triangle(n: Int) -> Nil {
  io.println(" ")
  io.println("A Sierpinski triangle:")
  io.println(" ")
  list.range(0, n)
  |> list.fold([symbol], aggregate)
  |> string.join("\n")
  |> io.println()
}

// Main escript entrypoint (function is required)
pub fn main(_args: List(CharList)) -> Nil {
  // Generate a Sierpinski triangle of order 4
  sierpinski_triangle(4)
}
