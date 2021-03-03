// (Full example with detailed comments in examples/01a_quick_example.rs)
//
// This example demonstrates clap's "usage strings" method of creating arguments
// which is less verbose
extern crate clap;
use clap::App;
use std::error::Error;
use std::io;
use std::process;

use serde::Deserialize;

// By default, struct field names are deserialized based on the position of
// a corresponding field in the CSV data's header record.
#[derive(Debug, Deserialize)]
struct Question {
    category: String,
    question: String,
    answer: String,
}

fn read_questions() -> Result<(), Box<dyn Error>> {
    let mut rdr = csv::Reader::from_reader(io::stdin());
    for result in rdr.deserialize() {
        // Notice that we need to provide a type hint for automatic
        // deserialization.
        let question: Question = result?;
        println!("{:?}", question);
    }
    Ok(())
}

fn main() {
    let matches = App::new("kenny")
        .version("0.1")
        .author("ob <ob@bonillas.net>")
        .about("Trivia Slack Bot")
        .args_from_usage(
            "-f, --file=[FILE] 'Questions file in CSV format'
            -k, --key=[FILE] 'Slack key'
            -v...                'Sets the level of verbosity'",
        )
        .get_matches();

    let _questions = matches.value_of("file").unwrap_or("questions.csv");
    println!("Value for questions: {}", _questions);
    let _slack_key = matches.value_of("key").unwrap_or("slack-key");
    println!("key: {}", _slack_key);

    if let Err(err) = read_questions() {
        println!("error reading questions: {}", err);
        process::exit(1);
    }
}
