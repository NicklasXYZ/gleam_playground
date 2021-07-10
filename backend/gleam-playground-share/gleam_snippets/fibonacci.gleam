//cname:'Fibonacci'
//cuuid:'35957df4-b5df-4f6e-8611-e5ce8a0bfa76'
import gleam/float
import gleam/list
import gleam/string
import gleam/int
import gleam/io
import gleam/pair

pub external type CharList

// Generate the next Fibonacci number given the previous two
// Fibonacci numbers 
pub fn next_fib(_, fib_pair: #(Int, Int)) -> #(Int, Int) {
  let first: Int =
    fib_pair
    |> pair.first()
  let second: Int =
    fib_pair
    |> pair.second()
  #(first + second, first)
}

// Generate the n'th Fibonacci number
pub fn fibonacci(n: Int) -> Int {
  list.range(0, n)
  |> list.fold(#(0, 1), next_fib)
  |> pair.first()
}

// Main escript entrypoint (function is required)
pub fn main(_args: List(CharList)) -> Nil {
  // Generate the 4th Fibonacci number
  fibonacci(4)
  |> int.to_string()
  |> io.println()
}
