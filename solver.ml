type filter =
  | Lenght of int
  | Contain of char * int option
  | NotContain of char * int option

(** Represent a decision rule *)
let format_filter : Format.formatter -> filter -> unit =
 fun formatter f ->
  match f with
  | Lenght l -> Format.fprintf formatter "Doit etre de longueur %d" l
  | Contain (c, None) -> Format.fprintf formatter "Doit contenir un %c" c
  | Contain (c, Some i) ->
      Format.fprintf formatter "Doit contenir un %c a la position %d" c i
  | NotContain (c, None) ->
      Format.fprintf formatter "Ne doit pas contenir un %c" c
  | NotContain (c, Some i) ->
      Format.fprintf formatter "Ne doit pas contenir un %c a la position %d" c i

(** Return true if the word match the given filter *)
let check_filter : string -> filter -> bool =
 fun word f ->
  match f with
  | Lenght l -> l = String.length word
  | Contain (c, pos) -> (
      match pos with
      | None -> String.contains word c
      | Some i -> Char.equal c (String.get word i))
  | NotContain (c, pos) -> (
      match pos with
      | None -> not (String.contains word c)
      | Some i -> not (Char.equal c (String.get word i)))

type data = {
  number : int;
  element : string list;
  freq : (char, int) Hashtbl.t;
}

let empty_data () = { number = 0; element = []; freq = Hashtbl.create 26 }

(** Evaluate the score for each char (lower is better) *)
let extract_freq : data -> (char * int) list =
 fun data ->
  let number_2 = data.number / 2 in
  Hashtbl.fold (fun k v acc -> (k, abs (v - number_2)) :: acc) data.freq []
  (* Sort the list for a pretty printing *)
  |> List.sort (fun v1 v2 -> snd v1 - snd v2)

(** Display the informations about the structure *)
let show_structure : Format.formatter -> data -> filter list -> unit =
 fun format data filters ->
  Format.fprintf format "Filtres en cours :\n%a\n\n"
    (Format.pp_print_list ~pp_sep:Format.pp_force_newline format_filter)
    filters;

  Format.fprintf format "Got %d elements\n" data.number;
  Format.pp_print_list ~pp_sep:Format.pp_force_newline
    (fun f (k, v) -> Format.fprintf f "%c -> %d" k v)
    format (extract_freq data)

let update_freq : (char, int) Hashtbl.t -> char -> unit =
 fun freq c ->
  match Hashtbl.find_opt freq c with
  | None -> Hashtbl.add freq c 1
  | Some value -> Hashtbl.replace freq c (value + 1)

let add_word : filter list -> data -> string -> data =
 fun filters data word ->
  match List.for_all (check_filter word) filters with
  | true ->
      String.iter (update_freq data.freq) word;
      { data with number = data.number + 1; element = word :: data.element }
  | false -> data

(** Get the initial list *)
let rec get_list : in_channel -> data -> filter list -> data =
 fun channel data filters ->
  let word =
    try Some (String.lowercase_ascii (Stdlib.input_line channel))
    with End_of_file -> None
  in
  match word with
  | None -> data
  | Some word ->
      let data = add_word filters data word in
      get_list channel data filters

(** Get the word which with the most information in it.
The information is the score given to each character, representing each
frequency in the whole word list (lower is better). If the same letter is
present many times, we consider that succeding letters does not give any more
informations (do not consider the position here) *)
let pick_next_word : data -> (char * int) list -> string * int =
 fun data scores ->
  let p' : (string * int) option -> string -> (string * int) option =
   fun prec word ->
    (* evaluate the score for this word *)
    let _, eval =
      String.fold_left
        (fun (scores, score) c ->
          match List.assoc_opt c scores with
          | None ->
              (* if the character has no score associated, we consider that it
                 does not provide any more information, and give it the max
                 score available *)
              (scores, score + (data.number / 2))
          | Some v ->
              let new_scores =
                List.filter (fun (c', _) -> not (Char.equal c c')) scores
              in
              (new_scores, score + v))
        (scores, 0) word
    in
    match prec with
    | None -> Some (word, eval)
    | Some (_, prec_score) when eval < prec_score -> Some (word, eval)
    | _ -> prec
  in
  match List.fold_left p' None data.element with None -> ("", 0) | Some r -> r

(** Compare the proposed word and the result from the user in order to identify
    the future rules to apply *)
let create_new_rules word result =
  let rules = ref []
  and max_length = min (String.length word) (String.length result) in
  for i = 0 to max_length - 1 do
    match (String.get word i, String.get result i) with
    (* A space means that the letter is not present *)
    | c, ' ' -> rules := NotContain (c, None) :: !rules
    (* The same letter means that the we found the right caracter *)
    | c, c' when Char.equal c c' -> rules := Contain (c, Some i) :: !rules
    (* Anything else, we got the letter, but at the wrong place *)
    | c, _ -> rules := Contain (c, None) :: NotContain (c, Some i) :: !rules
  done;
  !rules

let rec run filters words =
  let () = show_structure Format.std_formatter words filters in
  let freq = extract_freq words in
  let next, score = pick_next_word words freq in

  let () =
    Format.fprintf Format.std_formatter "Next word will be :\n%s (%d)\n" next
      score
  in

  let input = Stdlib.read_line () in

  (* if the input is empty, remove the word from the list and restart *)
  match String.equal String.empty input with
  | true ->
      let new_words =
        List.filter (fun w -> not (String.equal w next)) words.element
      in
      run filters { words with element = new_words; number = words.number - 1 }
  | false ->
      let new_rules =
        List.append filters (create_new_rules next input)
        |> List.sort_uniq Stdlib.compare
      in

      let words =
        List.fold_left (add_word new_rules) (empty_data ()) words.element
      in
      run new_rules words

let () =
  let initial_filter = [ Lenght 5 ] in
  let words_channel = open_in Sys.argv.(1) in
  let words = get_list words_channel (empty_data ()) initial_filter in
  close_in words_channel;
  run initial_filter words