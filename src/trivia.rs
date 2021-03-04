use serde::Deserialize;
use std::error::Error;
use std::io::Read;

// By default, struct field names are deserialized based on the position of
// a corresponding field in the CSV data's header record.
#[derive(Debug, Deserialize)]
pub struct Question {
    category: String,
    question: String,
    answer: String,
}

// Read all questions to a vec!
pub fn read_questions<R>(src: R) -> Result<Vec<Question>, Box<dyn Error>>
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
