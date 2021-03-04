// (Full example with detailed comments in examples/01a_quick_example.rs)
//
// This example demonstrates clap's "usage strings" method of creating arguments
// which is less verbose
extern crate clap;
extern crate kenny;
extern crate text_io;

use clap::App;
use std::fs::File;
use std::io::{self, Write};
use std::{env, process};
use text_io::read;

use kenny::handler;
use kenny::trivia;
use slack::RtmClient;

fn main() {
    let matches = App::new("kenny")
        .version("0.1")
        .author("ob <ob@bonillas.net>")
        .about("Trivia Slack Bot")
        .args_from_usage(
            "
            --questions-file=[FILE] 'Questions file in CSV format'
            --slack-key-file=[FILE] 'Slack key'
            --test 'Test the bot'
            ",
        )
        .get_matches();

    let questions_path = matches
        .value_of("quiestions-file")
        .unwrap_or("questions.csv");
    let slack_key_file = matches.value_of("slack-key-file");
    let testing = matches.is_present("test");

    let f = File::open(questions_path);
    let f = match f {
        Ok(file) => file,
        Err(error) => panic!("Problem opening the file: {:?}", error),
    };

    let questions = trivia::read_questions(f);
    let questions = match questions {
        Ok(questions) => questions,
        Err(e) => {
            println!("error reading questions: {}", e);
            process::exit(1);
        }
    };
    println!("Read {} questions", questions.len());

    if testing {
        println!("Testing bot");
        loop {
            print!("> ");
            io::stdout().flush().unwrap();
            let line: String = read!("{}\n");
            if line == "exit" {
                break;
            }
            println!("You typed: {}", line);
        }
        process::exit(0);
    }

    let api_key: String = api_key(slack_key_file);

    let mut handler = handler::Handler;
    let r = RtmClient::login_and_run(&api_key, &mut handler);

    match r {
        Ok(_) => {}
        Err(err) => panic!("Error: {}", err),
    }
}

fn api_key(key_file: Option<&str>) -> String {
    match key_file {
        Some(file) => {
            println!("Reading key from file: {}", file);
            return String::from("FOO");
        }
        _ => {}
    }
    match env::var("SLACK_API_TOKEN") {
        Ok(val) => val,
        Err(_) => {
            println!("Required the SLACK_API_TOKEN environment variable");
            process::exit(1);
        }
    }
}
