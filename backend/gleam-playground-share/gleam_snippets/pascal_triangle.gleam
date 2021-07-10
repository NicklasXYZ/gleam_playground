//cname:'Pascal Triangle'
//cuuid:'f0b0eb0e-11ce-4a74-bfb6-3e0d54bd0645'
import gleam/float
import gleam/int
import gleam/io
import gleam/list
import gleam/pair
import gleam/string

pub external type CharList

// Create type aliases
type Row =
  List(Int)

type State =
  #(Row, List(Row))

// Generate the next row in a Pascal triangle 
pub fn next_state(_, state: State) -> State {
  let current_row: Row = pair.first(state)
  let previous_rows: List(Row) = pair.second(state)
  let list_1: List(Int) = list.append(current_row, [0])
  let list_2: List(Int) = list.append([0], current_row)
  let next_row: Row =
    list.zip(list_1, list_2)
    |> list.map(fn(x) -> Int { pair.first(x) + pair.second(x) })
  #(next_row, [next_row, ..previous_rows])
}

// Generate the first n rows of a Pascal triangle  
pub fn pascal_triangle(n: Int) -> List(Row) {
  // Create a tuple that contains the state of the Pascal triangle with values:
  // (i) the current row, and (ii) a list containing all generated rows 
  let state: #(List(Int), List(List(Int))) = #([1], [[1]])
  list.range(1, n)
  |> list.fold(state, next_state)
  |> pair.second()
}

// Nicely format each row of a Pascal triangle
pub fn print_triangle(rows: List(Row), max_digits: Int) -> Nil {
  rows
  |> list.reverse()
  // Format each row in the Pascal triangle such that it looks nice when printed
  // to stdout. This function simply adds the correct amount of padding in front
  // of each value in a Pascal triangle such that all the values aligned. 
  |> list.fold(
    [],
    fn(row: Row, triangle: List(String)) -> List(String) {
      list.append(
        triangle,
        // Convert the integer values in a row to single string
        [
          row
          |> list.map(fn(x: Int) -> String {
            let x_string: String = int.to_string(x)
            let digits: Int = string.length(x_string)
            let padding = string.repeat(" ", max_digits - digits + 1)
            string.concat([padding, x_string])
          })
          |> string.join(""),
        ],
      )
    },
  )
  // Print to stdout each row of the Pascal triangle on a new line 
  |> string.join("\n")
  |> io.println()
}

// Calculate the binomial coefficiet using the effecient multiplicative formula
pub fn binomial_coefficient(n: Int, k: Int) -> Int {
  list.range(1, k + 1)
  |> list.map(fn(x: Int) { int.to_float(n + 1 - x) /. int.to_float(x) })
  |> float.product()
  |> float.round()
}

// Main escript entrypoint (function is required)
pub fn main(_args: List(CharList)) -> Nil {
  // The number of rows of a Pascal triangle to generate and print
  let n: Int = 15

  // Calculate the length of the largest number of the Pascal triangle.
  // If we know the largest number in the triangle, then we can add the
  // right amount of whitespace padding to each value in each of the rows.
  // As a result the triangle will look nice when printed to stdout
  let max_digits: Int =
    binomial_coefficient(n, n / 2)
    |> int.to_string()
    |> string.length()

  // Generate and print the first 15 rows of a Pascal triangle to stdout
  pascal_triangle(n)
  |> print_triangle(max_digits)
}
