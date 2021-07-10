//cname:'Hello World'
//cuuid:'55af814b-d632-411a-a583-06a6c7971e7d'
import gleam/io

pub external type CharList

// Main escript entrypoint (function is required)
pub fn main(_args: List(CharList)) {
  io.println("Hello, world!")
}
