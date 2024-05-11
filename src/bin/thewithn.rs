//! # Thewithn
//!
//! Thewithn implements a few useful commands to be run from within virtual machines spawned by
//! thebacknd. The different commands are supposed to be symlinks to this single binary, which acts
//! differently depending on the symlink name.

use clap::{Parser, Subcommand};
use std::env;
use std::path::Path;

/// Thewithn single binary main entry point.
fn main() {
    let invoked_as = env::args().nth(0).unwrap_or_else(|| String::from("unknown"));
    let invoked_as = Path::new(&invoked_as)
        .file_name()
        .unwrap_or_else(|| std::ffi::OsStr::new("unknown"))
        .to_str()
        .unwrap_or("unknown");

    if invoked_as == "thewithn" {
        // If invoked directly with "thewithn", parse fully
        let cli = Cli::parse();

        match &cli.command {
            Some(Commands::CurrentSystem(cmd)) => handle_current_system(cmd),
            Some(Commands::DesiredSystem(cmd)) => handle_desired_system(cmd),
            Some(Commands::DestroySystem(cmd)) => handle_destroy_system(cmd),
            Some(Commands::UpdateSystem(cmd)) => handle_update_system(cmd),
            None => println!("No subcommand provided."),
        }
    } else {
        // If invoked via symlink, simulate the respective subcommand
        let args = env::args().skip(1).collect::<Vec<_>>();
        let args = std::iter::once(invoked_as).chain(args.iter().map(String::as_str));

        match invoked_as {
            "current-system" => {
                let sub_args = CurrentSystemCmd::parse_from(args);
                handle_current_system(&sub_args);
            }
            "desired-system" => {
                let sub_args = DesiredSystemCmd::parse_from(args);
                handle_desired_system(&sub_args);
            }
            "destroy-system" => {
                let sub_args = DestroySystemCmd::parse_from(args);
                handle_destroy_system(&sub_args);
            }
            "update-system" => {
                let sub_args = UpdateSystemCmd::parse_from(args);
                handle_update_system(&sub_args);
            }
            _ => println!("Unknown symlink name: {}", invoked_as),
        }
    }
}

#[derive(Parser)]
#[command(name = "thewithn")]
#[command(about = "A program that behaves differently based on the symlink name or subcommands")]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand)]
enum Commands {
    CurrentSystem(CurrentSystemCmd),
    DesiredSystem(DesiredSystemCmd),
    DestroySystem(DestroySystemCmd),
    UpdateSystem(UpdateSystemCmd),
}

#[derive(Parser)]
struct CurrentSystemCmd {
    /// Activate verbose mode
    #[arg(short, long)]
    verbose: bool,
}

#[derive(Parser)]
struct DesiredSystemCmd {
    /// Provide a custom message
    #[arg(short, long, default_value = "Called as 'desired-system'.")]
    message: String,
}

#[derive(Parser)]
struct DestroySystemCmd {
    /// Print extra details
    #[arg(short, long)]
    details: bool,
}

#[derive(Parser)]
struct UpdateSystemCmd {
}

fn handle_current_system(args: &CurrentSystemCmd) {
    if args.verbose {
        println!("Called as 'current-system' with verbosity enabled.");
    } else {
        println!("Called as 'current-system'.");
    }
}

fn handle_desired_system(args: &DesiredSystemCmd) {
    println!("{}", args.message);
}

fn handle_destroy_system(args: &DestroySystemCmd) {
    if args.details {
        println!("Called as 'destroy-system' with extra details.");
    } else {
        println!("Called as 'destroy-system'.");
    }
}

fn handle_update_system(_args: &UpdateSystemCmd) {
    println!("Called as 'update-system'.");
}
