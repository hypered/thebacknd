use clap::{Parser, Subcommand};
use std::process::{Command as ProcessCommand, exit};
use regex::Regex;

fn main() {
    let cli = Cli::parse();

    match &cli.command {
        Commands::Run { full_path, verbose } => {
            if let Some(full_path) = full_path {
                let re = Regex::new(r"(/nix/store/[^/]+)/.+").unwrap();
                let store_path = re.captures(full_path)
                    .map(|caps| caps.get(1).unwrap().as_str())
                    .unwrap_or(full_path);

                let param = if full_path == store_path {
                    format!("nix_toplevel:{}", store_path)
                } else {
                    format!("nix_binary:{}", full_path)
                };

                invoke_function(Some(&param), *verbose);
            } else {
                invoke_function(None, *verbose);
            }
        }
    }
}

#[derive(Parser)]
#[command(
    version = "0.1.0",
    author = "Võ Minh Thu <thu@hypered.io>",
    about = "Ephemeral virtual machines in the cloud in one command"
)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Run a toplevel or a binary in a cloud virtual machine
    Run {
        /// The full path to a binary or toplevel store path
        full_path: Option<String>,

        /// Enable verbose output
        #[arg(short, long)]
        verbose: bool,
    },
}

fn invoke_function(param: Option<&str>, verbose: bool) {
    let mut command = ProcessCommand::new("doctl");
    command.args(&["serverless", "functions", "invoke", "thebacknd/create"]);

    if let Some(param) = param {
        command.args(&["--param", param]);
    }

    if verbose {
        println!("Executing: {:?}", command);
    }

    let status = command
        .status()
        .expect("Failed to execute doctl command");

    if !status.success() {
        exit(status.code().unwrap_or(1));
    }
}
