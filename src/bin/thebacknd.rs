//! # Thebacknd
//!
//!  Thebacknd runs ephemeral virtual machines in the cloud in one command.

use clap::{Parser};

use thebacknd::client::cli::{Cli, Commands};
use thebacknd::client::run;

/// Thebacknd client-side binary main entry point.
fn main() {
    let cli = Cli::parse();

    match &cli.command {
        Commands::Run(cmd) => run::handle_run(cmd),
    }
}
