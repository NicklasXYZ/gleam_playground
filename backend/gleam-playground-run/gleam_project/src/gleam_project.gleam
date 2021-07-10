import gleam/list
import gleam/io

pub external type CharList

pub fn main(args: List(CharList)) {
  let _args = list.map(args, char_list_to_string)
  io.println(hello_world())
}

pub fn hello_world() -> String {
  "Hello, from gleam_project!"
}

external fn char_list_to_string(CharList) -> String =
  "erlang" "list_to_binary"
