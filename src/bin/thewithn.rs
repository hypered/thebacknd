//! # Thewithn
//!
//! Thewithn implements a few useful commands to be run from within virtual machines spawned by
//! thebacknd. The different commands are supposed to be symlinks to this single binary, which acts
//! differently depending on the symlink name.

use clap::{Parser};
use std::env;
use std::path::Path;

use thebacknd::agent::cli::{Cli, Commands};
use thebacknd::agent::cli;
use thebacknd::agent::run;

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
            Some(Commands::CurrentSystem(cmd)) => run::handle_current_system(cmd),
            Some(Commands::DesiredSystem(cmd)) => run::handle_desired_system(cmd),
            Some(Commands::DestroySystem(cmd)) => run::handle_destroy_system(cmd),
            Some(Commands::UpdateSystem(cmd)) => run::handle_update_system(cmd),
            None => println!("No subcommand provided."),
        }
    } else {
        // If invoked via symlink, simulate the respective subcommand
        let args = env::args().skip(1).collect::<Vec<_>>();
        let args = std::iter::once(invoked_as).chain(args.iter().map(String::as_str));

        match invoked_as {
            "current-system" => {
                let sub_args = cli::CurrentSystemCmd::parse_from(args);
                run::handle_current_system(&sub_args);
            }
            "desired-system" => {
                let sub_args = cli::DesiredSystemCmd::parse_from(args);
                run::handle_desired_system(&sub_args);
            }
            "destroy-system" => {
                let sub_args = cli::DestroySystemCmd::parse_from(args);
                run::handle_destroy_system(&sub_args);
            }
            "update-system" => {
                let sub_args = cli::UpdateSystemCmd::parse_from(args);
                run::handle_update_system(&sub_args);
            }
            _ => println!("Unknown symlink name: {}", invoked_as),
        }
    }
}
