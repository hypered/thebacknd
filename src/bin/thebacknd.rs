//! # Thebacknd
//!
//!  Thebacknd runs ephemeral virtual machines in the cloud in one command.

use clap::{Parser};

use clap::{Command, CommandFactory, Arg, ValueHint, value_parser, ArgAction};
use clap_complete::{generate, Generator, Shell};
use std::io;

use thebacknd::client::cli::{Cli, Commands};
use thebacknd::client::run;

/// Thebacknd client-side binary main entry point.
fn main() {
    let cli = Cli::parse();

    if let Some(generator) = cli.generator {
        let mut cmd = Cli::command();
        eprintln!("Generating completion file for {generator:?}...");
        print_completions(generator, &mut cmd);
    } else {
      match &cli.command {
          Commands::Run(cmd) => run::handle_run(cmd),
      }
    }
}

fn print_completions<G: Generator>(gen: G, cmd: &mut Command) {
    generate(gen, cmd, cmd.get_name().to_string(), &mut io::stdout());
}
