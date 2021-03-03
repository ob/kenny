// (Full example with detailed comments in examples/01a_quick_example.rs)
//
// This example demonstrates clap's "usage strings" method of creating arguments
// which is less verbose
extern crate clap;
extern crate kenny;
use clap::App;
use std::error::Error;
use std::fs::File;
use std::io::Read;
use std::{env, process};

use kenny::handler;
use serde::Deserialize;
use slack::RtmClient;

// By default, struct field names are deserialized based on the position of
// a corresponding field in the CSV data's header record.
#[derive(Debug, Deserialize)]
struct Question {
    category: String,
    question: String,
    answer: String,
}

// Read all questions to a vec!
fn read_questions<R>(src: R) -> Result<Vec<Question>, Box<dyn Error>>
where
    R: Read,
{
    let mut questions: Vec<Question> = vec![];
    let mut rdr = csv::Reader::from_reader(src);
    for result in rdr.deserialize() {
        // Notice that we need to provide a type hint for automatic
        // deserialization.
        let question: Question = result?;
        questions.push(question);
    }
    Ok(questions)
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

    let questions_path = matches.value_of("file").unwrap_or("questions.csv");
    println!("Value for questions: {}", questions_path);
    let _slack_key = matches.value_of("key").unwrap_or("slack-key");
    println!("key: {}", _slack_key);

    let f = File::open(questions_path);
    let f = match f {
        Ok(file) => file,
        Err(error) => panic!("Problem opening the file: {:?}", error),
    };

    let questions = read_questions(f);
    let questions = match questions {
        Ok(questions) => questions,
        Err(e) => {
            println!("error reading questions: {}", e);
            process::exit(1);
        }
    };
    println!("Read {} questions", questions.len());

    let api_key: String = api_key();

    let mut handler = handler::Handler;
    let r = RtmClient::login_and_run(&api_key, &mut handler);

    match r {
        Ok(_) => {}
        Err(err) => panic!("Error: {}", err),
    }
}

fn api_key() -> String {
    match env::var("SLACK_API_TOKEN") {
        Ok(val) => val,
        Err(_) => {
            println!("Required the SLACK_API_TOKEN environment variable");
            process::exit(1);
        }
    }
}
