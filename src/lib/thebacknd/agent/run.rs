/// Implement thebacknd agent (thewithn) CLI.
use std::fs;

use super::cli;

pub fn handle_current_system(_args: &cli::CurrentSystemCmd) {
    let current_system_link = "/run/current-system";
    match fs::read_link(current_system_link) {
        Ok(path) => println!("{}", path.display()),
        Err(e) => eprintln!("Failed to read link {}: {}", current_system_link, e),
    }
}

pub fn handle_desired_system(args: &cli::DesiredSystemCmd) {
    println!("{}", args.message);
}

pub fn handle_destroy_system(args: &cli::DestroySystemCmd) {
    if args.details {
        println!("Called as 'destroy-system' with extra details.");
    } else {
        println!("Called as 'destroy-system'.");
    }
}

pub fn handle_update_system(_args: &cli::UpdateSystemCmd) {
    println!("Called as 'update-system'.");
}
